import streamlit as st
import google.generativeai as genai

st.title("🔍 เครื่องมือสแกนหา AI Model (แก้ปัญหา Error 404)")

try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
    st.success("✅ ดึง API Key จาก Secrets สำเร็จ!")

    st.write("⏳ กำลังสแกนหารุ่น AI ที่กุญแจของคุณใช้งานได้...")
    
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    if available_models:
        st.success("🎉 เจอแล้ว! นี่คือรายชื่อรุ่นที่กุญแจของคุณใช้ได้จริง:")
        st.write(available_models)
        st.info("💡 รบกวนคุณครูถ่ายรูปหน้าจอนี้ส่งให้ผมดูหน่อยครับ!")
    else:
        st.error("🚨 ไม่พบรุ่นที่รองรับข้อความเลย (อาจต้องสร้าง API Key ใหม่แบบเปิดสิทธิ์ทั้งหมด)")
        
except Exception as e:
    st.error(f"🚨 ข้อผิดพลาดระบบ: {e}")
