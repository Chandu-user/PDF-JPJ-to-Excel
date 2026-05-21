import streamlit as st
import pandas as pd
import io
from PIL import Image
import easyocr
import numpy as np
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Smart File to Excel Converter", layout="centered")

st.title("📄 Smart PDF/Image to Excel Converter")

# Upload File
uploaded_file = st.file_uploader(
    "Upload JPG / PNG / PDF",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    file_extension = uploaded_file.name.split(".")[-1].lower()

    images_to_process = []

    # =========================
    # PDF TO IMAGE
    # =========================
    if file_extension == "pdf":

        st.info("Converting PDF pages to images...")

        pdf_images = convert_from_bytes(uploaded_file.read())

        images_to_process.extend(pdf_images)

        st.write(f"PDF Pages Found: {len(pdf_images)}")

        st.image(pdf_images[0], caption="Preview", use_container_width=True)

    else:

        image = Image.open(uploaded_file)

        images_to_process.append(image)

        st.image(image, caption="Preview", use_container_width=True)

    # =========================
    # OCR ENGINE
    # =========================
    st.info("🤖 Extracting structured data...")

    reader = easyocr.Reader(['en'])

    final_data = []

    # =========================
    # PROCESS EACH PAGE
    # =========================
    for page_no, img in enumerate(images_to_process):

        image_np = np.array(img)

        # detail=1 gives coordinates
        results = reader.readtext(image_np, detail=1)

        # Store extracted text with positions
        extracted_items = []

        for detection in results:

            bbox, text, confidence = detection

            # Top-left coordinate
            x = int(bbox[0][0])
            y = int(bbox[0][1])

            extracted_items.append({
                "text": text,
                "x": x,
                "y": y
            })

        # =========================
        # SORT BY POSITION
        # =========================
        extracted_items = sorted(
            extracted_items,
            key=lambda item: (item["y"], item["x"])
        )

        # =========================
        # GROUP SAME LINE TEXTS
        # =========================
        grouped_lines = []

        current_line = []
        previous_y = None

        threshold = 20

        for item in extracted_items:

            if previous_y is None:
                current_line.append(item)

            elif abs(item["y"] - previous_y) <= threshold:
                current_line.append(item)

            else:
                grouped_lines.append(current_line)
                current_line = [item]

            previous_y = item["y"]

        if current_line:
            grouped_lines.append(current_line)

        # =========================
        # CREATE STRUCTURED ROWS
        # =========================
        for line in grouped_lines:

            # Sort left to right
            line = sorted(line, key=lambda item: item["x"])

            texts = [item["text"] for item in line]

            # Combine into single line
            combined_text = " ".join(texts)

            # Try Key : Value extraction
            if ":" in combined_text:

                parts = combined_text.split(":", 1)

                key = parts[0].strip()

                value = parts[1].strip()

            else:

                # Handle side-by-side text
                if len(texts) >= 2:

                    key = texts[0]

                    value = " ".join(texts[1:])

                else:

                    key = "Text"

                    value = texts[0]

            final_data.append({
                "Page": page_no + 1,
                "Field": key,
                "Value": value
            })

    # =========================
    # DATAFRAME
    # =========================
    df = pd.DataFrame(final_data)

    st.subheader("📊 Extracted Structured Data")

    st.dataframe(df)

    # =========================
    # EXPORT TO EXCEL
    # =========================
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:

        df.to_excel(writer, index=False, sheet_name='Extracted_Data')

    st.download_button(
        label="📥 Download Excel File",
        data=buffer.getvalue(),
        file_name="structured_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
