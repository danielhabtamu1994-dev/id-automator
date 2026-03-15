import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import json

# የገጽ መዋቅር
st.set_page_config(page_title="ID Card Data Extractor", layout="centered")

st.title("🪪 የመታወቂያ መረጃ አውቶሜሽን")
st.write("የመረጃውን ስክሪንሾት ይጫኑ፣ AI መረጃውን አውጥቶ ኤክሴል ያዘጋጅልዎታል!")

# API Key ማስገቢያ (በሴቲንግ ወይም በሳይድባር)
api_key = st.sidebar.text_input("OpenAI API Key ያስገቡ", type="password")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

if api_key:
    client = OpenAI(api_key=api_key)
    
    uploaded_file = st.file_uploader("የስክሪንሾት ፋይል ይምረጡ...", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="የተጫነው ምስል", use_container_width=True)
        
        if st.button("መረጃውን አውጣ (Extract Data)"):
            base64_image = encode_image(uploaded_file)
            
            with st.spinner("AI ምስሉን እያነበበ ነው... እባክዎ ይጠብቁ"):
                try:
                    # AI ምስሉን እንዲያነብ የሚሰጠው ትዕዛዝ (Prompt)
                    response = client.chat.completions.create(
                        model="gpt-4o", # በጣም ጎበዝ የሆነው የ OpenAI ሞዴል
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all person information from this image. Output ONLY a JSON array of objects with keys: 'Full Name', 'Position', 'ID Number', 'Phone'. Do not include any other text."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ],
                            }
                        ],
                        max_tokens=1500,
                    )
                    
                    # ውጤቱን መቀበል
                    raw_content = response.choices[0].message.content
                    # JSON መሆኑን ማረጋገጥ
                    json_str = raw_content.replace('```json', '').replace('```', '').strip()
                    data = json.loads(json_str)
                    
                    # ወደ ሰንጠረዥ መቀየር
                    df = pd.DataFrame(data)
                    
                    st.success("✅ መረጃው በተሳካ ሁኔታ ወጥቷል!")
                    st.dataframe(df, use_container_width=True)
                    
                    # ወደ CSV መቀየርና ለማውረድ ማዘጋጀት
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="መረጃውን በ Excel (CSV) አውርድ",
                        data=csv,
                        file_name="id_data_extracted.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"ስህተት ተፈጥሯል፦ {e}")
else:
    st.info("💡 ለመጀመር መጀመሪያ የ OpenAI API Key በግራ በኩል ባለው ሳጥን ውስጥ ያስገቡ።")
