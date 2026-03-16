import streamlit as st
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import cv2
import numpy as np
import io
import re

# ፋይሎች መኖራቸውን እርግጠኛ ሁን
FONT_PATH = "Nyala.ttf"
BG_PATH = "1000123189.jpg"

st.set_page_config(page_title="Fayda ID Processor", layout="wide")

st.title("🪪 ፋይዳ መታወቂያ መረጃ ነጣጣይ")
st.markdown("---")

# መረጃዎችን ነጥሎ የሚያወጣ ተግባር (Function)
def extract_id_details(text):
    details = {"name": "ያልተገኘ", "dob": "ያልተገኘ", "fan": "ያልተገኘ"}
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        # 1. ስም ፍለጋ (ከ Full Name ወይም ሙሉ ስም በታች ያለውን መስመር ይወስዳል)
        if "Full Name" in line or "ሙሉ ስም" in line:
            # ቃላቶቹን አጽድቶ ስሙን ብቻ ማስቀረት
            clean_name = re.sub(r'Full Name|ሙሉ ስም|[:|;]', '', line).strip()
            if not clean_name and i+1 < len(lines):
                clean_name = lines[i+1]
            details["name"] = clean_name
            
    # 2. የልደት ቀን ፍለጋ (ቀን የሚመስል ነገር ካለ - 00/00/0000)
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    if dob_match:
        details["dob"] = dob_match.group()
        
    # 3. የፋይዳ ቁጥር (FAN) ፍለጋ (12 እና ከዚያ በላይ ቁጥሮች)
    fan_match = re.search(r'\d{12,}', text)
    if fan_match:
        details["fan"] = fan_match.group()
        
    return details

uploaded_file = st.file_uploader("የቁም መታወቂያ ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    image_cv = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("የተጫነው ምስል")
        st.image(image_cv, channels="BGR", width=350)

    if st.button("መረጃውን ለይተህ አውጣ"):
        with st.spinner("ሲስተሙ መረጃውን እየለየ ነው..."):
            # 1. OCR ንባብ
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, lang='amh+eng')
            
            # 2. መረጃውን ነጥሎ ማውጣት
            extracted_info = extract_id_details(text)
            
            with col2:
                st.subheader("📝 የተለዩ መረጃዎች")
                name = st.text_input("ሙሉ ስም", value=extracted_info["name"])
                dob = st.text_input("የትውልድ ቀን", value=extracted_info["dob"])
                fan = st.text_input("የፋይዳ ቁጥር (FAN)", value=extracted_info["fan"])
                
                st.markdown("---")
                # 3. አግድም ባክግራውንድ ላይ መሳል
                try:
                    bg_img = Image.open(BG_PATH).convert("RGB")
                    draw = ImageDraw.Draw(bg_img)
                    nyala_font = ImageFont.truetype(FONT_PATH, 35)
                    
                    # ጽሁፎቹን በባክግራውንዱ ላይ መሳል
                    draw.text((415, 130), name, font=nyala_font, fill="black")
                    draw.text((415, 240), dob, font=nyala_font, fill="black")
                    draw.text((120, 520), f"FAN: {fan}", font=nyala_font, fill="black")
                    
                    st.image(bg_img, caption="የተዘጋጀው አግድም መታወቂያ", use_column_width=True)
                    
                    # ለማውረድ
                    buf = io.BytesIO()
                    bg_img.save(buf, format="PNG")
                    st.download_button("መታወቂያውን አውርድ", buf.getvalue(), f"{name}.png")
                    
                except Exception as e:
                    st.error(f"ባክግራውንድ ላይ ለመሳል አልተቻለም፦ {e}")
