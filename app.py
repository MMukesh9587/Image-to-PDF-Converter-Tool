import os
from PIL import Image
from fpdf import FPDF
import streamlit as st
from streamlit_sortables import sort_items

# Initialize session state for uploaded images
if "images" not in st.session_state:
    st.session_state.images = []
    st.session_state.image_names = []

# Function to create PDF
def create_pdf():
    pdf = FPDF()
    for img in st.session_state.images:
        # Ensure image fits within the page
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

# Display uploaded images with options
if st.session_state.images:
    st.subheader("Uploaded Images:")
    
    # Drag-and-drop reordering
    reordered_names = sort_items(st.session_state.image_names, direction="horizontal")
    reordered_images = [st.session_state.images[st.session_state.image_names.index(name)] for name in reordered_names]
    st.session_state.image_names = reordered_names
    st.session_state.images = reordered_images
    
    # Preview images with options
    for idx, (img, name) in enumerate(zip(st.session_state.images, st.session_state.image_names)):
        st.write(f"**{idx + 1}. {name}**")
        
        # Display image
        st.image(img, width=150)
        
        # Rotation and delete options
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Rotate Left {name}", key=f"rotate_left_{idx}"):
                st.session_state.images[idx] = img.rotate(90, expand=True)
        with col2:
            if st.button(f"Rotate Right {name}", key=f"rotate_right_{idx}"):
                st.session_state.images[idx] = img.rotate(-90, expand=True)
        with col3:
            if st.button(f"Delete {name}", key=f"delete_{idx}"):
                del st.session_state.images[idx]
                del st.session_state.image_names[idx]
                st.experimental_rerun()

    # Create PDF
    if st.button("Create PDF"):
        pdf_path = create_pdf()
        with open(pdf_path, "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, file_name="output.pdf")
                
