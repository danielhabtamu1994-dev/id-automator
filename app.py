import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import numpy as np
import io

st.set_page_config(page_title="ID Extractor Pro", layout="wide")

st.title("🪪 ፕሮፌሽናል መታወቂያ አንባቢ እና ፎቶ ቆራጭ")

uploaded_file = st.file_uploader("የመታወቂያ ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # 1. ምስሉን ለ Streamlit ለማሳየት እና ለ OpenCV ለማዘጋጀት
    file_bytes = uploaded_file.read() # ፋይሉን አንድ ጊዜ እናንብበው
    
    # ለ PIL (ማሳያ)
    image_pil = Image.open(io.BytesIO(file_bytes))
    st.image(image_pil, caption="የተጫነው ምስል", width=300)
    
    # ለ OpenCV (ፎቶ ለመቁረጥ)
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    col1, col2 = st.columns(2)
    
    if st.button("ጽሁፍ እና ፎቶ አውጣ"):
        if image_cv is None:
            st.error("ምስሉን ማንበብ አልተቻለም። እባክዎ ፋይሉን ያረጋግጡ።")
        else:
            with st.spinner("ሲስተሙ እያነበበ እና እየቆረጠ ነው..."):
                try:
                                    # --- ክፍል 1፡ ሙሉ ጉርድ ፎቶውን መቁረጥ (Fixed Frame Crop) ---
                with col1:
                    st.subheader("📷 የተቆረጠው ጉርድ ፎቶ")
                    
                    height, width = image_cv.shape[:2]
                    
                    # ምስሉ ሁልጊዜ ተመሳሳይ ከሆነ፣ ማዕቀፉን (Frame) መፈለግ ይሻላል
                    # እዚህ ጋር እንደ ምሳሌ ምስሉ ካለበት ቦታ ዙሪያውን ቆርጠናል
                    # ልኬቱን (Coordinates) እንደ አስፈላጊነቱ ማስተካከል ትችላለህ
                    
                    # ለምሳሌ ከላይ 10%፣ ከታች 10%፣ ከግራና ቀኝ 10% ትተን መቁረጥ
                    start_row, start_col = int(height * 0.05), int(width * 0.12)
                    end_row, end_col = int(height * 0.95), int(width * 0.88)
                    
                    cropped_img = image_cv[start_row:end_row, start_col:end_col]
                    
                    if cropped_img.size > 0:
                        cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                        st.image(cropped_rgb, caption="የወጣው ሙሉ ፎቶ", width=200)
                        
                        is_success, buffer = cv2.imencode(".png", cropped_img)
                        st.download_button("ፎቶውን አውርድ", data=buffer.tobytes(), file_name="full_photo.png", mime="image/png")
                    else:
                        st.warning("ፎቶውን መቁረጥ አልተቻለም።")

                    
                    # --- ክፍል 2፡ ጽሁፍ ማውጣት (OCR) ---
                    with col2:
                        st.subheader("📝 የወጣው ጽሁፍ")
                        # ምስሉን ለ OCR ትንሽ እናጥራው (Pre-processing)
                        text = pytesseract.image_to_string(gray, lang='amh+eng')
                        
                        if text.strip():
                            st.text_area("የተገኘ መረጃ፦", text, height=300)
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button("Excel አውርድ", data=csv, file_name="data.csv")
                        else:
                            st.warning("ምንም ጽሁፍ አልተገኘም።")
                            
                except Exception as e:
                    st.error(f"የማንበብ ስህተት ተፈጥሯል፦ {e}")
