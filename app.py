import streamlit as st
import requests
from PIL import Image
import io
import os

st.set_page_config(page_title="Image Translator", page_icon="🖼️")
st.title("🖼️ ระบบแปลภาษาจากภาพ (Image Translation App)")

uploaded_file = st.file_uploader("📤 อัปโหลดภาพ", type=["jpg", "jpeg", "png"])
target_lang = st.selectbox("🌐 เลือกภาษาที่ต้องการแปล", ["en", "th", "ja", "fr", "zh-cn"])

if uploaded_file:
    st.image(uploaded_file, caption="ภาพต้นฉบับ", use_column_width=True)

    if st.button("เริ่มแปลภาพ 🧠"):
        with st.spinner("กำลังประมวลผล..."):
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(
                "http://localhost:8000/translate_image/",
                files={"file": uploaded_file},
                params={"target_lang": target_lang}
            )
            result = response.json()
            translated_path = result["translated_image"]

            if os.path.exists(translated_path):
                img = Image.open(translated_path)
                st.image(img, caption="📄 ภาพที่แปลแล้ว", use_column_width=True)
            else:
                st.warning("⚠️ ไม่พบไฟล์ผลลัพธ์")

            st.subheader("ข้อความที่ตรวจพบและแปลแล้ว")
            for original, translated in result["text_data"]:
                st.write(f"**{original} → {translated}**")
