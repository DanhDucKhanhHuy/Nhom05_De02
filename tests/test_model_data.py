"""Kiểm thử chia dữ liệu mà không cần TensorFlow."""
import hashlib
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pytest
from PIL import Image

from src.model.predict import CLASS_NAMES
from src.model.prepare_data import extract_mendeley_subset, prepare_data
from src.model.training import evaluate_model, evaluate_real_images, save_metrics


def _make_dataset(root, duplicate=False):
    for label in CLASS_NAMES:
        (root / label).mkdir(parents=True)
        for index in range(4):
            Image.new("RGB", (12, 12), color=(index * 40, CLASS_NAMES.index(label) * 40, 40)).save(
                root / label / f"{index}.png"
            )
    if duplicate:
        (root / "dao_on" / "copy.png").write_bytes((root / "dao_on" / "0.png").read_bytes())


def test_prepare_data_makes_reproducible_partitions_and_keeps_duplicates_together(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "split"
    _make_dataset(source, duplicate=True)

    counts = prepare_data(source, output, seed=12)

    assert counts == {"train": 8, "validation": 4, "test": 4}
    locations = {}
    for split in ("train", "validation", "test"):
        for path in (output / split).rglob("*.png"):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            locations.setdefault(digest, set()).add(split)
    assert all(len(splits) == 1 for splits in locations.values())


def test_prepare_data_rejects_existing_nonempty_output(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "split"
    _make_dataset(source)
    output.mkdir()
    (output / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError):
        prepare_data(source, output)
    assert (output / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_prepare_data_excludes_external_holdout_by_sha256(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "split"
    _make_dataset(source)
    heldout = source / "dao_on" / "0.png"

    counts = prepare_data(source, output, exclude_paths=[heldout])

    assert counts["train"] + counts["validation"] + counts["test"] == 15
    heldout_digest = hashlib.sha256(heldout.read_bytes()).hexdigest()
    split_digests = {
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in output.rglob("*.png")
    }
    assert heldout_digest not in split_digests


def test_evaluate_model_returns_real_multiclass_metrics():
    class Model:
        def predict(self, images, verbose=0):
            return np.array([[0.8, 0.1, 0.05, 0.05], [0.1, 0.7, 0.1, 0.1]])

    metrics = evaluate_model(
        Model(), [(np.zeros((2, 1)), np.array([0, 1]))]
    )

    assert metrics["accuracy"] == 1.0
    assert metrics["precision_macro"] == 0.5
    assert metrics["recall_macro"] == 0.5
    assert metrics["f1_macro"] == pytest.approx(0.5)
    assert metrics["per_class"]["dao_on"] == {
        "precision": 1.0, "recall": 1.0, "f1": 1.0, "support": 1
    }
    assert metrics["per_class"]["bac_la"] == {
        "precision": 1.0, "recall": 1.0, "f1": 1.0, "support": 1
    }
    assert metrics["per_class"]["dom_nau"]["support"] == 0
    assert metrics["confusion_matrix"] == [
        [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
    ]


def test_evaluate_model_rejects_empty_test_set():
    class Model:
        pass

    with pytest.raises(ValueError, match="Tập test rỗng"):
        evaluate_model(Model(), [])


def test_evaluate_model_rejects_non_softmax_outputs():
    class Model:
        def predict(self, images, verbose=0):
            return np.array([[2.0, 0.0, 0.0, 0.0]])

    with pytest.raises(ValueError, match="softmax"):
        evaluate_model(Model(), [(np.zeros((1, 1)), np.array([0]))])


def test_save_metrics_writes_utf8_json(tmp_path):
    destination = tmp_path / "reports" / "metrics.json"
    save_metrics({"nhan": "đạo ôn", "accuracy": 0.75}, destination)

    assert '"nhan": "đạo ôn"' in destination.read_text(encoding="utf-8")


def test_extract_mendeley_subset_maps_four_source_folders(tmp_path):
    archive = tmp_path / "source.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
        for folder in ("Leaf Blast", "Bacterial Leaf Blight", "Brown Spot", "Healthy"):
            zipped.writestr(f"dataset/{folder}/leaf.jpg", b"image")

    counts = extract_mendeley_subset(archive, tmp_path / "extracted")

    assert counts == {"dao_on": 1, "bac_la": 1, "dom_nau": 1, "la_khoe": 1}
    assert (tmp_path / "extracted" / "dao_on" / "leaf.jpg").read_bytes() == b"image"


def test_extract_mendeley_subset_rejects_nonempty_output_without_deleting_it(tmp_path):
    archive = tmp_path / "source.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
        zipped.writestr("Leaf Blast/leaf.jpg", b"image")
    output = tmp_path / "extracted"
    output.mkdir()
    (output / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError):
        extract_mendeley_subset(archive, output)
    assert (output / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_evaluate_real_images_writes_predictions_without_claiming_accuracy(tmp_path, monkeypatch):
    from src.model import predict

    image_root = tmp_path / "real"
    class_dir = image_root / "dao_on"
    class_dir.mkdir(parents=True)
    for index in range(20):
        (class_dir / f"{index}.jpg").write_bytes(b"image")
    monkeypatch.setattr(
        predict, "predict_top3", lambda path: [("dao_on", .7), ("bac_la", .2), ("dom_nau", .1)]
    )
    report = tmp_path / "reports" / "real.csv"

    assert evaluate_real_images(image_root, report) == 20
    contents = report.read_text(encoding="utf-8-sig")
    assert "nhan_thu_muc_chua_xac_minh" in contents
    assert "khop_nhan_thu_muc_chua_xac_minh" in contents
    assert "accuracy" not in contents


def test_evaluate_real_images_requires_minimum_count(tmp_path):
    with pytest.raises(ValueError, match="ít nhất 20"):
        evaluate_real_images(tmp_path, tmp_path / "report.csv")
