import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="MASS-Py Workspace")

# --- 1. ใส่รหัส API KEY ของคุณครูตรงนี้ ---
API_KEY = "AIzaSyBvpP_kLWH1iW6D5GTahf8CqYVdZK3l7W8นี้" 

genai.configure(api_key=API_KEY)

# --- 2. ระบบสแกนหา AI ที่ใช้งานได้อัตโนมัติ (ไม้ตาย!) ---
def get_working_model():
    try:
        # ให้ระบบวิ่งไปเช็คว่า API นี้ใช้โมเดลชื่ออะไรได้บ้าง
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception as e:
        pass
    # ถ้าหาไม่เจอจริงๆ จะบังคับใช้รุ่นล่าสุด
    return genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 MASS-Py: Mission Control")

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
                    # ดึงเอา AI ตัวที่พร้อมใช้งานมาตอบ
                    model = get_working_model()
                    response = model.generate_content(system_prompt + "\nคำถามจากนักเรียน: " + user_input)
                    st.success(response.text)
                except Exception as e:
                    st.error("🚨 ระบบ API ขัดข้อง กรุณาเช็คว่าใส่ API KEY ถูกต้องและไม่มีเว้นวรรคส่วนเกิน")
                    st.warning(f"รายละเอียดเชิงลึก: {e}")
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
