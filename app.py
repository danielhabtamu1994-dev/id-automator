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
                    # --- ክፍል 1፡ ፊት ፈልጎ መቁረጥ ---
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                    
                    with col1:
                        st.subheader("📷 የተቆረጠው ፎቶ")
                        if len(faces) > 0:
                            (x, y, w, h) = faces[0]
                            # ፎቶው ትንሽ ሰፋ እንዲል (Padding)
                            cropped_face = image_cv[max(0, y-20):y+h+20, max(0, x-20):x+w+20]
                            cropped_face_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                            st.image(cropped_face_rgb, width=150)
                            
                            is_success, buffer = cv2.imencode(".png", cropped_face)
                            st.download_button("ፎቶውን አውርድ", data=buffer.tobytes(), file_name="face.png", mime="image/png")
                        else:
                            st.warning("ምስሉ ላይ ፊት ሊገኝ አልቻለም።")
                    
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
