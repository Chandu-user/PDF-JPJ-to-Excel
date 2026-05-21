import streamlit as st
import pandas as pd
import io
from PIL import Image

# 1. App Configuration & Title
st.set_page_config(page_title="File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")
st.write("Upload a PDF or an Image (JPG/PNG) containing a table, and we will convert it to an Excel spreadsheet.")

# 2. File Uploader Component
uploaded_file = st.file_uploader(
    "Choose a file...", 
    type=["pdf", "jpg", "jpeg", "png"]
)

# 3. Processing Logic
if uploaded_file is not None:
    # Display details about the uploaded file
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    
    # Check the file type
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    # Placeholder for our final data
    df_result = None

    if file_extension in ["jpg", "jpeg", "png"]:
        st.info("Processing Image file...")
        # Show a preview of the image to the user
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)
        
        # --- PLACEHOLDER FOR OCR ENGINE ---
        # In a complete app, you would use 'pytesseract' or 'easyocr' here.
        # For this sample interface, we simulate an extracted table:
        st.warning("OCR Engine text extraction happens here.")
        df_result = pd.DataFrame({
            "Receipt/Data Column 1": ["Item A", "Item B", "Item C"],
            "Amount": [10.50, 24.99, 5.00]
        })

    elif file_extension == "pdf":
        st.info("Processing PDF file...")
        
        # --- PLACEHOLDER FOR PDF PARSER ---
        # In a complete app, you would use 'pdfplumber' or 'camelot-py' here.
        st.warning("PDF table parsing happens here.")
        df_result = pd.DataFrame({
            "Invoice Number": ["INV-001", "INV-002"],
            "Client": ["Acme Corp", "Wayne Enterprises"],
            "Total Due": ["$1,200", "$3,500"]
        })

    # 4. Preview and Download Section
    if df_result is not None:
        st.subheader("📊 Extracted Data Preview")
        st.dataframe(df_result) # Displays the data in an interactive grid

        # Convert the DataFrame to an Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, index=False, sheet_name='Converted Data')
        
        # Download Button
        st.download_button(
            label="📥 Download as Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"converted_{uploaded_file.name.split('.')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )