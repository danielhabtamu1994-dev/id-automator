import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import numpy as np
import io

# የገጽ መዋቅር እና ዲዛይን
st.set_page_config(page_title="ID Processor Pro", layout="wide")

# የዌብሳይቱ ርዕስ እና አርማ
st.title("🪪 ፕሮፌሽናል መታወቂያ አንባቢ እና ፎቶ ቆራጭ")
st.markdown("---")

uploaded_file = st.file_uploader("የመታወቂያ ምስል/ስክሪንሾት ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # ምስሉን አንዴ ማንበብ (ለማሳያ እና ለሂደት)
    file_bytes = uploaded_file.read()
    
    # ለ Streamlit ማሳያ
    image_pil = Image.open(io.BytesIO(file_bytes))
    
    # ለ OpenCV ማቀነባበሪያ
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # በግራ እና በቀኝ መረጃዎችን ለማሳየት
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("የተጫነው ምስል")
        st.image(image_pil, width=300)

    if st.button("መረጃውን እና ፎቶውን አውጣ"):
        if image_cv is None:
            st.error("ምስሉን ማንበብ አልተቻለም!")
        else:
            with st.spinner("ሲስተሙ መረጃዎችን እያወጣ ነው..."):
                try:
                    # --- 1. ሙሉ ጉርድ ፎቶውን መቁረጥ (Frame Cropping) ---
                    # ምስሉ ሁልጊዜ ተመሳሳይ ስለሆነ በልኬት መቁረጥ ይሻላል
                    height, width = image_cv.shape[:2]
                    
                    # ፎቶው ያለበትን ቦታ መለካት (እነዚህን ቁጥሮች እንደ አስፈላጊነቱ ያሻሽሉ)
                    start_row = int(height * 0.08) # ከላይ 8% ተው
                    end_row = int(height * 0.92)   # ከታች 8% ተው
                    start_col = int(width * 0.15)  # ከግራ 15% ተው
                    end_col = int(width * 0.85)    # ከቀኝ 15% ተው
                    
                    cropped_img = image_cv[start_row:end_row, start_col:end_col]
                    
                    # --- 2. ጽሁፍ ማውጣት (Amharic + English) ---
                    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                    # ጽሁፉን ይበልጥ ግልጽ ለማድረግ (Thresholding)
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                    
                    extracted_text = pytesseract.image_to_string(thresh, lang='amh+eng')

                    # ውጤቶችን ማሳየት
                    st.markdown("---")
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.subheader("📷 የተቆረጠው ጉርድ ፎቶ")
                        if cropped_img.size > 0:
                            cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                            st.image(cropped_rgb, width=200)
                            
                            # ፎቶውን ማውረጃ
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
                            st.text_area("የተገኘ መረጃ፦", extracted_text, height=250)
                            
                            # ሰንጠረዥ ውስጥ ማስገባት
                            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                            df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                            st.dataframe(df, use_container_width=True)
                            
                            # ኤክሴል ማውረጃ
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label="መረጃውን በ Excel (CSV) አውርድ",
                                data=csv,
                                file_name="id_text_data.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("ምንም ሊነበብ የሚችል ጽሁፍ አልተገኘም።")

                except Exception as e:
                    st.error(f"ስህተት ተፈጥሯል፦ {e}")
