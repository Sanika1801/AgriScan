import tensorflow as tf
from tensorflow.keras import layers, models

# Create a tiny fake model
model = models.Sequential([
    layers.Conv2D(8, (3,3), activation='relu', input_shape=(224, 224, 3)),
    layers.GlobalAveragePooling2D(),
    layers.Dense(5, activation='softmax')
])
model.save("crop_disease_model.h5")

# Create dummy class names
with open("class_names.txt", "w") as f:
    f.write("Tomato___Late_blight\nPotato___Early_blight\nApple___Apple_scab\nCorn___Common_rust\nHealthy\n")
print("✅ Dummy model created!")