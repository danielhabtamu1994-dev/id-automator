import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import numpy as np
import io

# የገጽ መዋቅር
st.set_page_config(page_title="ID Extractor Pro", layout="wide")

st.title("🪪 ፕሮፌሽናል መታወቂያ አንባቢ እና ፎቶ ቆራጭ")
st.markdown("---")

uploaded_file = st.file_uploader("የመታወቂያ ስክሪንሾት ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # ምስሉን ማንበብ
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
            with st.spinner("ሲስተሙ ፎቶውን እየቆረጠ እና ጽሁፉን እያነበበ ነው..."):
                try:
                    # --- 1. ፎቶውን ለይቶ መቁረጥ (Face-based Smart Crop) ---
                    gray_img = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray_img, 1.1, 5)

                    st.markdown("---")
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.subheader("📷 የወጣው ጉርድ ፎቶ")
                        if len(faces) > 0:
                            # የመጀመሪያውን ፊት መውሰድ
                            (x, y, w, h) = faces[0]
                            
                            # ፊቱ ላይ ሰፋ ያለ ክፍተት (Padding) መጨመር (ሙሉ ጉርዱ እንዲወጣ)
                            height, width = image_cv.shape[:2]
                            offset_y = int(h * 0.8) # ወደ ላይ እና ወደ ታች 80% ጨምር
                            offset_x = int(w * 0.6) # ወደ ጎን 60% ጨምር
                            
                            y1 = max(0, y - offset_y)
                            y2 = min(height, y + h + int(offset_y/2))
                            x1 = max(0, x - offset_x)
                            x2 = min(width, x + w + offset_x)
                            
                            cropped_img = image_cv[y1:y2, x1:x2]
                            cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                            st.image(cropped_rgb, width=250)
                            
                            # ማውረጃ ቁልፍ
                            is_success, buffer = cv2.imencode(".png", cropped_img)
                            st.download_button(
                                label="ፎቶውን አውርድ",
                                data=buffer.tobytes(),
                                file_name="extracted_photo.png",
                                mime="image/png"
                            )
                        else:
                            st.warning("ምስሉ ላይ ፊት ሊገኝ አልቻለም።")

                    # --- 2. ጽሁፍ ማውጣት (Amharic + English OCR) ---
                    with res_col2:
                        st.subheader("📝 የወጣው ጽሁፍ")
                        # ጽሁፉን ለማንበብ amh+eng እንጠቀማለን
                        extracted_text = pytesseract.image_to_string(gray_img, lang='amh+eng')

                        if extracted_text.strip():
                            st.text_area("የተገኘ መረጃ፦", extracted_text, height=350)
                            
                            # ወደ ሰንጠረዥ መቀየር
                            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                            df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label="መረጃውን በ Excel (CSV) አውርድ",
                                data=csv,
                                file_name="extracted_data.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("ምንም ጽሁፍ አልተገኘም።")

                except Exception as e:
                    st.error(f"ስህተት ተፈጥሯል፦ {e}")
