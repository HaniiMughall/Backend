import os
from PIL import Image
import numpy as np

def ensure_upload_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def preprocess_image_for_model(image_path, target_size=(224, 224)):
    """
    Simple preprocessing: read via PIL, resize, convert to float32 and normalize 0-1,
    return batch array shaped (1, H, W, 3).
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr
