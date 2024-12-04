import os
from PIL import Image
from fpdf import FPDF
import streamlit as st

# Initialize session state for uploaded images
if "images" not in st.session_state:
    st.session_state.images = []
    st.session_state.image_names = []

# Function to reorder images
def reorder_images(from_idx, to_idx):
    images = st.session_state.images
    names = st.session_state.image_names
    image = images.pop(from_idx)
    name = names.pop(from_idx)
    images.insert(to_idx, image)
    names.insert(to_idx, name)

# Function to create PDF
def create_pdf():
    pdf = FPDF()
    for img in st.session_state.images:
        temp_file = "temp_image.jpg"
        img.save(temp_file)
        pdf.add_page()
        pdf.image(temp_file, x=10, y=10, w=190)
        os.remove(temp_file)
    output_file = "output.pdf"
    pdf.output(output_file)
    return output_file

# Streamlit UI
st.title("Image to PDF Converter")

# Upload images
uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        st.session_state.images.append(img)
        st.session_state.image_names.append(uploaded_file.name)

# Display uploaded images
if st.session_state.images:
    st.subheader("Uploaded Images:")
    for idx, name in enumerate(st.session_state.image_names):
        st.write(f"{idx + 1}. {name}")
    
    # Reorder images
    st.subheader("Reorder Images:")
    from_idx = st.number_input("Move from position", min_value=1, max_value=len(st.session_state.images), step=1) - 1
    to_idx = st.number_input("Move to position", min_value=1, max_value=len(st.session_state.images), step=1) - 1
    if st.button("Reorder"):
        reorder_images(from_idx, to_idx)
        st.success("Image order updated!")

    # Delete images
    st.subheader("Delete Image:")
    delete_idx = st.number_input("Enter position to delete", min_value=1, max_value=len(st.session_state.images), step=1) - 1
    if st.button("Delete"):
        del st.session_state.images[delete_idx]
        del st.session_state.image_names[delete_idx]
        st.success("Image deleted!")

    # Create PDF
    if st.button("Create PDF"):
        pdf_path = create_pdf()
        with open(pdf_path, "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, file_name="output.pdf")
