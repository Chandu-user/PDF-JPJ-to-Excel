import streamlit as st
import pandas as pd
import io
from PIL import Image
import pdfplumber

# Advanced table extraction tools
from img2table.document.image import Image as Img2TableImage
from img2table.ocr import TesseractOCR

st.set_page_config(page_title="File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    # --- METHOD 1: DIGITAL PDF TABLE EXTRACTION ---
    if file_extension == "pdf":
        st.info("Reading PDF structural layout tables...")
        all_tables = []
        
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for idx, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables.append(df)
        
        if all_tables:
            df_final = pd.concat(all_tables, ignore_index=True)
            st.subheader("📊 Extracted Table Preview")
            st.dataframe(df_final)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, header=False)
        else:
            st.warning("Could not find a digital table grid. Your PDF might be a scanned image snapshot.")

    # --- METHOD 2: DEEP LEARNING IMAGE TABLE ALIGNMENT ---
    else:
        # Show image preview
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)
        st.info("🔍 Deep learning is mapping the table grids and columns...")
        
        # Save uploaded file temporarily to bytes for the structural engine
        img_bytes = uploaded_file.getvalue()
        src_image = Img2TableImage(io.BytesIO(img_bytes))
        
        # Connect Tesseract OCR to the structural table mapper
        ocr = TesseractOCR(n_threads=1, lang="eng")
        
        # Extract tables based on visual grid lines
        extracted_tables = src_image.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=False)
        
        if extracted_tables:
            # Grab the very first table found in the image and turn it into a DataFrame
            table = extracted_tables[0]
            df_final = table.to_dataframe()
            
            st.subheader("📊 Extracted Table Preview")
            st.dataframe(df_final)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, header=False)
        else:
            st.error("❌ Could not identify structured table rows or columns. Make sure the table lines in your image are clearly visible.")

    # --- COMMON DOWNLOAD CONTROL ---
    if 'df_final' in locals() and not df_final.empty:
        st.download_button(
            label="📥 Download as Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="converted_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
