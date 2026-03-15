import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import numpy as np

# የገጽ መዋቅር
st.set_page_config(page_title="ID Extractor Pro", layout="wide")

st.title("🪪 ፕሮፌሽናል መታወቂያ አንባቢ እና ፎቶ ቆራጭ")
st.write("ይህ ሲስተም ያለ AI ጽሁፉን ያነባል፣ ፎቶውንም ለይቶ ይቆርጣል።")

uploaded_file = st.file_uploader("የመታወቂያ ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # 1. ምስሉን ለ streamlit ማሳየት
    image_pil = Image.open(uploaded_file)
    st.image(image_pil, caption="የተጫነው ምስል", width=300)
    
    # 2. ለ OpenCV እና OCR ምስሉን ማዘጋጀት
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image_cv = cv2.imdecode(file_bytes, 1) # ምስሉን በ OpenCV መክፈት
    
    # ኮለመን መፍጠር (ግራ እና ቀኝ ለማሳየት)
    col1, col2 = st.columns(2)
    
    if st.button("ጽሁፍ እና ፎቶ አውጣ"):
        with st.spinner("ሲስተሙ እያነበበ እና እየቆረጠ ነው..."):
            try:
                # --- ክፍል 1፡ ፊት ፈልጎ መቁረጥ (Face Detection) ---
                # የፊት መፈለጊያ ፋይል (Haar Cascade) መጥራት
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                
                # ምስሉን ወደ ግራጫ (Grayscale) መቀየር
                gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                
                # ፊቶችን መፈለግ
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                # col1 (የመጀመሪያው ኮለመን) ላይ ፎቶውን ማሳየት
                with col1:
                    st.subheader("📷 የተቆረጠው ፎቶ")
                    if len(faces) > 0:
                        # የመጀመሪያውን ፊት መቁረጥ (ካሬውን)
                        (x, y, w, h) = faces[0]
                        cropped_face = image_cv[y:y+h, x:x+w]
                        
                        # OpenCV ምስልን ወደ PIL መቀየር
                        cropped_face_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                        cropped_face_pil = Image.fromarray(cropped_face_rgb)
                        
                        st.image(cropped_face_pil, caption="የተቆረጠ ፎቶ", width=150)
                        
                        # ፎቶውን ለማውረድ ማዘጋጀት
                        is_success, buffer = cv2.imencode(".png", cropped_face)
                        st.download_button("ፎቶውን አውርድ", data=buffer.tobytes(), file_name="face.png", mime="image/png")
                    else:
                        st.warning("ምስሉ ላይ ፊት ሊገኝ አልቻለም።")
                
                # --- ክፍል 2፡ ጽሁፍ ማውጣት (Amharic + English OCR) ---
                with col2:
                    st.subheader("📝 የወጣው ጽሁፍ")
                    # Tesseract lang='amh+eng'
                    text = pytesseract.image_to_string(gray, lang='amh+eng')
                    
                    if text.strip():
                        st.text_area("የተገኘ መረጃ፦", text, height=300)
                        
                        # ወደ ሰንጠረዥ መቀየር
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("Excel አውርድ", data=csv, file_name="data.csv")
                    else:
                        st.warning("ምንም ጽሁፍ አልተገኘም።")
                        
            except Exception as e:
                st.error(f"ስህተት፡ {e}")
                st.info("ምክር፡ 'packages.txt' እና 'requirements.txt' በትክክል መጫናቸውን ያረጋግጡ።")
