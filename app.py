import streamlit as st
import pandas as pd
import io
from PIL import Image
from google import genai
import json
import re

# 1. Page Configuration
st.set_page_config(
    page_title="TabularAI - Image to Excel", 
    page_icon="⚡", 
    layout="centered"
)

# Custom CSS to make the interface look highly premium
st.markdown("""
    <style>
    .main-title {
        text-align: center; 
        padding: 10px;
        color: #0066cc; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-size: 2.8rem;
        font-weight: 700;
    }
    .sub-title {
        text-align: center;
        color: #555555;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .stDownloadButton button {
        background-color: #0066cc !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease;
    }
    .stDownloadButton button:hover {
        background-color: #004499 !important;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Modern Header Display
st.markdown('<div class="main-title">⚡ TabularAI Converter</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Convert Scanned JPJ/Images into Perfect Excel Files Instantly</div>', unsafe_allow_html=True)
st.markdown("---")

# Automatically fetch key from Streamlit Cloud Secrets
api_key = st.secrets.get("GEMINI_API_KEY", None)

# Two-column dynamic layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📸 Upload Image")
    uploaded_file = st.file_uploader(
        "Drop your file here", 
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.success(f"📂 Loaded: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document Preview", use_container_width=True)

with col2:
    st.markdown("### 🤖 AI Processing Engine")
    
    if uploaded_file is None:
        st.info("💡 Drop an image (JPG/PNG) on the left side to instantly extract your structured table data.")
    else:
        if not api_key:
            st.error("❌ API Key missing! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")
        else:
            with st.spinner("🧠 AI Agent is analyzing rows and aligning columns..."):
                try:
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
                    
                    # Regex logic to clean and pull the structured table safely
                    match = re.search(r'\[\s*\s*.*\]', response.text, re.DOTALL)
                    if match:
                        clean_text = match.group(0)
                    else:
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    
                    table_data = json.loads(clean_text)
                    df_final = pd.DataFrame(table_data)
                    
                    st.success("🎉 Data extraction successful!")
                    st.session_state['image_df'] = df_final
                    
                except Exception as e:
                    st.error(f"Processing Error: {e}")

st.markdown("---")

# Data Presentation and Excel Download Zone
if 'image_df' in st.session_state and uploaded_file is not None:
    df_final = st.session_state['image_df']
    
    st.markdown("### 📊 Extracted Table Grid Preview")
    st.dataframe(df_final, use_container_width=True)
    
    # Prep Excel File
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Beautiful Centered Download Action Button
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        st.download_button(
            label="📥 Download Structured Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="ai_aligned_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
