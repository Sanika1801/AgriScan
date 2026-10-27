import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

DATASET_DIR = "PlantVillage"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

if not os.path.exists(DATASET_DIR):
    print("❌ ERROR: Folder 'PlantVillage' not found! Rename your 'color' folder to 'PlantVillage'.")
    exit()

print("🔄 Loading a small subset of images to train FAST...")

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.1
)

# We limit the number of steps so it finishes in ~2-3 minutes
train_data = datagen.flow_from_directory(
    DATASET_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', subset='training'
)

val_data = datagen.flow_from_directory(
    DATASET_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode='categorical', subset='validation'
)

class_names = list(train_data.class_indices.keys())
with open("class_names.txt", "w") as f:
    for item in class_names:
        f.write(f"{item}\n")

print(f"🧠 Building Model with {len(class_names)} classes...")
base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("🚀 Training (This will take 2-3 minutes)...")
# Train on only 50 steps to save time
model.fit(train_data, validation_data=val_data, epochs=1, steps_per_epoch=100)

model.save("crop_disease_model.h5")
print("\n🎉 SUCCESS! The REAL model is saved. Restart your Django server now!")