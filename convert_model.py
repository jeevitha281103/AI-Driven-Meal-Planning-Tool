"""
Run this script LOCALLY to convert the H5 model to TFLite format.
The TFLite model is ~45MB and doesn't need Git LFS.

Usage: python convert_model.py
"""
import tensorflow as tf
import os

MODEL_PATH = "Model/model_v1_inceptionV3.h5"
TFLITE_PATH = "Model/model_v1_inceptionV3.tflite"

print("Loading H5 model...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
model.summary()

print("\nConverting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

os.makedirs("Model", exist_ok=True)
with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

size_mb = os.path.getsize(TFLITE_PATH) / 1024 / 1024
print(f"\nSaved: {TFLITE_PATH} ({size_mb:.1f} MB)")
print(f"H5 was: {os.path.getsize(MODEL_PATH) / 1024 / 1024:.1f} MB")
print(f"\nNext steps:")
print(f"1. git add Model/model_v1_inceptionV3.tflite")
print(f"2. git commit -m 'add: TFLite model for Render deployment'")
print(f"3. git push")
