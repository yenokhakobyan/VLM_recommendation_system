import os
import pandas as pd
from PIL import Image

def load_catalog(image_dir: str, metadata_csv: str):
    df = pd.read_csv(metadata_csv)
    items = []
    for _, row in df.iterrows():
        image_path = os.path.join(image_dir, row['local_path'])
        try:
            img = Image.open(image_path).convert("RGB")
            items.append({
                "id": row['file_name'],
                "image": img,
                "text": row.get("category", ""),
                "meta": row.to_dict()
            })
        except Exception as e:
            print(f"Could not open {image_path}: {e}")
    return items