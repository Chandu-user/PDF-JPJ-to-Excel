import streamlit as st
import pandas as pd
import io
from PIL import Image
import easyocr  # <--- NEW AI library to read images!
import numpy as np

st.set_page_config(page_title="File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    
    # 1. Open the image file
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Preview", use_container_width=True)
    
    st.info("🤖 AI is reading the image data now...")
    
    # 2. Fire up the EasyOCR Reader engine (tells it to read English)
    reader = easyocr.Reader(['en'])
    
    # Convert image to format EasyOCR understands
    image_np = np.array(image)
    
    # 3. Extract the text!
    # This reads the image and returns a list of text rows it found
    result = reader.readtext(image_np)
    
    # Clean up the results to put into our Excel preview sheet
    extracted_lines = []
    for detection in result:
        text_found = detection[1] # This is the actual text string
        extracted_lines.append(text_found)
    
    # 4. Turn the real text rows into our Excel Data Grid
    df_result = pd.DataFrame({
        "Line Number": range(1, len(extracted_lines) + 1),
        "Extracted Text Data": extracted_lines
    })
    
    # 5. Preview and Download
    st.subheader("📊 Extracted Data Preview")
    st.dataframe(df_result)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name='OCR Data')
    
    st.download_button(
        label="📥 Download as Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name="converted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
