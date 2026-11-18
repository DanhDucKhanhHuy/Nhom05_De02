"""Huấn luyện, lưu mô hình và tính chỉ số trên tập test độc lập."""
import csv
import json
from pathlib import Path

import numpy as np

from src.model import predict as predictor
from src.model.predict import CLASS_NAMES


def train_model(model, datasets: dict[str, object], output_path: str | Path, epochs: int = 20):
    """Huấn luyện trên train, chọn checkpoint theo validation loss, xuất .keras."""
    try:
        from tensorflow import keras
    except ImportError as exc:
        raise RuntimeError("Cần cài TensorFlow theo requirements.txt để huấn luyện.") from exc
    if epochs < 1:
        raise ValueError("epochs phải là số nguyên dương.")
    required = {"train", "validation"}
    if not required.issubset(datasets):
        raise ValueError("datasets cần có train và validation.")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(
            destination, monitor="val_loss", save_best_only=True, save_weights_only=False
        ),
    ]
    history = model.fit(
        datasets["train"], validation_data=datasets["validation"], epochs=epochs,
        callbacks=callbacks,
    )
    return history


def evaluate_model(model, test_dataset) -> dict[str, object]:
    """Trả metrics tổng hợp và precision/recall/F1 từng lớp trên tập test."""
    from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

    expected_batches = []
    predicted_batches = []
    for images, labels in test_dataset:
        probabilities = np.asarray(model.predict(images, verbose=0), dtype=float)
        labels_array = np.asarray(labels).reshape(-1)
        if probabilities.shape != (len(labels_array), len(CLASS_NAMES)):
            raise ValueError("Đầu ra mô hình không khớp số mẫu và bốn lớp chuẩn.")
        if (
            not np.isfinite(probabilities).all()
            or (probabilities < 0).any()
            or (probabilities > 1).any()
            or not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-5)
        ):
            raise ValueError("Đầu ra mô hình phải là các vector xác suất softmax hợp lệ.")
        if ((labels_array < 0) | (labels_array >= len(CLASS_NAMES))).any():
            raise ValueError("Nhãn test nằm ngoài thứ tự bốn lớp chuẩn.")
        expected_batches.extend(labels_array.astype(int).tolist())
        predicted_batches.extend(probabilities.argmax(axis=1).tolist())
    if not expected_batches:
        raise ValueError("Tập test rỗng; không thể tính chỉ số.")
    per_precision, per_recall, per_f1, support = precision_recall_fscore_support(
        expected_batches, predicted_batches, labels=range(len(CLASS_NAMES)),
        average=None, zero_division=0,
    )
    precision, recall, f1, _ = precision_recall_fscore_support(
        expected_batches, predicted_batches, labels=range(len(CLASS_NAMES)),
        average="macro", zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(expected_batches, predicted_batches)),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(f1),
        "per_class": {
            name: {
                "precision": float(per_precision[index]),
                "recall": float(per_recall[index]),
                "f1": float(per_f1[index]),
                "support": int(support[index]),
            }
            for index, name in enumerate(CLASS_NAMES)
        },
        "confusion_matrix": confusion_matrix(
            expected_batches, predicted_batches, labels=range(len(CLASS_NAMES))
        ).tolist(),
        "class_names": list(CLASS_NAMES),
        "test_samples": len(expected_batches),
    }


def save_metrics(metrics: dict[str, object], output_path: str | Path) -> None:
    """Ghi kết quả đánh giá JSON UTF-8 để gắn với hồ sơ của lần chạy."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def evaluate_real_images(
    image_root: str | Path,
    output_path: str | Path,
    minimum_images: int = 20,
) -> int:
    """Ghi top-3 từng ảnh; nhãn thư mục chỉ là tham khảo, không tính accuracy."""
    root = Path(image_root)
    image_paths = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    if len(image_paths) < minimum_images:
        raise ValueError(f"Cần ít nhất {minimum_images} ảnh; hiện có {len(image_paths)}.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "tep_anh", "nhan_thu_muc_chua_xac_minh", "du_doan_1", "xac_suat_1",
        "top3_json", "so_sanh_tham_khao",
    ]
    with destination.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        for image_path in image_paths:
            top3 = predictor.predict_top3(image_path)
            folder_label = image_path.parent.name
            known_folder_label = folder_label if folder_label in CLASS_NAMES else ""
            comparison = "khong_co_nhan" if not known_folder_label else (
                "khop_nhan_thu_muc_chua_xac_minh"
                if top3[0][0] == known_folder_label
                else "khong_khop_nhan_thu_muc_chua_xac_minh"
            )
            writer.writerow(
                {
                    "tep_anh": image_path.relative_to(root).as_posix(),
                    "nhan_thu_muc_chua_xac_minh": known_folder_label,
                    "du_doan_1": top3[0][0],
                    "xac_suat_1": top3[0][1],
                    "top3_json": json.dumps(top3, ensure_ascii=False),
                    "so_sanh_tham_khao": comparison,
                }
            )
    return len(image_paths)
