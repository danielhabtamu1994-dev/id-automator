import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Amharic OCR", layout="centered")

st.title("🪪 የአማርኛ መታወቂያ አንባቢ (ያለ AI)")
st.write("ይህ ሲስተም የአማርኛ ፊደላትን ለይቶ ያነባል።")

uploaded_file = st.file_uploader("የመታወቂያውን ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("አማርኛውን አንብብ (Extract Amharic)"):
        with st.spinner("አማርኛውን እያነበብኩ ነው... እባክዎ ይጠብቁ"):
            try:
                # ቋንቋውን ወደ አማርኛ (amh) ቀይረነዋል
                # አማርኛ እና እንግሊዝኛ እንዲቀላቀል ከፈለክ lang='amh+eng' ማድረግ ትችላለህ
                text = pytesseract.image_to_string(image, lang='amh')
                
                if text.strip():
                    st.success("ተሳክቷል!")
                    st.text_area("የወጣው የአማርኛ ጽሁፍ፦", text, height=250)
                    
                    # መረጃውን ወደ ሰንጠረዥ መቀየር
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    df = pd.DataFrame(lines, columns=["የተገኘ መረጃ"])
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8-sig') # ለአማርኛ utf-8-sig ይሻላል
                    st.download_button("በ Excel (CSV) አውርድ", data=csv, file_name="amharic_data.csv")
                else:
                    st.warning("ምንም የአማርኛ ጽሁፍ ሊገኝ አልቻለም።")
            
            except Exception as e:
                st.error(f"ስህተት፦ {e}")
                st.info("ምክር፦ 'packages.txt' ላይ 'tesseract-ocr-amh' መጨመሩን ያረጋግጡ።")
