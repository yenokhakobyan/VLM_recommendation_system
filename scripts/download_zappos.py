import os
import requests
import zipfile
import shutil

def download_and_extract(url, download_path, extract_to):
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    os.makedirs(extract_to, exist_ok=True)

    if not os.path.exists(download_path):
        print("Downloading UT Zappos50K dataset...")
        response = requests.get(url, stream=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")

    print("Extracting dataset...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    print("Dataset extracted to:", extract_to)

if __name__ == "__main__":
    ZAPPOS_URL = "http://vision.cs.utexas.edu/projects/finegrained/utzap50k.zip"
    ZIP_PATH = "data/raw/utzap50k.zip"
    DEST_DIR = "data/raw/images"

    download_and_extract(ZAPPOS_URL, ZIP_PATH, DEST_DIR)

    # Optionally move/rename folders if needed
    extracted_main_folder = os.path.join(DEST_DIR, "utzap50k")
    if os.path.isdir(extracted_main_folder):
        for sub in os.listdir(extracted_main_folder):
            shutil.move(os.path.join(extracted_main_folder, sub), DEST_DIR)
        shutil.rmtree(extracted_main_folder)
        print("Reorganized extracted folders.")
