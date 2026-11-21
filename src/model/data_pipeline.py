"""Tạo pipeline TensorFlow; chỉ tăng cường ảnh trong tập train."""
from pathlib import Path

from src.model.predict import CLASS_NAMES, IMAGE_SIZE


def build_pipeline(thu_muc: str | Path, batch_size: int = 32, seed: int = 1314) -> dict[str, object]:
    """Nạp ba phân vùng cùng thứ tự lớp và augmentation chỉ cho train."""
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Cần cài TensorFlow theo requirements.txt để nạp dữ liệu.") from exc
    root = Path(thu_muc)
    datasets = {}
    for split in ("train", "validation", "test"):
        datasets[split] = tf.keras.utils.image_dataset_from_directory(
            root / split,
            labels="inferred",
            label_mode="int",
            class_names=list(CLASS_NAMES),
            image_size=IMAGE_SIZE,
            batch_size=batch_size,
            shuffle=split == "train",
            seed=seed,
        )
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal_and_vertical"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomBrightness(0.15, value_range=(0, 255)),
        ],
        name="tang_cuong_anh",
    )
    datasets["train"] = datasets["train"].map(
        lambda images, labels: (augmentation(images, training=True), labels),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    return {name: dataset.prefetch(tf.data.AUTOTUNE) for name, dataset in datasets.items()}
