import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="MASS-Py Workspace")

# --- 1. ดึงกุญแจ API อย่างปลอดภัย ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("🚨 ไม่พบกุญแจ API กรุณาตรวจสอบ Streamlit Secrets")
    st.stop()

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        pass
    return genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 MASS-Py: Mission Control")

col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI แชท =================
with col1:
    st.subheader("🤖 เรียกใช้ AI Agents")
    
    agent = st.selectbox("เลือกบัดดี้ของคุณ:", ["1. สถาปนิกตรรกะ (ช่วยวางแผน)", "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", "3. สารวัตรนักสืบ (ช่วยแก้ Error)"])
    
    # ระบบความจำและล้างสมองเมื่อเปลี่ยนบัดดี้
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        st.session_state.messages = []
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[])

    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนตรรกะ Python ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อเขียน Pseudocode"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด ช่วยเด็ก ม.3 เขียน Python ห้ามพิมพ์ Code Block ยาวๆ ให้บอกใบ้โครงสร้าง"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยเด็กวิเคราะห์ Error ห้ามแก้โค้ดให้ แต่ให้บอกใบ้ 3 ข้อว่าควรไปเช็คตรงไหน"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("พิมพ์ปรึกษาบัดดี้ที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                full_prompt = f"[คำสั่งบังคับ: {sys_prompt}]\nคำถามของนักเรียน: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("🚨 เกิดข้อผิดพลาดในการประมวลผล")

# ================= ฝั่งขวา: ภารกิจและ Programiz =================
with col2:
    st.subheader("🎯 ภารกิจการเรียนรู้ (Missions)")
    
   # เมนูเลือกภารกิจ (ครอบคลุมทั้งหน่วยการเรียนรู้)
    mission = st.radio("เลือกภารกิจประจำสัปดาห์:",
        ["EP.1: 🤖 ตู้สั่งน้ำอัจฉริยะ (การรับค่า & แสดงผล Input/Output)",
         "EP.2: 🏥 คลินิก AI ประเมินสุขภาพ (เงื่อนไข If-Else)",
         "EP.3: 🔒 ระบบรักษาความปลอดภัย (การวนซ้ำ While Loop)",
         "EP.4: 🛒 ตะกร้าสินค้าออนไลน์ (โครงสร้างข้อมูล List/Array)",
         "EP.5: 🚀 โครงงานนวัตกรรมแก้ปัญหาโรงเรียน (Final Project)"]
    )
    
    st.markdown("---")
    
    # แสดงรายละเอียดโจทย์ตามภารกิจที่เลือก
    if "EP.1" in mission:
        st.success("**🎯 เป้าหมาย EP.1:**\nเรียนรู้พื้นฐานตัวแปร ให้นักเรียนเขียนโปรแกรมรับชื่อลูกค้า รับเมนูที่สั่ง และคำนวณเงินทอน")
    elif "EP.2" in mission:
        st.success("**🎯 เป้าหมาย EP.2:**\nเรียนรู้การตัดสินใจ รับค่าน้ำหนัก ส่วนสูง คำนวณค่า BMI และแสดงผลลัพธ์ว่า อ้วน, ผอม, หรือ ปกติ")
    elif "EP.3" in mission:
        st.success("**🎯 เป้าหมาย EP.3:**\nเรียนรู้การทำซ้ำ สร้างระบบจำลองการใส่รหัสผ่านตู้เซฟ ถ้าใส่ผิดให้โปรแกรมวนลูปถามใหม่จนกว่าจะถูก")
    elif "EP.4" in mission:
        st.success("**🎯 เป้าหมาย EP.4:**\nเรียนรู้เรื่อง List สร้างโปรแกรมเก็บรายชื่อสินค้าในตะกร้า และให้ผู้ใช้สามารถเพิ่ม/ลบสินค้าได้")
    elif "EP.5" in mission:
        st.info("**🏆 เป้าหมายสูงสุด (Final Project):**\nให้นักเรียนบูรณาการความรู้ทั้งหมด สร้างโปรแกรมเพื่อแก้ปัญหาในชีวิตประจำวัน 1 อย่าง (อิสระ)")
