import streamlit as st
from extract_text import extract_tables_from_image
from PIL import Image
import json
import os
import tempfile

st.set_page_config(page_title="Table Extraction Agent", layout="wide")
st.title("📊 Table Extraction Agent")

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded.read())
        img_path = tmp.name

    image = Image.open(img_path)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    extracted_json = extract_tables_from_image(img_path)

    st.subheader("Extracted JSON")
    st.json(extracted_json)

    os.remove(img_path)
