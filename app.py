import streamlit as st
import pandas as pd
import io
from PIL import Image
from google import genai
import json
import re

st.set_page_config(page_title="AI File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

# 1. Automatically grab the key from Streamlit's backend Secrets manager
api_key = st.secrets.get("GEMINI_API_KEY", None)

uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded File Preview", use_container_width=True)
    
    if not api_key:
        st.error("❌ API Key missing! Please add 'GEMINI_API_KEY' to your Streamlit Cloud Secrets.")
    else:
        st.info("🤖 AI Document Agent is reading the visual table matrix...")
        
        try:
            # Initialize the Google GenAI client natively
            client = genai.Client(api_key=api_key)
            
            prompt = """
            Analyze this document image carefully. Identify the tabular layout data.
            Extract all text lines, matching the rows and columns exactly as they are aligned in the image layout.
            Return the data as a clean, raw JSON list of lists (a matrix where each element is an array of columns).
            Do not provide conversational introductions or markdown block ticks. Just return the raw data grid.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt]
            )
            
            # Use regular expressions to extract only the valid JSON array matrix, ignoring any extra conversational text
            match = re.search(r'\[\s*\s*.*\]', response.text, re.DOTALL)
            if match:
                clean_text = match.group(0)
            else:
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
            
            # Parse the text data into a structured Excel-ready grid
            table_data = json.loads(clean_text)
            df_final = pd.DataFrame(table_data)
            
            st.subheader("📊 Extracted Table Preview")
            st.dataframe(df_final)
            
            # Create download package
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, header=False)
                
            st.download_button(
                label="📥 Download as Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="ai_aligned_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Processing Error: {e}")
            st.info("Ensure your API key is correctly active and unrestricted in Google AI Studio.")
