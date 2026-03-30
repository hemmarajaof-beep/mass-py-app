import streamlit as st
import google.generativeai as genai

# --- ใส่รหัส API KEY ของคุณครูตรงนี้ ---
API_KEY = "AIzaSyBvpP_kLWH1iW6D5GTahf8CqYVdZK3l7W8"

st.title("🔍 เครื่องมือสแกนสมองกล Google AI")

try:
    genai.configure(api_key=API_KEY)
    st.info("กำลังตรวจสอบรายชื่อ AI ที่กุญแจของคุณครูสามารถเข้าถึงได้...")
    
    working_models = []
    # สั่งให้วิ่งไปค้นหารายชื่อ AI ทั้งหมดที่ Google อนุญาต
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            working_models.append(m.name)
            
    if working_models:
        st.success("🎉 สแกนสำเร็จ! นี่คือชื่อรุ่น AI ที่คุณครูใช้งานได้ครับ:")
        for name in working_models:
            st.code(name)
        st.markdown("---")
        st.markdown("**(👉 รบกวนคุณครูแคปหน้าจอนี้ หรือก๊อปปี้ชื่อที่อยู่ในกรอบสีเทามาบอกผมหน่อยนะครับ เราจะได้เอาชื่อที่ถูกต้อง 100% ไปใส่ในแอปหลักกันครับ!)**")
    else:
        st.error("❌ ไม่พบรุ่นที่รองรับการพิมพ์โต้ตอบเลยครับ")
        
except Exception as e:
    st.error("🚨 สแกนล้มเหลว ตรวจสอบพบ Error ดังนี้:")
    st.write(e)
