import os
from PIL import Image, ImageOps
from fpdf import FPDF
import streamlit as st
from streamlit_sortables import sort_items
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Initialize session state for uploaded images
if "images" not in st.session_state:
    st.session_state.images = []
    st.session_state.image_names = []

# Function to create PDF
def create_pdf(page_size="A4", password=None, watermark_text=None):
    pdf = FPDF(orientation="P", unit="mm", format=page_size)
    for idx, img in enumerate(st.session_state.images):
        temp_file = f"temp_image_{idx}.jpg"
        img.save(temp_file)

        # Add watermark (if any)
        if watermark_text:
            watermark_image = ImageOps.expand(img, border=50, fill="white")
            watermark_draw = ImageDraw.Draw(watermark_image)
            watermark_draw.text((10, 10), watermark_text, fill="gray")
            watermark_image.save(temp_file)

        pdf.add_page()
        pdf.image(temp_file, x=10, y=10, w=190)
        os.remove(temp_file)

    if password:
        pdf.set_protection(["print"], user_pwd=password)

    output_file = "output.pdf"
    pdf.output(output_file)
    return output_file

# Streamlit UI
st.title("Smart PDF Designer")
st.sidebar.header("PDF Settings")
page_size = st.sidebar.selectbox("Page Size", ["A4", "Letter", "Legal"])
password = st.sidebar.text_input("Password (optional)", type="password")
watermark_text = st.sidebar.text_input("Watermark (optional)")

uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.image_names:
            img = Image.open(uploaded_file).convert("RGB")
            st.session_state.images.append(img)
            st.session_state.image_names.append(uploaded_file.name)

# Display uploaded images
if st.session_state.images:
    st.subheader("Manage Your Images")
    reordered_names = sort_items(st.session_state.image_names, direction="horizontal")
    reordered_images = [st.session_state.images[st.session_state.image_names.index(name)] for name in reordered_names]
    st.session_state.image_names = reordered_names
    st.session_state.images = reordered_images

    for idx, (img, name) in enumerate(zip(st.session_state.images, st.session_state.image_names)):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.image(img, caption=name, use_column_width=True)
        with col2:
            if st.button(f"Rotate {name}", key=f"rotate_{idx}"):
                st.session_state.images[idx] = img.rotate(90, expand=True)
        with col3:
            if st.button(f"Delete {name}", key=f"delete_{idx}"):
                del st.session_state.images[idx]
                del st.session_state.image_names[idx]
                st.experimental_rerun()

    if st.button("Create PDF"):
        pdf_path = create_pdf(page_size, password, watermark_text)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, file_name="output.pdf")
                
