import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="MASS-Py Workspace")

# --- จุดที่ 1: วาง API KEY ของคุณครูในเครื่องหมายคำพูดด้านล่างนี้ ---
API_KEY = "AIzaSyBvpP_kLWH1iW6D5GTahf8CqYVdZK3l7W8" 

# เชื่อมต่อระบบ AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 MASS-Py: Mission Control (Python & AI Agents)")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.subheader("🤖 เรียกใช้ AI Agents")
    agent = st.selectbox("เลือกบัดดี้ของคุณ:", ["1. สถาปนิกตรรกะ (ช่วยวางแผน)", "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", "3. สารวัตรนักสืบ (ช่วยแก้ Error)"])
    
    if "1" in agent:
        system_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนตรรกะ Python ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อเขียน Pseudocode"
    elif "2" in agent:
        system_prompt = "คุณคือบัดดี้เขียนโค้ด ช่วยเด็ก ม.3 เขียน Python ห้ามพิมพ์ Code Block ยาวๆ ให้บอกใบ้โครงสร้าง"
    else:
        system_prompt = "คุณคือสารวัตรนักสืบ ช่วยเด็กวิเคราะห์ Error ห้ามแก้โค้ดให้ แต่ให้บอกใบ้ 3 ข้อว่าควรไปเช็คตรงไหน"

    user_input = st.text_area("พิมพ์ปรึกษาบัดดี้ที่นี่:", height=150)
    
    if st.button("ส่งข้อความ"):
        if user_input:
            with st.spinner("บัดดี้กำลังคิด..."):
                try:
                    # พยายามเรียก AI
                    response = model.generate_content(system_prompt + "\nคำถามจากนักเรียน: " + user_input)
                    st.success(response.text)
                except Exception as e:
                    # ถ้าพัง จะแจ้งเตือนตรงนี้แทนจอแดงๆ
                    st.error("🚨 เกิดปัญหาการเชื่อมต่อกับ Google AI")
                    st.warning(f"สาเหตุ: {e}")
                    st.info("💡 ข้อแนะนำ: กรุณากลับไปเช็คว่าใส่ API_KEY ในไฟล์ app.py ถูกต้องครบถ้วนหรือไม่")
        else:
            st.warning("กรุณาพิมพ์ข้อความก่อนครับ!")

with col2:
    st.subheader("💻 พื้นที่ปฏิบัติการ (Coding Zone)")
    st.info("💡 เปิด Google Colab เพื่อเขียนโค้ด แล้วใช้ฟีเจอร์แบ่งครึ่งหน้าจอ (Split Screen) เพื่อคุยกับ AI ฝั่งซ้ายไปพร้อมๆ กัน")
    st.link_button("➡️ คลิกเปิด Google Colab สำหรับโจทย์วันนี้", "https://colab.research.google.com/")
    
    st.markdown("---")
    st.markdown("### 📝 คู่มือการถาม AI (Prompt Cheat Sheet)")
    st.markdown("- **สถาปนิก:** 'ช่วยออกแบบตรรกะโปรแกรมตัดเกรดให้หน่อย เริ่มยังไงดี?'")
    st.markdown("- **บัดดี้:** 'คำสั่งที่รับข้อมูลทางคีย์บอร์ดเขียนยังไงนะ ขอคำใบ้หน่อย'")
    st.markdown("- **นักสืบ:** 'รันแล้วขึ้น SyntaxError บรรทัดที่ 4 เกิดจากอะไร?'")
