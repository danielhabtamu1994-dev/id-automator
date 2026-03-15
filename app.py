import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import numpy as np
import io

st.set_page_config(page_title="ID Photo Extractor", layout="wide")

st.title("🪪 ፕሮፌሽናል መታወቂያ አንባቢ (Smart Crop)")
st.markdown("---")

uploaded_file = st.file_uploader("የመታወቂያ ስክሪንሾት ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    image_pil = Image.open(io.BytesIO(file_bytes))
    
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("የተጫነው ምስል")
        st.image(image_pil, width=350)

    if st.button("መረጃውን እና ፎቶውን አውጣ"):
        if image_cv is None:
            st.error("ምስሉን ማንበብ አልተቻለም!")
        else:
            with st.spinner("ሲስተሙ ነጩን ባክግራውንድ በማጥፋት ላይ ነው..."):
                try:
                    # --- 1. ነጩን ባክግራውንድ ፈልጎ ፎቶውን መቁረጥ ---
                    # ምስሉን ወደ ግራጫ (Grayscale) መቀየር
                    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                    
                    # ነጭ ያልሆነውን ክፍል ለመለየት (Thresholding)
                    # ከ 240 በላይ የሆኑ ፒክሰሎች (ነጭ አካባቢዎች) ይጠፋሉ
                    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                    
                    # የነጩን ባክግራውንድ ዳርቻዎች (Contours) መፈለግ
                    contours, _ = cv2.find_all_contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    st.markdown("---")
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.subheader("📷 የወጣው ጉርድ ፎቶ")
                        if contours:
                            # በትልቅነቱ አንደኛ የሆነውን ኮንቱር መምረጥ (ይህ ፎቶው ነው)
                            c = max(contours, key=cv2.contourArea)
                            x, y, w, h = cv2.boundingRect(c)
                            
                            # ፎቶውን መቁረጥ (ከነጩ ነፃ የሆነውን ክፍል)
                            cropped_img = image_cv[y:y+h, x:x+w]
                            
                            if cropped_img.size > 0:
                                cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                                st.image(cropped_rgb, width=250)
                                
                                is_success, buffer = cv2.imencode(".png", cropped_img)
                                st.download_button("ፎቶውን አውርድ", data=buffer.tobytes(), file_name="photo.png")
                        else:
                            st.warning("ነጭ ያልሆነ ፎቶ ሊገኝ አልቻለም።")

                    # --- 2. ጽሁፍ ማውጣት (Amharic + English) ---
                    with res_col2:
                        st.subheader("📝 የወጣው ጽሁፍ")
                        text = pytesseract.image_to_string(gray, lang='amh+eng')
                        if text.strip():
                            st.text_area("የተገኘ መረጃ፦", text, height=350)
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button("Excel አውርድ", data=csv, file_name="data.csv")
                
                except Exception as e:
                    st.error(f"ስህተት ተፈጥሯል፦ {e}")
