"""Transfer learning với MobileNetV2 hoặc EfficientNetB0."""

from src.model.predict import CLASS_NAMES, IMAGE_SIZE


def build_transfer(base: str = "mobilenetv2"):
    """Tạo classifier transfer learning; backbone đóng băng để huấn luyện đầu."""
    try:
        from tensorflow import keras
    except ImportError as exc:
        raise RuntimeError("Cần cài TensorFlow theo requirements.txt để dùng transfer learning.") from exc

    normalized = base.lower()
    backbones = {
        "mobilenetv2": keras.applications.MobileNetV2,
        "efficientnetb0": keras.applications.EfficientNetB0,
    }
    if normalized not in backbones:
        raise ValueError("base chỉ nhận 'mobilenetv2' hoặc 'efficientnetb0'.")

    backbone_factory = backbones[normalized]
    inputs = keras.Input(shape=(*IMAGE_SIZE, 3), name="anh_rgb")
    x = inputs
    if normalized == "mobilenetv2":
        x = keras.layers.Rescaling(1.0 / 127.5, offset=-1, name="tien_xu_ly_mobilenet")(x)
    backbone = backbone_factory(include_top=False, weights="imagenet", input_shape=(*IMAGE_SIZE, 3))
    backbone.trainable = False
    x = backbone(x, training=False)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(0.3)(x)
    outputs = keras.layers.Dense(len(CLASS_NAMES), activation="softmax", name="xac_suat")(x)
    model = keras.Model(inputs, outputs, name=f"bac_si_lua_{normalized}")
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model
