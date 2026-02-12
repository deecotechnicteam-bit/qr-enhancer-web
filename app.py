import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai
import qrcode

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Auto QR AI Reconstructor", page_icon="🪄", layout="wide")

# --- ฟังก์ชันอัจฉริยะสำหรับเลือกโมเดลอัตโนมัติ ---
def get_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # ลำดับความสำคัญของโมเดล (Priority List)
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']
        
        for p in priority:
            if p in available:
                return p
        return available[0] if available else None
    except:
        return None

# --- ส่วน Sidebar ---
with st.sidebar:
    st.header("🔑 API Access")
    api_key = st.text_input("ใส่ Gemini API Key:", type="password")
    
    st.divider()
    st.header("⚙️ โหมดการทำงาน")
    mode = st.radio("เลือกความละเอียด:", ["ระดับปกติ (OpenCV)", "ระดับสูง (AI Auto-Select)"])
    
    if api_key:
        auto_model = get_best_model(api_key)
        if auto_model:
            st.success(f"ระบบพร้อมใช้โมเดล: {auto_model.split('/')[-1]}")
        else:
            st.error("ไม่พบโมเดลที่รองรับในบัญชีนี้")

# --- ส่วนแสดงผลหลัก ---
st.title("🪄 Auto QR Code AI Reconstructor")
st.write("อัปโหลด QR Code ที่มีปัญหา ระบบ AI จะวิเคราะห์และสร้างใหม่ให้คมชัดโดยอัตโนมัติ")

uploaded_file = st.file_uploader("เลือกไฟล์ภาพ...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    input_image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ ต้นฉบับ")
        st.image(input_image, use_container_width=True)

    with col2:
        st.subheader("✨ ผลลัพธ์")
        
        if mode == "ระดับปกติ (OpenCV)":
            # การประมวลผล OpenCV
            img_array = np.array(input_image.convert('RGB'))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            _, final = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            st.image(final, caption="Enhanced by OpenCV", use_container_width=True)
            
            # Download
            is_success, buffer = cv2.imencode(".png", final)
            st.download_button("📩 ดาวน์โหลดรูปภาพ", buffer.tobytes(), "opencv_qr.png", "image/png")

        else:
            # โหมด AI แบบ Auto
            if not api_key or not auto_model:
                st.warning("⚠️ กรุณากรอก API Key เพื่อเปิดใช้งานโหมด AI")
            else:
                if st.button("🚀 เริ่มการทำงาน AI"):
                    try:
                        with st.spinner(f'AI ({auto_model.split("/")[-1]}) กำลังทำงาน...'):
                            model = genai.GenerativeModel(auto_model)
                            prompt = "Identify the data in this QR code. Return ONLY the URL or text. No chatter."
                            response = model.generate_content([prompt, input_image])
                            
                            qr_content = response.text.strip()
                            
                            if qr_content:
                                st.info(f"ถอดรหัสข้อมูลได้: {qr_content}")
                                # สร้างใหม่
                                qr_new = qrcode.make(qr_content)
                                st.image(qr_new, caption="AI Reconstructed (ชัด 100%)", use_container_width=True)
                                
                                # Download
                                buf = io.BytesIO()
                                qr_new.save(buf, format="PNG")
                                st.download_button("📩 ดาวน์โหลด QR แบบคมชัด", buf.getvalue(), "ai_qr.png", "image/png")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
