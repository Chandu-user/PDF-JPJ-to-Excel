import streamlit as st
import pandas as pd
import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import pdfplumber

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
            st.write(f"Found {len(pdf.pages)} page(s) in PDF.")
            
            for idx, page in enumerate(pdf.pages):
                # Attempt to extract natural grid tables
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables.append(df)
        
        if all_tables:
            st.subheader("📊 Extracted Table Preview")
            # Combine all found tables into one sheet
            df_final = pd.concat(all_tables, ignore_index=True)
            st.dataframe(df_final)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, header=False)
        else:
            st.warning("Could not find a digital table grid. Your PDF might be a scanned image snapshot.")

    # --- METHOD 2: IMAGE TABLE ALIGNMENT ---
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)
        st.info("🤖 Reconstructing columns from your image text lines...")
        
        # Pull positional data block arrays from the image
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Group words together that share the same horizontal tier (row)
        lines = {}
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 40:  # Skip sketchy or blank read elements
                text = data['text'][i].strip()
                if text:
                    top = data['top'][i]
                    # Give a tiny 10-pixel vertical buffer to catch words slightly tilted
                    matched_row = min(lines.keys(), key=lambda x: abs(x - top), default=None)
                    
                    if matched_row is not None and abs(matched_row - top) < 10:
                        lines[matched_row].append((data['left'][i], text))
                    else:
                        lines[top] = [(data['left'][i], text)]
                        
        # Sort rows from top to bottom, and words from left to right
        sorted_rows = []
        for top in sorted(lines.keys()):
            sorted_words = sorted(lines[top], key=lambda x: x[0])
            row_string = "   ".join([w[1] for w in sorted_words])
            sorted_rows.append(row_string)
            
        df_final = pd.DataFrame({"Table Rows (Aligned)": sorted_rows})
        st.subheader("📊 Extracted Data Preview")
        st.dataframe(df_final)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False)

    # --- COMMON DOWNLOAD CONTROL ---
    if 'df_final' in locals():
        st.download_button(
            label="📥 Download as Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="converted_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
