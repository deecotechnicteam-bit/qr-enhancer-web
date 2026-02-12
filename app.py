import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai
import qrcode

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ultimate QR AI", page_icon="🛡️", layout="wide")

# --- ฟังก์ชันดึงรายชื่อโมเดลที่บัญชีนี้ใช้ได้จริง ---
def get_available_models(api_key):
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            # กรองเฉพาะโมเดลที่รองรับการจัดการภาพ (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception as e:
        return []

# --- Sidebar ---
with st.sidebar:
    st.header("🔑 API Access")
    api_key = st.text_input("ใส่ Gemini API Key:", type="password")
    
    available_models = []
    if api_key:
        available_models = get_available_models(api_key)
        if available_models:
            model_choice = st.selectbox("เลือกโมเดลที่ระบบของคุณรองรับ:", available_models)
            st.success(f"พบ {len(available_models)} โมเดลที่ใช้งานได้")
        else:
            st.error("ไม่พบโมเดลที่ใช้งานได้ หรือ API Key ผิดพลาด")
    
    st.divider()
    mode = st.radio("โหมดการทำงาน:", ["OpenCV (ปรับภาพ)", "AI Gemini (สร้างใหม่)"])

# --- ส่วนหลัก ---
st.title("🛡️ Ultimate QR AI Reconstructor")
st.write("ระบบจะดึงโมเดลที่รองรับจากบัญชีของคุณโดยอัตโนมัติ เพื่อป้องกันข้อผิดพลาด 404")

uploaded_file = st.file_uploader("อัปโหลด QR Code", type=["jpg", "jpeg", "png"])

if uploaded_file:
    input_image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ ต้นฉบับ")
        st.image(input_image, use_container_width=True)

    with col2:
        st.subheader("✨ ผลลัพธ์")
        
        if "OpenCV" in mode:
            img_array = np.array(input_image.convert('RGB'))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            _, final_img = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            st.image(final_img, use_container_width=True)
            
        else:
            if not api_key or not available_models:
                st.warning("⚠️ กรุณาใส่ API Key ให้ถูกต้องเพื่อดึงรายชื่อโมเดล")
            else:
                if st.button("🚀 รัน AI"):
                    try:
                        with st.spinner(f'กำลังประมวลผลด้วย {model_choice}...'):
                            # เรียกใช้โมเดลตามที่เลือกจากรายการที่ระบบตรวจพบ
                            model = genai.GenerativeModel(model_name=model_choice)
                            
                            prompt = "Identify the content of this QR code. Return only the URL or plain text."
                            response = model.generate_content([prompt, input_image])
                            
                            if response.text:
                                content = response.text.strip()
                                st.success(f"ถอดรหัสสำเร็จ: {content}")
                                
                                # สร้างใหม่
                                qr_new = qrcode.make(content)
                                st.image(qr_new, caption="AI Reconstructed", use_container_width=True)
                                
                                # ดาวน์โหลด
                                buf = io.BytesIO()
                                qr_new.save(buf, format="PNG")
                                st.download_button("📩 ดาวน์โหลด QR", buf.getvalue(), "ai_qr.png", "image/png")
                    except Exception as e:
                        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
                        st.info("หากยังติด 404 ให้ลองเลือกโมเดลอื่นในรายการด้านซ้ายมือครับ")
