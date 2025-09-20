# utils.py
import os
from PIL import Image
import numpy as np

def ensure_upload_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def preprocess_image_for_model(path, target_size=(224,224)):
    """
    Open image from path, resize, normalize.
    Return numpy array shaped (1, H, W, C)
    Adjust normalization according to your TF model.
    """
    img = Image.open(path).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr
