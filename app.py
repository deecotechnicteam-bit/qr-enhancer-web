import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai
import qrcode

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="QR Code AI Sharpener", page_icon="🪄", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🪄 QR Code AI Enhancer")
st.write("เลือกโหมดปรับความชัดเพื่อคืนค่า QR Code ที่เบลอให้กลับมาใช้งานได้")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("ใส่ Gemini API Key:", type="password")
    st.divider()
    mode = st.radio("เลือกความละเอียด:", 
                    ["ระดับปกติ (OpenCV - ปรับภาพ)", 
                     "ระดับสูง (AI Gemini - สร้างภาพใหม่)"])
    
    if api_key:
        genai.configure(api_key=api_key)

# --- ส่วนอัปโหลดไฟล์ ---
uploaded_file = st.file_uploader("อัปโหลด QR Code (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # อ่านรูปภาพ
    input_image = Image.open(uploaded_file)
    img_array = np.array(input_image.convert('RGB'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ ต้นฉบับ")
        st.image(input_image, use_container_width=True)

    with col2:
        st.subheader("✨ ผลลัพธ์")
        
        # --- โหมด OpenCV ---
        if "OpenCV" in mode:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            # ขยายภาพและทำ Threshold
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            _, final_img = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            st.image(final_img, caption="ปรับความชัดด้วย OpenCV", use_container_width=True)
            
            # ปุ่มดาวน์โหลด
            is_success, buffer = cv2.imencode(".png", final_img)
            if is_success:
                st.download_button("📩 ดาวน์โหลดภาพปกติ", buffer.tobytes(), "clear_qr.png", "image/png")

        # --- โหมด AI Gemini ---
        else:
            if not api_key:
                st.warning("⚠️ กรุณาใส่ API Key ที่ฝั่งซ้าย")
            else:
                if st.button("🚀 ประมวลผลด้วย AI"):
                    try:
                        with st.spinner('AI กำลังวิเคราะห์โครงสร้างภาพ...'):
                            # แก้ไขจุดนี้: ใช้ชื่อโมเดลแบบไม่มี models/ นำหน้า เพื่อเลี่ยง Error 404
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            prompt = "Extract the text or URL from this QR code image. Return only the text content."
                            response = model.generate_content([prompt, input_image])
                            
                            qr_data = response.text.strip()
                            
                            if qr_data:
                                st.info(f"ข้อมูลที่อ่านได้: {qr_data}")
                                
                                # สร้าง QR Code ใหม่ (High Definition)
                                new_qr = qrcode.make(qr_data)
                                st.image(new_qr, caption="สร้างใหม่ด้วย AI (ชัด 100%)", use_container_width=True)
                                
                                # เตรียมปุ่มดาวน์โหลด
                                buf = io.BytesIO()
                                new_qr.save(buf, format="PNG")
                                st.download_button("📩 ดาวน์โหลดภาพความละเอียดสูง", buf.getvalue(), "ai_qr.png", "image/png")
                            else:
                                st.error("AI ไม่สามารถถอดรหัสภาพนี้ได้")
                                
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
                        st.info("หากพบ Error 404 ให้ตรวจสอบว่า API Key ของคุณมีสิทธิ์เข้าถึง gemini-1.5-flash หรือยัง")

st.divider()
st.caption("Tip: โหมดความละเอียดสูงจะใช้ AI อ่านข้อมูลแล้ววาด QR ขึ้นมาใหม่ ซึ่งจะได้ความชัดสูงสุด")
