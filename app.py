import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd

st.set_page_config(page_title="No-AI OCR", layout="centered")

st.title("🪪 ምስልን ወደ ጽሁፍ መቀየሪያ (ያለ AI)")
st.write("ይህ ዌብሳይት ምስልን ለማንበብ ምንም አይነት የ AI ክፍያ አይጠይቅም።")

uploaded_file = st.file_uploader("የመታወቂያውን ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # ምስሉን መክፈት
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("ጽሁፉን አንብብ (Extract Text)"):
        with st.spinner("ሲስተሙ ምስሉን እያነበበ ነው..."):
            try:
                # ጽሁፉን ማውጣት (OCR)
                # ማሳሰቢያ፡ ስልክ ላይ የምትሞክር ከሆነ Tesseract መጫኑን አረጋግጥ
                text = pytesseract.image_to_string(image)
                
                if text.strip():
                    st.success("ማንበብ ተችሏል!")
                    
                    # የወጣውን ጽሁፍ ለተጠቃሚው ማሳየት
                    st.text_area("የተገኘው ጽሁፍ፦", text, height=200)
                    
                    # መረጃውን መስመር በመስመር ከፋፍሎ ሰንጠረዥ ውስጥ ማስገባት
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    df = pd.DataFrame(lines, columns=["የተገኙ መረጃዎች"])
                    st.dataframe(df, use_container_width=True)
                    
                    # ኤክሴል አድርጎ ለማውረድ
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("በ Excel (CSV) አውርድ", data=csv, file_name="extracted_text.csv")
                else:
                    st.warning("ምንም ጽሁፍ ሊገኝ አልቻለም። ምስሉ ጥራት ያለው መሆኑን ያረጋግጡ።")
            
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል፦ {e}")
                st.info("ምክር፡ በ Streamlit Cloud ላይ ከሆኑ 'packages.txt' ፋይል በትክክል መጨመሩን ያረጋግጡ።")
