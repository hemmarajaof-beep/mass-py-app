import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ (Layout) ---
st.set_page_config(layout="wide", page_title="MASS-Py: Future School Workspace")

# --- 2. ระบบเชื่อมต่อ AI (Gemini 2.5 Flash) ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets")
    st.stop()

def get_working_model():
    # ใช้รุ่นที่กุญแจคุณครูมีสิทธิ์ (gemini-2.5-flash)
    return genai.GenerativeModel('gemini-2.5-flash')

# --- 3. ระบบจัดการสถานะ (Session State) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_no" not in st.session_state:
    st.session_state.user_no = ""
if "progress" not in st.session_state:
    st.session_state.progress = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logic_plan" not in st.session_state:
    st.session_state.logic_plan = ""

# --- 4. หน้าจอระบุตัวตน (Login) ---
if not st.session_state.user_name:
    st.title("🚀 MASS-Py: Mission Control")
    st.subheader("กรุณาระบุข้อมูลนักเรียนเพื่อเข้าใช้งานระบบ")
    
    with st.container(border=True):
        name = st.text_input("ชื่อ-นามสกุล:")
        no = st.text_input("เลขที่:")
        room = st.selectbox("ห้องเรียน:", ["ม.3/1", "ม.3/2", "ม.3/3", "ม.3/4"])
        
        if st.button("🚀 เข้าสู่ห้องเรียนอัจฉริยะ", use_container_width=True):
            if name and no:
                st.session_state.user_name = name
                st.session_state.user_no = no
                st.session_state.user_room = room
                st.rerun()
            else:
                st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
    st.stop()

# --- 5. แถบข้าง (Sidebar) สำหรับข้อมูลและความก้าวหน้า ---
with st.sidebar:
    st.title("👤 ข้อมูลผู้เรียน")
    st.info(f"**ชื่อ:** {st.session_state.user_name}\n\n**เลขที่:** {st.session_state.user_no} | **ห้อง:** {st.session_state.user_room}")
    
    st.divider()
    
    # คำนวณ Progress
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed_missions) / len(missions_list)
    
    st.subheader("📊 ความก้าวหน้าการเรียน")
    st.progress(progress_val)
    st.write(f"สำเร็จแล้ว {len(completed_missions)} จาก 5 ภารกิจ")
    
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

# --- 6. พื้นที่ทำงานหลัก (Main Workspace) ---
col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI Chat & Logic Plan =================
with col1:
    st.subheader("🤖 AI Learning Buddies")
    agent = st.selectbox("เลือกผู้ช่วยสอน:", [
        "1. สถาปนิกตรรกะ (ช่วยวางแผน)", 
        "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", 
        "3. สารวัตรนักสืบ (ช่วยแก้ Error)"
    ])
    
    # กำหนดคำสั่ง AI (System Prompt)
    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนโปรแกรม ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อให้เด็กเขียน Pseudocode"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด สอนไวยากรณ์ Python สั้นๆ ห้ามพิมพ์ Code Block ยาว"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยแก้ Error โดยบอกใบ้จุดที่ผิด ห้ามแก้โค้ดให้ทันที"

    # จัดการแชท
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[])

    # แสดงข้อความแชท
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("ปรึกษา AI บัดดี้ที่นี่..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                full_query = f"[Role Instruction: {sys_prompt}]\nStudent Question: {prompt}"
                response = st.session_state.chat_session.send_message(full_query)
                with st.chat_message("assistant"): st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception:
                st.error("🚨 บัดดี้ขาดการติดต่อชั่วคราว กรุณาลองใหม่อีกครั้ง")

    # ----- ✨ ส่วนส่งแผนตรรกะ (ปรากฏเฉพาะสถาปนิกตรรกะ) ✨ -----
    if "1" in agent:
        st.divider()
        with st.expander("📝 สรุปและส่งลำดับการเขียนโปรแกรม (Logic Plan)", expanded=True):
            st.info("ให้นักเรียนสรุปลำดับขั้นตอนการทำงานจากที่ได้คุยกับสถาปนิกตรรกะ")
            logic_input = st.text_area("เขียนลำดับขั้นตอน (Pseudocode) ที่นี่:", value=st.session_state.logic_plan, height=150)
            if st.button("📤 ส่งแผนงานให้ครูตรวจ"):
                st.session_state.logic_plan = logic_input
                st.success("บันทึกแผนงานตรรกะสำเร็จ! ครูสามารถตรวจดูได้ในหน้า Teacher Mode")
                st.balloons()

# ================= ฝั่งขวา: ภารกิจ & ระบบจัดการงาน =================
with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจวันนี้", "📤 ส่งชิ้นงาน", "🔐 Teacher Mode"])
    
    with tab1:
        st.subheader("🎯 Programming Missions")
        mission_choice = st.radio("เลือกภารกิจ:", missions_list, horizontal=True)
        st.divider()
        
        if "EP.1" in mission_choice:
            st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ**\nโจทย์: เขียนโปรแกรมรับชื่อลูกค้า รับเมนูน้ำ และคำนวณเงินทอน")
        elif "EP.2" in mission_choice:
            st.success("**EP.2: คลินิก AI ประเมินสุขภาพ**\nโจทย์: รับค่าน้ำหนัก ส่วนสูง เพื่อคำนวณและแสดงค่า BMI")
        elif "EP.3" in mission_choice:
            st.success("**EP.3: ระบบล็อคบ้านอัจฉริยะ**\nโจทย์: ใช้ While Loop เพื่อตรวจสอบรหัสผ่าน 3 ครั้ง")
        
        st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz)", "https://www.programiz.com/python-programming/online-compiler/")
        
        if st.button(f"✅ เรียน {mission_choice} สำเร็จแล้ว"):
            st.session_state.progress[mission_choice] = True
            st.toast("บันทึกความก้าวหน้าสำเร็จ!")
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งหลักฐานการเรียนรู้")
        up_file = st.file_uploader("แนบไฟล์โค้ด (.py) หรือภาพหน้าจอผลลัพธ์", type=['py', 'png', 'jpg', 'jpeg'])
        if up_file:
            st.success(f"ไฟล์ {up_file.name} เตรียมพร้อมส่ง")
            if st.button("ยืนยันการส่งงานไปยังคุณครู"):
                st.balloons()
                st.info(f"บันทึกข้อมูลสำเร็จเมื่อ: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("🔒 ส่วนสำหรับผู้สอน")
        teacher_pw = st.text_input("รหัสผ่านผู้สอน:", type="password")
        if teacher_pw == "obec2026":
            # ตารางสรุปทั่วไป
            st.write("### 📋 สรุปข้อมูลรายบุคคล")
            st.table({
                "นักเรียน": [st.session_state.user_name],
                "เลขที่": [st.session_state.user_no],
                "ความก้าวหน้า": [f"{int(progress_val*100)}%"],
                "การส่งชิ้นงาน": ["✅ ส่งแล้ว" if up_file else "❌ ยังไม่ส่ง"]
            })
            
            # ส่วนแสดงแผนตรรกะที่เด็กส่งมา
            st.write("### 🧠 กระบวนการคิดเชิงตรรกะ (Logic Plan)")
            if st.session_state.logic_plan:
                st.code(st.session_state.logic_plan, language="text")
            else:
                st.warning("นักเรียนยังไม่มีการส่งแผนตรรกะใน EP นี้")
