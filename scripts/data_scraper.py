import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.sas.am"
CATALOG_URL = f"{BASE_URL}/en/catalog/"
SAVE_DIR = "data/raw/sas_images"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
DELAY = 2
MAX_IMAGES_PER_CATEGORY = 50

METADATA_FILE = os.path.join(SAVE_DIR, "sas_metadata.csv")
os.makedirs(SAVE_DIR, exist_ok=True)

def get_all_categories():
    response = requests.get(CATALOG_URL, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch main catalog page")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a[href^="/en/catalog/"]')
    categories = set()
    for link in links:
        href = link.get('href')
        if href and "/catalog/" in href:
            slug = href.replace("/en/catalog/", "").strip('/')
            if slug:
                categories.add(slug)
    return list(categories)

def download_image(img_url, category, metadata_writer):
    try:
        if not img_url.endswith(".webp") or "/upload/Sh/imageCache/" not in img_url:
            return

        if img_url.startswith("/upload/"):
            img_url = urljoin(BASE_URL, img_url)

        response = requests.get(img_url, headers=HEADERS)
        if response.status_code == 200:
            os.makedirs(os.path.join(SAVE_DIR, category), exist_ok=True)
            file_name = os.path.basename(img_url.split("?")[0])
            save_path = os.path.join(SAVE_DIR, category, file_name)

            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded: {file_name}")
            metadata_writer.writerow({
                "file_name": file_name,
                "category": category,
                "url": img_url,
                "local_path": os.path.relpath(save_path, start=SAVE_DIR)
            })
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

def scrape_category(category, metadata_writer):
    print(f"Scraping category: {category}")
    url = urljoin(CATALOG_URL, category)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to access {url} with status {response.status_code}")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    count = 0
    for tag in img_tags:
        if count >= MAX_IMAGES_PER_CATEGORY:
            break
        src = tag.get('data-src') or tag.get('src')
        if src and src.endswith(".webp") and "/upload/Sh/imageCache/" in src:
            img_url = urljoin(BASE_URL, src)
            download_image(img_url, category, metadata_writer)
            count += 1
    time.sleep(DELAY)

if __name__ == "__main__":
    all_categories = get_all_categories()
    print(f"Found categories: {all_categories}")
    with open(METADATA_FILE, mode='w', newline='') as csvfile:
        fieldnames = ["file_name", "category", "url", "local_path"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cat in all_categories:
            scrape_category(cat, writer)
            time.sleep(DELAY * 4)