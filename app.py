import streamlit as st
import pandas as pd
import io
from PIL import Image
from google import genai
import json

st.set_page_config(page_title="AI File to Excel Converter", layout="centered")
st.title("📄 Image & PDF to Excel Converter")

# --- API KEY INPUT ---
# You can get a free API key from Google AI Studio (https://aistudio.google.com)
st.sidebar.subheader("🔑 API Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded File Preview", use_container_width=True)
    
    if not api_key:
        st.warning("Please enter your Gemini API Key in the left sidebar to process the image.")
    else:
        st.info("🤖 AI Document Agent is analyzing the table matrix structure...")
        
        try:
            # Initialize the official Google GenAI client
            client = genai.Client(api_key=api_key)
            
            # Request structured JSON format directly from the visual layout
            prompt = """
            Analyze this document image carefully. Identify the main table structure.
            Extract all rows and columns exactly as they are aligned in the image.
            Return the output as a clean, raw JSON list of arrays (rows), where each item represents a row grid.
            Do not include markdown blocks or text explanations, just valid JSON data.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt]
            )
            
            # Clean up the raw text string from the model response
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            
            # Parse the structured JSON into a beautiful table
            table_data = json.loads(clean_text)
            df_final = pd.DataFrame(table_data)
            
            st.subheader("📊 Extracted Table Preview")
            st.dataframe(df_final)
            
            # Generate your Excel download file
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, header=False)
                
            st.download_button(
                label="📥 Download as Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="ai_extracted_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"AI Processing failed: {e}")
