import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="ID Automator Pro", layout="centered")
st.title("🪪 የመታወቂያ መረጃ አውቶሜሽን")

api_key = st.sidebar.text_input("Google Gemini API Key ያስገቡ", type="password")
st.sidebar.markdown("[API Key ከዚህ ያግኙ](https://aistudio.google.com/app/apikey)")

# የደህንነት ገደቦችን ማላላት
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

uploaded_file = st.file_uploader("የመረጃውን ምስል ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("መረጃውን አውጣ (Extract Data)"):
        if not api_key:
            st.error("እባክዎ መጀመሪያ የ Gemini API Key ያስገቡ!")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # ሞዴሉን ወደ gemini-1.5-pro ቀይረነዋል (ይህ ብዙ ጊዜ 404 አይሰጥም)
                model = genai.GenerativeModel(
                    model_name='gemini-1.0-pro',
                    safety_settings=safety_settings
                )
                
                with st.spinner("AI መረጃውን እያነበበ ነው..."):
                    prompt = "In this image, find names, positions, and ID numbers. Return them as a JSON list. Keys: 'Full Name', 'Position', 'ID Number', 'Phone'."
                    
                    # አሰራሩን ትንሽ ቀየር አድርገነዋል
                    response = model.generate_content([prompt, image])
                    
                    res_text = response.text
                    # JSON ብቻ መሆኑን ለማረጋገጥ ማጽጃ
                    if "```json" in res_text:
                        res_text = res_text.split("```json")[1].split("```")[0]
                    elif "```" in res_text:
                        res_text = res_text.split("```")[1].split("```")[0]
                    
                    data = json.loads(res_text.strip())
                    df = pd.DataFrame(data)
                    
                    st.success("✅ ተሳክቷል!")
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Excel (CSV) አውርድ", data=csv, file_name="data.csv")
                    
            except Exception as e:
                # ሞዴሉ ካልተገኘ ወደ ሌላ አማራጭ (gemini-pro-vision) እንዲቀይር
                st.error(f"ስህተት፡ {e}")
                st.info("ምክር፡ 'gemini-1.5-pro' ካልሰራ 'gemini-1.0-pro-vision' የሚለውን ስም በኮዱ ውስጥ መቀየር ይቻላል።")
