import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# 1. Setup
# NOTE: You must download the PlantVillage dataset from Kaggle 
# and extract it so this folder path is correct.
DATASET_DIR = "PlantVillage" 
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

if not os.path.exists(DATASET_DIR):
    print(f"❌ ERROR: Dataset folder '{DATASET_DIR}' not found!")
    print("Please download the PlantVillage dataset from Kaggle and extract it here.")
    exit()

print("🔄 Loading images... (This might take a minute)")
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2, # 80% for training, 20% for testing
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

train_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Save the class names (disease names) to a text file for Django to use
class_names = list(train_data.class_indices.keys())
with open("class_names.txt", "w") as f:
    for item in class_names:
        f.write(f"{item}\n")

print(f"✅ Found {len(class_names)} different diseases/crops.")

# 2. Build the AI Brain (Using MobileNetV2 for high accuracy)
print("🧠 Building the AI Model...")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False # Freeze base model

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(len(class_names), activation='softmax')
])

# 3. Train the Model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("🚀 Starting training... (This will take 10-20 minutes)")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=5 # Increase to 10 or 15 for even higher accuracy
)

# 4. Save the Real Model
model.save("crop_disease_model.h5")
print("\n🎉 SUCCESS! 'crop_disease_model.h5' and 'class_names.txt' have been created.")
print("Restart your Django server to use the new AI!")