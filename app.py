import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import google.generativeai as genai
import qrcode

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Universal QR AI", page_icon="🔍", layout="wide")

# --- Sidebar สำหรับการตั้งค่าโมเดล ---
with st.sidebar:
    st.header("⚙️ API Configuration")
    api_key = st.text_input("ใส่ Gemini API Key:", type="password")
    
    # เพิ่มตัวเลือก Model ชื่อต่างๆ เผื่อกรณี 404
    model_choice = st.selectbox(
        "เลือก AI Model (หาก 404 ให้ลองเปลี่ยน):",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro-vision-latest", "gemini-pro-vision"]
    )
    
    st.divider()
    mode = st.radio("โหมดการทำงาน:", ["OpenCV (ปรับภาพ)", "AI Gemini (อ่านแล้วสร้างใหม่)"])

# --- ฟังก์ชันสำหรับเรียกใช้งาน AI แบบยืดหยุ่น ---
def call_gemini_ai(api_key, model_name, image):
    genai.configure(api_key=api_key)
    # พยายามเรียกใช้ Model ที่เลือก
    model = genai.GenerativeModel(model_name)
    prompt = "Extract the text or URL from this QR code image. Return ONLY the text content. If you cannot see it, say 'Error'."
    response = model.generate_content([prompt, image])
    return response.text.strip()

# --- ส่วนแสดงผลหลัก ---
st.title("🔍 Universal QR Code Enhancer")

uploaded_file = st.file_uploader("อัปโหลด QR Code", type=["jpg", "jpeg", "png"])

if uploaded_file:
    input_image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ รูปต้นฉบับ")
        st.image(input_image, use_container_width=True)

    with col2:
        st.subheader("✨ ผลลัพธ์")
        
        if "OpenCV" in mode:
            # การประมวลผลพื้นฐาน (ไม่ต้องใช้ API Key)
            img_array = np.array(input_image.convert('RGB'))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            _, final_img = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            st.image(final_img, caption="Processed by OpenCV", use_container_width=True)
            
        else:
            if not api_key:
                st.warning("⚠️ กรุณาใส่ API Key ใน Sidebar")
            else:
                if st.button("🚀 รัน AI (Reconstruct)"):
                    try:
                        with st.spinner(f'กำลังใช้โมเดล {model_choice} วิเคราะห์...'):
                            result_text = call_gemini_ai(api_key, model_choice, input_image)
                            
                            if result_text and result_text.lower() != "error":
                                st.success(f"อ่านข้อมูลได้: {result_text}")
                                # สร้างใหม่ให้คมชัด
                                new_qr = qrcode.make(result_text)
                                st.image(new_qr, caption="AI Generated (Clear 100%)", use_container_width=True)
                                
                                # ปุ่มดาวน์โหลด
                                buf = io.BytesIO()
                                new_qr.save(buf, format="PNG")
                                st.download_button("📩 ดาวน์โหลด QR ใหม่", buf.getvalue(), "ai_qr.png", "image/png")
                            else:
                                st.error("AI อ่านรหัสนี้ไม่ได้ หรือโมเดลไม่รองรับการวิเคราะห์ภาพ")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 คำแนะนำ: หากเจอ 404 ให้ลองเปลี่ยนชื่อ Model ใน Sidebar เป็นตัวอื่นครับ")

st.divider()
st.caption("Universal QR AI - รองรับการสลับโมเดลเพื่อเลี่ยงปัญหา API Restriction")
