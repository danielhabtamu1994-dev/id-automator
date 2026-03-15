import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Multi-Language OCR", layout="centered")

st.title("🪪 አማርኛ እና እንግሊዝኛ አንባቢ")
st.write("መታወቂያው ላይ ያለውን የአማርኛ እና የእንግሊዝኛ ጽሁፍ በአንድ ላይ ያወጣል።")

uploaded_file = st.file_uploader("የመታወቂያ ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("ሁሉንም ጽሁፍ አውጣ"):
        with st.spinner("በመፈለግ ላይ..."):
            try:
                # እዚህ ጋር ነው ለውጡ፡ amh+eng ተቀናጅተዋል
                text = pytesseract.image_to_string(image, lang='amh+eng')
                
                if text.strip():
                    st.success("ተጠናቀቀ!")
                    st.text_area("የወጣው መረጃ፦", text, height=250)
                    
                    # ወደ ሰንጠረዥ መቀየር
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    df = pd.DataFrame(lines, columns=["ዝርዝር መረጃ"])
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("Excel አውርድ", data=csv, file_name="extracted_data.csv")
                else:
                    st.warning("ምንም ጽሁፍ አልተገኘም።")
            
            except Exception as e:
                st.error(f"ስህተት፡ {e}")
