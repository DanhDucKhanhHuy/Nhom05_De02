"""CNN tự thiết kế với đầu ra theo thứ tự lớp chuẩn của dự án."""

from src.model.predict import CLASS_NAMES, IMAGE_SIZE


def build_custom_cnn():
    """Tạo CNN gồm ba khối tích chập, dropout và softmax bốn lớp."""
    try:
        from tensorflow import keras
    except ImportError as exc:
        raise RuntimeError("Cần cài TensorFlow theo requirements.txt để xây CNN.") from exc

    inputs = keras.Input(shape=(*IMAGE_SIZE, 3), name="anh_rgb")
    x = keras.layers.Rescaling(1.0 / 255)(inputs)
    for filters in (32, 64, 128):
        x = keras.layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Activation("relu")(x)
        x = keras.layers.MaxPooling2D()(x)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(0.35)(x)
    outputs = keras.layers.Dense(len(CLASS_NAMES), activation="softmax", name="xac_suat")(x)
    model = keras.Model(inputs, outputs, name="bac_si_lua_custom_cnn")
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model
