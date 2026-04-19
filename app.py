import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(layout="wide", page_title="MASS-Py: Smart LMS Workspace")

# --- 2. ระบบเชื่อมต่อ AI (ใช้รุ่น 2.5-flash ตามกุญแจ API) ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets กรุณาตรวจสอบการตั้งค่าหลังบ้าน")
    st.stop()

def get_working_model():
    # ใช้รุ่นที่กุญแจคุณครูมีสิทธิ์เข้าถึง (gemini-2.5-flash)
    return genai.GenerativeModel('gemini-2.5-flash')

# --- 3. ระบบจัดการสถานะผู้เรียน (Session State) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_no" not in st.session_state:
    st.session_state.user_no = ""
if "progress" not in st.session_state:
    st.session_state.progress = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. ส่วนการระบุตัวตน (Login) ---
if not st.session_state.user_name:
    st.title("🚀 ยินดีต้อนรับสู่ MASS-Py")
    st.subheader("กรุณาระบุข้อมูลนักเรียนเพื่อเริ่มบทเรียน")
    
    with st.container(border=True):
        name = st.text_input("ชื่อ-นามสกุล:")
        no = st.text_input("เลขที่:")
        room = st.selectbox("ห้องเรียน:", ["ม.3/1", "ม.3/2", "ม.3/3", "ม.3/4"])
        
        if st.button("เข้าสู่ห้องเรียน", use_container_width=True):
            if name and no:
                st.session_state.user_name = name
                st.session_state.user_no = no
                st.session_state.user_room = room
                st.rerun()
            else:
                st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
    st.stop()

# --- 5. โครงสร้างหน้าจอหลัก ---
with st.sidebar:
    st.title("👤 โปรไฟล์นักเรียน")
    st.info(f"**ชื่อ:** {st.session_state.user_name}\n\n**เลขที่:** {st.session_state.user_no} | **ห้อง:** {st.session_state.user_room}")
    
    st.divider()
    
    # คำนวณความก้าวหน้า
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed) / len(missions_list)
    
    st.subheader("📊 ความก้าวหน้า")
    st.progress(progress_val)
    st.write(f"สำเร็จแล้ว {len(completed)} จาก 5 ภารกิจ")
    
    if st.button("ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI Buddies (Chat) =================
with col1:
    st.subheader("🤖 เลือก AI บัดดี้ของคุณ")
    agent = st.selectbox("เปลี่ยนบทบาท AI:", [
        "1. สถาปนิกตรรกะ (เน้นวางแผน)", 
        "2. บัดดี้เขียนโค้ด (เน้นไวยากรณ์)", 
        "3. สารวัตรนักสืบ (เน้นแก้ Error)"
    ])
    
    # กำหนด System Prompt
    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนโปรแกรม ห้ามให้โค้ด ให้ถามนำเพื่อให้เด็กคิดเอง"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด สอนไวยากรณ์ Python สั้นๆ ห้ามพิมพ์ Code Block ยาว"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยแก้ Error โดยบอกใบ้จุดที่ผิด 3 จุด ห้ามแก้โค้ดให้ทันที"

    # จัดการประวัติการคุย
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("ปรึกษา AI ที่นี่..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                full_query = f"[Role: {sys_prompt}]\nStudent Query: {prompt}"
                response = st.session_state.chat_session.send_message(full_query)
                with st.chat_message("assistant"): st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("🚨 การเชื่อมต่อขัดข้อง")
                st.warning("กรุณาลองใหม่อีกครั้ง หรือตรวจสอบ API Key")

# ================= ฝั่งขวา: บทเรียน & ระบบส่งงาน =================
with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจเรียนรู้", "📤 ส่งหลักฐาน", "🔐 Teacher Mode"])
    
    with tab1:
        st.subheader("🎯 ค้นหาภารกิจ")
        m_choice = st.radio("เลือก EP:", missions_list, horizontal=True)
        st.divider()
        if "EP.1" in m_choice:
            st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ**\nโจทย์: เขียนโปรแกรมรับชื่อลูกค้า รับเมนูน้ำ และแสดงเงินทอน")
        elif "EP.2" in m_choice:
            st.success("**EP.2: คลินิก AI ประเมินสุขภาพ**\nโจทย์: รับค่าน้ำหนัก ส่วนสูง เพื่อคำนวณและแสดงค่า BMI")
        # (เพิ่มโจทย์ EP.3-5 ได้ตามต้องการ)
        
        st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz)", "https://www.programiz.com/python-programming/online-compiler/")
        
        if st.button(f"✅ บันทึกว่าทำ {m_choice} สำเร็จแล้ว"):
            st.session_state.progress[m_choice] = True
            st.toast("บันทึกความก้าวหน้าสำเร็จ!")
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งงานเพื่อบันทึกข้อมูล")
        up_file = st.file_uploader("อัปโหลดไฟล์ (.py) หรือภาพหน้าจอผลลัพธ์", type=['py', 'png', 'jpg'])
        if up_file:
            st.success(f"ไฟล์ {up_file.name} พร้อมส่ง")
            if st.button("ยืนยันการส่งงาน"):
                st.balloons()
                st.info(f"ระบบบันทึกเวลาส่ง: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("👨‍🏫 ระบบสรุปผลสำหรับครู")
        pw = st.text_input("รหัสผ่านผู้สอน:", type="password")
        if pw == "obec2026":
            st.write("### สรุปสถานะปัจจุบัน")
            st.table({
                "นักเรียน": [st.session_state.user_name],
                "เลขที่": [st.session_state.user_no],
                "ความก้าวหน้า": [f"{int(progress_val*100)}%"],
                "การส่งงาน": ["✅ ส่งแล้ว" if up_file else "❌ ยังไม่ส่ง"]
            })
