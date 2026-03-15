import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="ID Automator", layout="centered")
st.title("🪪 የመታወቂያ መረጃ አውቶሜሽን (Gemini)")

# የ Gemini API Key ማስገቢያ (ከ aistudio.google.com በነፃ ማግኘት ትችላለህ)
api_key = st.sidebar.text_input("Google Gemini API Key ያስገቡ", type="password")

uploaded_file = st.file_uploader("የስክሪንሾት ፋይል ይምረጡ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("መረጃውን አውጣ (Extract Data)"):
        if not api_key:
            st.error("እባክዎ መጀመሪያ የ Gemini API Key ያስገቡ!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner("AI መረጃውን እያነበበ ነው..."):
                    # ለ AI የሚሰጥ ትዕዛዝ
                    prompt = "Extract all person information from this image. Output ONLY a JSON array of objects with keys: 'Full Name', 'Position', 'ID Number', 'Phone'. No extra text."
                    response = model.generate_content([prompt, image])
                    
                    # ጽሁፉን ወደ JSON መቀየር
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(res_text)
                    
                    df = pd.DataFrame(data)
                    st.success("ተሳክቷል!")
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Excel (CSV) አውርድ", data=csv, file_name="extracted.csv")
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል፦ {e}")
