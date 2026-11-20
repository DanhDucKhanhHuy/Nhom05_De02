"""Huấn luyện, đánh giá và đóng gói hai mô hình CN3 trên cùng một phép chia."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from src.model.custom_cnn import build_custom_cnn
from src.model.data_pipeline import build_pipeline
from src.model.predict import CLASS_NAMES, MODEL_PATH, predict_top3
from src.model.prepare_data import extract_mendeley_subset, prepare_data
from src.model.training import evaluate_model, evaluate_real_images, save_metrics, train_model
from src.model.transfer import build_transfer

DATASET_DOI = "10.17632/n8jpkpfz5p.1"
CLASS_COUNTS = {"dao_on": 521, "bac_la": 785, "dom_nau": 761, "la_khoe": 753}


def _sha256(path: Path) -> str:
    """Tính checksum theo luồng để không nạp artifact vào bộ nhớ."""
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_split_counts(root: Path, excluded_hashes: set[str]) -> dict[str, object]:
    """Đọc số tệp ảnh theo từng phân vùng và lớp, đồng thời kiểm tra đủ lớp."""
    result = {}
    for split in ("train", "validation", "test"):
        class_counts = {}
        for label in CLASS_NAMES:
            class_dir = root / split / label
            if not class_dir.is_dir():
                raise ValueError(f"Thiếu thư mục phân vùng/lớp: {class_dir}")
            image_paths = [
                path for path in class_dir.iterdir()
                if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
            ]
            overlaps = [
                path.name for path in image_paths
                if hashlib.sha256(path.read_bytes()).hexdigest() in excluded_hashes
            ]
            if overlaps:
                raise ValueError(
                    f"Phân vùng {split} trùng ảnh kiểm tra thực tế; hãy tạo split ở thư mục mới."
                )
            class_counts[label] = len(image_paths)
            if class_counts[label] == 0:
                raise ValueError(f"Phân vùng {split} không có ảnh lớp {label}.")
        result[split] = {"total": sum(class_counts.values()), "per_class": class_counts}
    return result


def main() -> None:
    """Chạy toàn bộ quy trình huấn luyện CN3 và ghi hồ sơ đánh giá."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path("data/raw/mendeley_n8jpkpfz5p_v1.zip"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/mendeley_n8jpkpfz5p_v1"))
    parser.add_argument("--splits-dir", type=Path, default=Path("artifacts/data_cn3"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/cn3"))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=1314)
    args = parser.parse_args()

    if not args.raw_dir.is_dir():
        extract_mendeley_subset(args.archive, args.raw_dir)
    real_image_root = Path("data/anh_thuc_te")
    real_images = sorted(
        path for path in real_image_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    if len(real_images) < 20:
        raise ValueError(f"Cần ít nhất 20 ảnh kiểm tra; hiện có {len(real_images)}.")
    real_hashes = {hashlib.sha256(path.read_bytes()).hexdigest() for path in real_images}

    if args.splits_dir.exists():
        split_counts = _read_split_counts(args.splits_dir, real_hashes)
    else:
        prepare_data(
            args.raw_dir, args.splits_dir, seed=args.seed, exclude_paths=real_images
        )
        split_counts = _read_split_counts(args.splits_dir, real_hashes)
    datasets = build_pipeline(args.splits_dir, batch_size=args.batch_size, seed=args.seed)

    import tensorflow as tf

    candidates = (
        ("custom_cnn", build_custom_cnn),
        ("mobilenetv2", lambda: build_transfer("mobilenetv2")),
    )
    validation_scores: dict[str, tuple[float, float, Path]] = {}
    for name, factory in candidates:
        model = factory()
        artifact = args.output_dir / f"{name}.keras"
        history = train_model(model, datasets, artifact, epochs=args.epochs)
        validation_accuracy = history.history["val_accuracy"]
        validation_loss = history.history["val_loss"]
        best_index = min(
            range(len(validation_accuracy)),
            key=lambda index: (validation_loss[index], -validation_accuracy[index]),
        )
        best_validation_accuracy = float(validation_accuracy[best_index])
        best_validation_loss = float(validation_loss[best_index])
        epochs_run = len(validation_accuracy)
        del history, model
        tf.keras.backend.clear_session()
        model = tf.keras.models.load_model(artifact)
        metrics = evaluate_model(model, datasets["test"])
        metrics["ho_so"] = {
            "model": name,
            "validation_accuracy": best_validation_accuracy,
            "validation_loss": best_validation_loss,
            "epochs_run": epochs_run,
            "tensorflow": tf.__version__,
            "dataset_doi": DATASET_DOI,
            "dataset_license": "CC BY 4.0",
            "class_order": list(CLASS_NAMES),
            "source_class_counts": CLASS_COUNTS,
            "split_counts_unique_files": split_counts,
            "real_images_excluded_from_splits": len(real_images),
            "seed": args.seed,
            "batch_size": args.batch_size,
            "image_size": [224, 224],
            "artifact_sha256": _sha256(artifact),
        }
        save_metrics(metrics, args.output_dir / f"{name}_metrics.json")
        validation_scores[name] = (
            -best_validation_loss,
            best_validation_accuracy,
            artifact,
        )
        del model
        tf.keras.backend.clear_session()

    selected_name = max(validation_scores, key=lambda name: validation_scores[name][:2])
    selected_artifact = validation_scores[selected_name][2]
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected_artifact, MODEL_PATH)
    first_real_image = real_images[0]
    smoke_prediction = predict_top3(first_real_image)
    evaluated_count = evaluate_real_images(
        "data/anh_thuc_te", args.output_dir / "anh_thuc_te_top3.csv"
    )
    run_summary = {
        "selected_by": "lowest_validation_loss_then_validation_accuracy",
        "selected_model": selected_name,
        "selected_artifact": str(MODEL_PATH),
        "selected_artifact_sha256": _sha256(MODEL_PATH),
        "first_image_smoke_test": {
            "file": first_real_image.as_posix(),
            "top3": smoke_prediction,
        },
        "real_image_predictions_written": evaluated_count,
        "real_image_label_status": "folder labels are unverified; no field accuracy reported",
    }
    (args.output_dir / "run_summary.json").write_text(
        json.dumps(run_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
