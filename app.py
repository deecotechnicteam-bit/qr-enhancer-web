import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai
import qrcode

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="QR Code Clearer AI", page_icon="🪄", layout="wide")

st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🪄 QR Code Enhancer & AI Reconstructor")
st.write("เครื่องมือปรับความชัด QR Code ด้วย OpenCV และระบบ AI (Gemini) เพื่อสร้างใหม่ให้คมชัด 100%")

# --- ส่วน Sidebar สำหรับการตั้งค่า ---
with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    api_key = st.text_input("ใส่ Gemini API Key:", type="password", help="รับ Key ได้ที่ Google AI Studio")
    st.divider()
    mode = st.radio("เลือกโหมดการทำงาน:", 
                    ["ความละเอียดปกติ (OpenCV)", 
                     "ความละเอียดสูง (AI Gemini - สร้างใหม่)"])
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("API Key พร้อมใช้งาน")
        except Exception as e:
            st.error(f"Error: {e}")

# --- ส่วนอัปโหลดไฟล์ ---
uploaded_file = st.file_uploader("อัปโหลดรูปภาพ QR Code ที่เบลอ...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # อ่านรูปภาพต้นฉบับ
    input_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ รูปต้นฉบับ")
        st.image(input_image, use_container_width=True)

    with col2:
        st.subheader("✨ ผลลัพธ์")
        
        # --- กรณีเลือกโหมด OpenCV (ความละเอียดปกติ) ---
        if mode == "ความละเอียดปกติ (OpenCV)":
            # แปลงภาพเป็น OpenCV format
            img_array = np.array(input_image.convert('RGB'))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # ปรับปรุงภาพด้วย Thresholding
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            blur = cv2.GaussianBlur(resized, (3, 3), 0)
            _, final_img = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            st.image(final_img, caption="ปรับปรุงความชัดด้วย OpenCV", use_container_width=True)
            
            # เตรียมปุ่มดาวน์โหลด
            is_success, buffer = cv2.imencode(".png", final_img)
            if is_success:
                st.download_button("📩 ดาวน์โหลดภาพ (PNG)", buffer.tobytes(), "opencv_qr.png", "image/png")

        # --- กรณีเลือกโหมด Gemini (ความละเอียดสูง) ---
        else:
            if not api_key:
                st.warning("⚠️ กรุณากรอก API Key ในแถบด้านซ้ายเพื่อใช้งานโหมด AI")
            else:
                if st.button("🚀 เริ่มการวิเคราะห์ด้วย AI"):
                    try:
                        with st.spinner('AI กำลังอ่านข้อมูลจาก QR Code...'):
                            # ใช้โมเดล gemini-1.5-flash
                            model = genai.GenerativeModel('models/gemini-1.5-flash')
                            
                            # Prompt ให้ AI สกัดข้อมูล
                            prompt = "This image is a blurry QR code. What is the URL or text encoded in this QR? Return only the text/link."
                            response = model.generate_content([prompt, input_image])
                            extracted_data = response.text.strip()
                            
                            if extracted_data:
                                st.info(f"ข้อมูลที่พบ: {extracted_data}")
                                
                                # สร้าง QR Code ใหม่จากข้อมูลที่ได้
                                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                                qr.add_data(extracted_data)
                                qr.make(fit=True)
                                new_qr_img = qr.make_image(fill_color="black", back_color="white")
                                
                                # แสดงผลรูปใหม่
                                st.image(new_qr_img.get_image(), caption="AI Reconstructed (ชัด 100%)", use_container_width=True)
                                
                                # เตรียมปุ่มดาวน์โหลด
                                buf = io.BytesIO()
                                new_qr_img.save(buf)
                                st.download_button("📩 ดาวน์โหลด QR แบบคมชัดสูง", buf.getvalue(), "ai_reconstructed_qr.png", "image/png")
                            else:
                                st.error("AI ไม่สามารถอ่านข้อมูลได้ กรุณาลองใช้รูปที่ชัดกว่านี้")
                                
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

st.divider()
st.caption("พัฒนาโดย AI Collaborator | รองรับการทำงานผ่าน Streamlit Cloud")
