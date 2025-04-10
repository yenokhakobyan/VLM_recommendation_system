import streamlit as st
from PIL import Image
import requests
import io

st.set_page_config(page_title="SAS Product Recommender", layout="centered")
st.title("🧠 Visual + Textual Product Recommender")

st.markdown("Upload a product image and (optionally) describe what you're looking for.")

uploaded_file = st.file_uploader("Upload a product image", type=["png", "jpg", "jpeg", "webp"])
prompt = st.text_input("Optional: Describe what you're looking for")

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Find Similar Products"):
        with st.spinner("Thinking... Finding recommendations..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"prompt": prompt}
            try:
                response = requests.post("http://localhost:8000/recommend", files=files, data=data)
                results = response.json()
                st.success("Here are your results!")
                st.markdown(f"**AI Caption:** _{results['caption']}_")
                for item in results["results"]:
                    image_path = f"data/raw/sas_images/{item['local_path']}"
                    st.image(image_path, caption=item['file_name'], width=200)
            except Exception as e:
                st.error(f"Failed to get recommendations: {e}")