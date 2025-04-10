import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from transformers import pipeline


class VLMEncoder:
    def __init__(self, text_weight=0.6):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.rewriter = pipeline("text2text-generation", model="google/flan-t5-small", device=0 if self.device == 'cuda' else -1)
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

        self.text_weight = text_weight
        self.image_weight = 1.0 - text_weight

    def normalize(self, vec):
        return vec / np.linalg.norm(vec)

    def encode_image(self, image):
        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.clip_model.get_image_features(pixel_values=inputs["pixel_values"])
        return self.normalize(outputs[0].cpu().numpy())

    def encode_text(self, text):
        text = text.strip() if text else ""
        if not text:
            return np.zeros((512,), dtype=np.float32)
        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.clip_model.get_text_features(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        return self.normalize(outputs[0].cpu().numpy())

    def encode_dual(self, image, text=""):
        image_vec = self.encode_image(image)
        text_vec = self.encode_text(text)
        return self.normalize(self.image_weight * image_vec + self.text_weight * text_vec)

    def think(self, image):
        inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.blip_model.generate(**inputs, max_length=20)
        return self.blip_processor.decode(out[0], skip_special_tokens=True)

    def encode_from_image_only(self, image):
        caption = self.think(image)
        return self.encode_dual(image, caption)
    
    def transform_prompt(self, image_caption, user_prompt):
        full_prompt = f"The image shows: {image_caption}. The user wants: {user_prompt}. Rephrase it as a clear search description."
        rewritten = self.rewriter(full_prompt, max_length=50, do_sample=False)[0]['generated_text']
        return rewritten
