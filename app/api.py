from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
from app.model import VLMEncoder
from app.index import FaissIndex
import app.data as data_loader
from transformers import pipeline


app = FastAPI()
encoder = VLMEncoder()

catalog = data_loader.load_catalog("data/raw/sas_images", "data/raw/sas_images/sas_metadata.csv")
index = FaissIndex(dim=512)
id_to_meta = {}

# Combine caption (if exists) with the image for embedding
for item in catalog:
    text = item.get('caption', item['text'])
    vec = encoder.encode_dual(item['image'], text)
    index.add(vec, item['id'])
    id_to_meta[item['id']] = item['meta']

index.build()

@app.post("/recommend")
async def recommend(file: UploadFile, prompt: str = Form("")):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")

    # Generate image-based description
    image_caption = encoder.think(image)
    if prompt.strip():
        combined_description = encoder.transform_prompt(image_caption, prompt)
    else:
        combined_description = image_caption


    # Embed based on combined image and description
    query_vec = encoder.encode_dual(image, combined_description)
    result_ids = index.search(query_vec)

    return JSONResponse(content={
        "caption": combined_description,
        "results": [id_to_meta[i] for i in result_ids]
    })
