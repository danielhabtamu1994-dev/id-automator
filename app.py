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
                    # --- 1. ፎቶውን ከላይ በግራ በኩል መቁረጥ (Top-Left Crop) ---
                    height, width = image_cv.shape[:2]
                    
                    # ፎቶው ያለበትን ሳጥን መለካት (በላክኸው ምስል መሠረት)
                    # ከላይ 0 ጀምሮ እስከ 45% ቁመት፣ ከግራ 0 ጀምሮ እስከ 48% ስፋት
                    crop_h = int(height * 0.45)
                    crop_w = int(width * 0.48)
                    
                    cropped_img = image_cv[0:crop_h, 0:crop_w]
                    
                    # --- 2. ጽሁፍ ማውጣት (Amharic + English OCR) ---
                    # ምስሉን ለ OCR ማዘጋጀት (ወደ ግራጫ መቀየር)
                    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                    
                    # ጽሁፉን ለማንበብ amh+eng እንጠቀማለን
                    extracted_text = pytesseract.image_to_string(gray, lang='amh+eng')

                    st.markdown("---")
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.subheader("📷 የወጣው ጉርድ ፎቶ")
                        if cropped_img.size > 0:
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
                            st.warning("ፎቶውን መቁረጥ አልተቻለም።")

                    with res_col2:
                        st.subheader("📝 የወጣው ጽሁፍ")
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
