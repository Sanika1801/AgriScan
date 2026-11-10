import tensorflow as tf

# Path to your existing model
MODEL_PATH = "crop_disease_model.h5"

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# Convert to TFLite (Quantized for mobile)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open("crop_disease_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✅ TFLite model saved as crop_disease_model.tflite (Size: ~4MB)")