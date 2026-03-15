import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import json

# የገጽ መዋቅር
st.set_page_config(page_title="ID Automator Pro", layout="centered")
st.title("🪪 የመታወቂያ መረጃ አውቶሜሽን")
st.write("የሰራተኞች ዝርዝር ያለበትን ምስል ይጫኑ።")

# በሳይድባር የ Gemini API ቁልፍ ማስገቢያ
api_key = st.sidebar.text_input("Google Gemini API Key ያስገቡ", type="password")
st.sidebar.markdown("[API Key ከዚህ ያግኙ](https://aistudio.google.com/app/apikey)")

# የደህንነት ገደቦችን ማላላት (Safety Settings)
# ይህ AI-ው መታወቂያዎችን ሲያይ እንዳያግድ ይረዳዋል
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

uploaded_file = st.file_uploader("የመረጃውን ምስል/ስክሪንሾት ይጫኑ...", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="የተጫነው ምስል", use_container_width=True)
    
    if st.button("መረጃውን አውጣ (Extract Data)"):
        if not api_key:
            st.error("እባክዎ መጀመሪያ የ Gemini API Key ያስገቡ!")
        else:
            try:
                # Gemini ማቀናጃ
                genai.configure(api_key=api_key)
                
                # ሞዴሉን ከነደህንነት ማስተካከያው መጥራት
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    safety_settings=safety_settings
                )
                
                with st.spinner("AI መረጃውን እያነበበ ነው..."):
                    # ለ AI የሚሰጥ ጥብቅ ትዕዛዝ (Prompt)
                    # "መታወቂያ" ከማለት ይልቅ "ሰነድ" የሚለውን ቃል ተጠቅሜያለሁ
                    prompt = """
                    Extract all text information from this document. 
                    Organize it into a JSON array of objects.
                    Each object should have these keys: 'Full Name', 'Position', 'ID Number', 'Phone'.
                    If a field is missing, leave it empty.
                    Return ONLY the raw JSON data.
                    """
                    
                    response = model.generate_content([prompt, image])
                    
                    # ውጤቱን ከማያስፈልጉ ምልክቶች ማጽዳት
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    
                    # ወደ JSON እና Pandas DataFrame መቀየር
                    data = json.loads(res_text)
                    df = pd.DataFrame(data)
                    
                    st.success("✅ መረጃው በተሳካ ሁኔታ ወጥቷል!")
                    st.dataframe(df, use_container_width=True)
                    
                    # ለኤክሴል እንዲመች ማዘጋጀት
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="መረጃውን በ Excel (CSV) አውርድ",
                        data=csv,
                        file_name="id_data_extracted.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"ስህተት ተፈጥሯል፦ {e}")
                st.info("ምክር፦ ምስሉ በጣም ደብዛዛ ካልሆነና API Key-ው የሚሰራ ከሆነ ደግመው ይሞክሩ።")
