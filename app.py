import streamlit as st
import pandas as pd
import io
from PIL import Image
import easyocr
import numpy as np
from pdf2image import convert_from_bytes # <--- NEW: Converts PDFs to images

st.set_page_config(page_title="File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

# Updated file uploader to accept both formats!
uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    # We will collect all images to process in this list
    images_to_process = []
    
    # 1. Handle File Types
    if file_extension == "pdf":
        st.info("Converting PDF pages to images...")
        # Convert PDF bytes into a list of PIL Images
        pdf_images = convert_from_bytes(uploaded_file.read())
        images_to_process.extend(pdf_images)
        st.write(f"Found {len(pdf_images)} page(s) in PDF.")
        # Preview the first page
        st.image(pdf_images[0], caption="PDF Page 1 Preview", use_container_width=True)
    else:
        # It's a normal image file
        image = Image.open(uploaded_file)
        images_to_process.append(image)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)
        
    # 2. Run the AI Reader Engine
    st.info("🤖 AI is reading the file data now... (This can take a moment)")
    reader = easyocr.Reader(['en'])
    extracted_lines = []
    
    # Loop through all pages/images collected
    for idx, img in enumerate(images_to_process):
        image_np = np.array(img)
        result = reader.readtext(image_np)
        
        for detection in result:
            text_found = detection[1]
            # If it's a PDF, we track which page the text came from
            if file_extension == "pdf":
                extracted_lines.append(f"[Page {idx+1}] {text_found}")
            else:
                extracted_lines.append(text_found)
                
    # 3. Create the Data Frame Grid
    df_result = pd.DataFrame({
        "Line Number": range(1, len(extracted_lines) + 1),
        "Extracted Text Data": extracted_lines
    })
    
    # 4. Preview and Download
    st.subheader("📊 Extracted Data Preview")
    st.dataframe(df_result)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name='Extracted Data')
    
    st.download_button(
        label="📥 Download as Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name="converted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
