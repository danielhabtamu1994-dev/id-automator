import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import json

st.set_page_config(page_title="ID Extractor", layout="centered")

st.title("🪪 የመታወቂያ መረጃ አውቶሜሽን")

# በሳይድባር የ API ቁልፍ ማስገቢያ
api_key = st.sidebar.text_input("OpenAI API Key ያስገቡ", type="password")

uploaded_file = st.file_uploader("የስክሪንሾት ፋይል ይምረጡ...", type=['png', 'jpg', 'jpeg'])

# ምስሉ ከተመረጠ በኋላ ቁልፉ እንዲመጣ
if uploaded_file is not None:
    st.image(uploaded_file, caption="የተጫነው ምስል", use_container_width=True)
    
    # ቁልፉ እዚህ ጋር ነው
    extract_button = st.button("መረጃውን አውጣ (Extract Data)")

    if extract_button:
        if not api_key:
            st.error("እባክዎ መጀመሪያ በግራ በኩል ባለው ሜኑ የ OpenAI API Key ያስገቡ!")
        else:
            client = OpenAI(api_key=api_key)
            base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
            
            with st.spinner("AI መረጃውን እያነበበ ነው..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all person information from this image. Output ONLY a JSON array of objects with keys: 'Full Name', 'Position', 'ID Number', 'Phone'."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ],
                            }
                        ],
                    )
                    
                    data = json.loads(response.choices[0].message.content.replace('```json', '').replace('```', '').strip())
                    df = pd.DataFrame(data)
                    st.success("ተሳክቷል!")
                    st.table(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("በ Excel (CSV) አውርድ", data=csv, file_name="data.csv")
                except Exception as e:
                    st.error(f"ስህተት፡ {e}")
