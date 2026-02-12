import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI QR Enhancer", page_icon="🪄")

# ส่วนตั้งค่า API Key (ใส่ใน Streamlit Secrets หรือกรอกหน้าเว็บ)
api_key = st.sidebar.text_input("AIzaSyDJCEUbO_4SaSwnrOdF88MtHNZ3YxM6aUs", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🪄 AI QR Code Enhancer")
st.write("เลือกโหมดการปรับความชัดด้วย OpenCV หรือ AI (Gemini)")

mode = st.radio("เลือกความละเอียด/วิธีการประมวลผล:", 
                ["ความละเอียดต่ำ (เน้นเร็ว - OpenCV)", 
                 "ความละเอียดสูง (เน้นชัด - AI Gemini)"])

uploaded_file = st.file_uploader("อัปโหลด QR Code", type=['png', 'jpg', 'jpeg'])

def process_opencv(img):
    # ใช้เทคนิคเดิมที่เร็วและประหยัด Resource
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
    _, final = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return final

async def process_gemini(pil_img):
    # ส่งภาพให้ Gemini วิเคราะห์และ Generate ภาพใหม่หรือลบ Noise
    prompt = "This is a blurry QR code. Please reconstruct it to be a clean, high-contrast black and white QR code image. Remove all noise and artifacts."
    response = model.generate_content([prompt, pil_img])
    # หมายเหตุ: ปัจจุบัน Gemini ส่งกลับเป็น Text/Description 
    # หากต้องการทำ Image-to-Image แท้ๆ ต้องใช้ Imagen 
    # แต่เราสามารถใช้ Gemini ช่วยวิเคราะห์ 'Data' ใน QR ได้
    return None # (ดูคำอธิบายด้านล่าง)

if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))
    
    col1, col2 = st.columns(2)
    col1.image(image, caption="ต้นฉบับ", use_container_width=True)

    if st.button("เริ่มการปรับปรุง"):
        if "OpenCV" in mode:
            with st.spinner('กำลังประมวลผล...'):
                result = process_opencv(img_array)
                col2.image(result, caption="ผลลัพธ์ (OpenCV)", use_container_width=True)
                
                # ปุ่มดาวน์โหลด
                is_success, buffer = cv2.imencode(".png", result)
                st.download_button("📩 ดาวน์โหลดภาพ", buffer.tobytes(), "clear_qr.png", "image/png")
        
        elif "Gemini" in mode:
            if not api_key:
                st.warning("กรุณาใส่ API Key ในแถบด้านซ้ายก่อนครับ")
            else:
                st.info("โหมด AI กำลังวิเคราะห์โครงสร้างภาพ...")
                # ในทางปฏิบัติ Gemini Vision จะเด่นเรื่องการ 'อ่าน' (Extract Data) 
                # มากกว่าการทำ Image Upscaling ตรงๆ
                st.write("🤖 AI วิเคราะห์ข้อมูลจาก QR นี้ได้ว่า: ")
                response = model.generate_content(["What is the content/URL of this QR code?", image])
                st.success(response.text)
                st.caption("เคล็ดลับ: เมื่อได้ URL แล้ว คุณสามารถนำไปสร้าง QR ใหม่ที่ชัด 100% ได้ทันที")

