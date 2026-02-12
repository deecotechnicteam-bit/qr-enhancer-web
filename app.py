import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="QR Code Enhancer", layout="centered")

st.title("📷 QR Code Enhancer")
st.write("อัปโหลดรูป QR Code ที่เบลอ เพื่อปรับให้คมชัดและดาวน์โหลดไปใช้งาน")

# ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("เลือกรูปภาพ QR Code...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # แปลงไฟล์ที่อัปโหลดเป็น OpenCV Format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # แสดงรูปต้นฉบับ
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="รูปต้นฉบับ", use_container_width=True)

    # --- กระบวนการปรับปรุงรูปภาพ ---
    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Resize ให้ใหญ่ขึ้น (Interpolation)
    scale_percent = 200
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LANCZOS4)
    
    # 3. Denoising & Thresholding
    blur = cv2.GaussianBlur(resized, (3, 3), 0)
    _, final_img = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # แสดงรูปที่ปรับปรุงแล้ว
    with col2:
        st.image(final_img, caption="รูปที่ปรับปรุงแล้ว", use_container_width=True)

    # --- ส่วนการดาวน์โหลด ---
    # แปลง OpenCV image กลับเป็น format ที่ดาวน์โหลดได้
    is_success, buffer = cv2.imencode(".png", final_img)
    if is_success:
        io_buf = io.BytesIO(buffer)
        st.download_button(
            label="📩 ดาวน์โหลดรูปภาพที่ปรับชัดแล้ว",
            data=io_buf,
            file_name="enhanced_qrcode.png",
            mime="image/png"
        )

st.divider()
st.info("คำแนะนำ: หากรูปต้นฉบับเอียงมากเกินไป หรือขาดหายบางส่วน ระบบอาจจะยังสแกนไม่ได้")