import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(layout="wide", page_title="MASS-Py Workspace")

# --- 2. ดึงกุญแจ API อย่างปลอดภัยจากตู้เซฟ (Secrets) ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("🚨 ไม่พบกุญแจ API กรุณาตรวจสอบ Streamlit Secrets ในหลังบ้าน")
    st.stop()

# --- 3. ฟังก์ชันสแกนหา AI รุ่นที่ใช้งานได้อัตโนมัติ ---
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        pass
    return genai.GenerativeModel('gemini-1.5-flash')

# --- ส่วนหัวของเว็บ ---
st.title("🚀 MASS-Py: Mission Control")

# แบ่งหน้าจอ ซ้าย (40%) : ขวา (60%)
col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: ผู้ช่วย AI (Agents & Chat) =================
with col1:
    st.subheader("🤖 เรียกใช้ AI Agents")
    
    # เมนูเลือกบัดดี้
    agent = st.selectbox("เลือกบัดดี้ของคุณ:", [
        "1. สถาปนิกตรรกะ (ช่วยวางแผน)", 
        "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", 
        "3. สารวัตรนักสืบ (ช่วยแก้ Error)"
    ])
    
    # กำหนดนิสัย AI (System Prompt) ตามที่เด็กเลือก
    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนตรรกะ Python ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อเขียน Pseudocode"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด ช่วยเด็ก ม.3 เขียน Python ห้ามพิมพ์ Code Block ยาวๆ ให้บอกใบ้โครงสร้าง"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยเด็กวิเคราะห์ Error ห้ามแก้โค้ดให้ แต่ให้บอกใบ้ 3 ข้อว่าควรไปเช็คตรงไหน"

    # ระบบความจำ (ถ้าเปลี่ยนบัดดี้ ให้ล้างสมองเริ่มคุยใหม่)
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        st.session_state.messages = [] # ล้างประวัติแชท
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[]) # เริ่มห้องแชทใหม่

    # แสดงประวัติการแชทเก่าๆ บนหน้าจอ
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # กล่องพิมพ์ข้อความแชท (จะอยู่ด้านล่างสุดของคอลัมน์ซ้าย)
    if prompt := st.chat_input("พิมพ์ปรึกษาบัดดี้ที่นี่..."):
        # แสดงข้อความที่เด็กพิมพ์
        with st.chat_message("user"):
            st.markdown(prompt)
        # จำสิ่งที่เด็กพิมพ์
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # ให้ AI คิดและตอบกลับ
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                # แอบแนบกฎเหล็กไปกับคำถามเด็กเสมอ
                full_prompt = f"[คำสั่งบังคับ: {sys_prompt}]\nคำถามของนักเรียน: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt)
                
                # แสดงคำตอบ AI
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                # จำสิ่งที่ AI ตอบ
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("🚨 เกิดข้อผิดพลาดในการประมวลผล")
                st.warning(str(e))

# ================= ฝั่งขวา: ภารกิจการเรียนรู้ (Missions & Workspace) =================
with col2:
    st.subheader("🎯 ภารกิจการเรียนรู้ (Learning Roadmap)")
    
    # เมนูเลือกภารกิจ (ครอบคลุมทั้งหน่วยการเรียนรู้)
    mission = st.radio("เลือกภารกิจประจำสัปดาห์:",
        ["EP.1: 🤖 ตู้สั่งน้ำอัจฉริยะ (การรับค่า & แสดงผล)",
         "EP.2: 🏥 คลินิก AI ประเมินสุขภาพ (เงื่อนไข If-Else)",
         "EP.3: 🔒 ระบบรักษาความปลอดภัย (การวนซ้ำ While Loop)",
         "EP.4: 🛒 ตะกร้าสินค้าออนไลน์ (ข้อมูลแบบ List)",
         "EP.5: 🚀 โครงงานนวัตกรรมแก้ปัญหาโรงเรียน (Final Project)"]
    )
    
    st.markdown("---")
    st.subheader("💻 พื้นที่ปฏิบัติการ (Coding Zone)")
    st.info("💡 คลิกปุ่มด้านล่างเพื่อเปิด Programiz แล้วจัดหน้าจอแบบแบ่งครึ่ง (Split Screen) ขนานกับหน้าต่างนี้")
    
    # ปุ่มเปิด Programiz
    st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz Online Compiler)", "https://www.programiz.com/python-programming/online-compiler/")
    
    st.markdown("---")
    
    # แสดงรายละเอียดโจทย์และคำใบ้ตามภารกิจที่เลือก
    if "EP.1" in mission:
        st.success("**🎯 เป้าหมาย EP.1:**\nเรียนรู้พื้นฐานตัวแปร ให้นักเรียนเขียนโปรแกรมรับชื่อลูกค้า รับเมนูที่สั่ง และคำนวณเงินทอน")
        st.caption("💡 คำใบ้: ลองทักไปหา '1. สถาปนิกตรรกะ' ฝั่งซ้าย แล้วบอกว่า 'อยากเขียนโปรแกรมคิดเงินทอน เริ่มยังไงดี?'")
    elif "EP.2" in mission:
        st.success("**🎯 เป้าหมาย EP.2:**\nเรียนรู้การตัดสินใจ รับค่าน้ำหนัก ส่วนสูง คำนวณค่า BMI และแสดงผลลัพธ์ว่า อ้วน, ผอม, หรือ ปกติ")
        st.caption("💡 คำใบ้: ภารกิจนี้ใช้เงื่อนไข (If-Else) ถ้าพิมพ์โค้ดแล้ว Error ให้รีบไปหา '3. สารวัตรนักสืบ' เลย!")
    elif "EP.3" in mission:
        st.success("**🎯 เป้าหมาย EP.3:**\nเรียนรู้การทำซ้ำ สร้างระบบจำลองการใส่รหัสผ่านตู้เซฟ ถ้าใส่ผิดให้โปรแกรมวนลูปถามใหม่จนกว่าจะถูก")
        st.caption("💡 คำใบ้: ภารกิจนี้ใช้ While Loop ถ้าจำคำสั่งไม่ได้ ลองถาม '2. บัดดี้เขียนโค้ด' ดูนะ!")
    elif "EP.4" in mission:
        st.success("**🎯 เป้าหมาย EP.4:**\nเรียนรู้เรื่อง List สร้างโปรแกรมเก็บรายชื่อสินค้าในตะกร้า และให้ผู้ใช้เพิ่ม/ลบสินค้าได้")
        st.caption("💡 คำใบ้: ภารกิจนี้ซับซ้อนขึ้น ให้เริ่มวางแผนตรรกะทีละข้อกับสถาปนิกก่อนลงมือเขียนโค้ด")
    elif "EP.5" in mission:
        st.info("**🏆 เป้าหมายสูงสุด (Final Project):**\nให้นักเรียนบูรณาการความรู้ทั้งหมด สร้างโปรแกรมเพื่อแก้ปัญหาในชีวิตประจำวัน 1 อย่าง")
        st.caption("💡 คำใบ้: นี่คือภารกิจอิสระ! ใช้ความรู้จาก EP.1-4 มาสร้างสรรค์ผลงานของตัวเองได้เลย")
