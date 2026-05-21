import streamlit as st
import pandas as pd
import io
import fitz  # PyMuPDF

st.set_page_config(page_title="File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

uploaded_file = st.file_uploader("Choose a file...", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    st.info("⚡ Processing file lines using native text engine...")
    extracted_lines = []
    
    # Process file using PyMuPDF
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype=file_extension)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")  # Extract layout text
            
            for line in text.split("\n"):
                if line.strip():
                    if file_extension == "pdf":
                        extracted_lines.append(f"[Page {page_num+1}] {line.strip()}")
                    else:
                        extracted_lines.append(line.strip())
                        
        if extracted_lines:
            # Build clean data preview dataframe
            df_final = pd.DataFrame({
                "Line": range(1, len(extracted_lines) + 1),
                "Extracted Text": extracted_lines
            })
            
            st.subheader("📊 Extracted Data Preview")
            st.dataframe(df_final)
            
            # Create Excel download buffer
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False)
                
            st.download_button(
                label="📥 Download as Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="converted_text.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No direct text metadata found. If this is a photo/scanned file, it may require OCR libraries.")
            
    except Exception as e:
        st.error(f"Processing Error: {e}")
