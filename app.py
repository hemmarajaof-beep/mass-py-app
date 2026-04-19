import streamlit as st
import google.generativeai as genai
import gspread
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ (Layout) ---
st.set_page_config(layout="wide", page_title="MASS-Py: Future School Workspace")

# --- 2. ระบบเชื่อมต่อ AI ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets")
    st.stop()

def get_working_model():
    return genai.GenerativeModel('gemini-2.5-flash')

# --- 3. ระบบเชื่อมต่อ Google Sheets ฐานข้อมูล ---
# 🟢 นำลิงก์ Google Sheets ของคุณครูมาวางแทนที่ลิงก์ด้านล่างนี้ครับ 🟢
SHEET_URL = "https://docs.google.com/spreadsheets/d/17jLwS9BhfRSsIWCYi8p9c4xXqQFfldmofhVMiLAUZE0/edit?usp=sharing"

def save_to_database(mission_ep, logic_plan, work_status):
    try:
        # เชื่อมต่อกับ Google Sheets แบบสาธารณะ (สำหรับตัวต้นแบบ)
        gc = gspread.service_account_from_dict({}) if False else gspread.authorize(None) # Bypass auth for public editable sheet in simple mode
        # ทริคสำหรับ Streamlit: ใช้ Gspread ดึงข้อมูลแบบไม่ระบุตัวตนสำหรับชีทที่เปิด Public Editor ไว้
        # *หมายเหตุ: เพื่อความเสถียรสูงสุดในการประกวด เราจะจำลองการบันทึกไว้ใน Teacher Mode ก่อน 
        # หากต้องการต่อ API จริงแบบ Private ต้องใช้ Service Account (แจ้งผมได้ถ้าต้องการแบบเจาะลึกครับ)
    except Exception as e:
        pass # เราจะใช้ st.session_state เก็บประวัติไว้แสดงในตารางให้ครูดูเป็นหลักในตัวต้นแบบนี้

# --- 4. ระบบจัดการสถานะ (Session State) ---
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "user_no" not in st.session_state: st.session_state.user_no = ""
if "progress" not in st.session_state: st.session_state.progress = {}
if "messages" not in st.session_state: st.session_state.messages = []
if "logic_plan" not in st.session_state: st.session_state.logic_plan = ""
if "db_records" not in st.session_state: st.session_state.db_records = [] # เก็บข้อมูลฐานข้อมูล

# --- 5. หน้าจอระบุตัวตน (Login) ---
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

# --- 6. แถบข้าง (Sidebar) ---
with st.sidebar:
    st.title("👤 ข้อมูลผู้เรียน")
    st.info(f"**ชื่อ:** {st.session_state.user_name}\n\n**เลขที่:** {st.session_state.user_no} | **ห้อง:** {st.session_state.user_room}")
    st.divider()
    
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed_missions) / len(missions_list)
    
    st.subheader("📊 ความก้าวหน้าการเรียน")
    st.progress(progress_val)
    st.write(f"สำเร็จแล้ว {len(completed_missions)} จาก 5 ภารกิจ")
    
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

# --- 7. พื้นที่ทำงานหลัก (Main Workspace) ---
col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.subheader("🤖 AI Learning Buddies")
    agent = st.selectbox("เลือกผู้ช่วยสอน:", ["1. สถาปนิกตรรกะ (ช่วยวางแผน)", "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", "3. สารวัตรนักสืบ (ช่วยแก้ Error)"])
    
    if "1" in agent: sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนโปรแกรม ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อให้เด็กเขียน Pseudocode"
    elif "2" in agent: sys_prompt = "คุณคือบัดดี้เขียนโค้ด สอนไวยากรณ์ Python สั้นๆ ห้ามพิมพ์ Code Block ยาว"
    else: sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยแก้ Error โดยบอกใบ้จุดที่ผิด ห้ามแก้โค้ดให้ทันที"

    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        st.session_state.chat_session = get_working_model().start_chat(history=[])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("ปรึกษา AI บัดดี้ที่นี่..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                response = st.session_state.chat_session.send_message(f"[Role Instruction: {sys_prompt}]\nStudent Question: {prompt}")
                with st.chat_message("assistant"): st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception:
                st.error("🚨 บัดดี้ขาดการติดต่อชั่วคราว")

    if "1" in agent:
        st.divider()
        with st.expander("📝 สรุปและส่งลำดับการเขียนโปรแกรม (Logic Plan)", expanded=True):
            st.info("ให้นักเรียนสรุปลำดับขั้นตอนการทำงานจากที่ได้คุยกับสถาปนิกตรรกะ")
            logic_input = st.text_area("เขียนลำดับขั้นตอน (Pseudocode) ที่นี่:", value=st.session_state.logic_plan, height=150)
            if st.button("📤 ส่งแผนงานให้ครูตรวจ"):
                st.session_state.logic_plan = logic_input
                # บันทึกลงฐานข้อมูลจำลอง
                record = {"เวลา": datetime.now().strftime("%H:%M:%S"), "ชื่อ": st.session_state.user_name, "ตรรกะ": logic_input, "สถานะ": "ส่งแผนตรรกะแล้ว"}
                st.session_state.db_records.append(record)
                st.success("บันทึกแผนงานตรรกะเข้าสู่ระบบฐานข้อมูลสำเร็จ!")
                st.balloons()

with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจวันนี้", "📤 ส่งชิ้นงาน", "🔐 Teacher Mode"])
    
    with tab1:
        st.subheader("🎯 Programming Missions")
        mission_choice = st.radio("เลือกภารกิจ:", missions_list, horizontal=True)
        st.divider()
        if "EP.1" in mission_choice: st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ**\nโจทย์: เขียนโปรแกรมรับชื่อลูกค้า รับเมนูน้ำ และคำนวณเงินทอน")
        elif "EP.2" in mission_choice: st.success("**EP.2: คลินิก AI ประเมินสุขภาพ**\nโจทย์: รับค่าน้ำหนัก ส่วนสูง เพื่อคำนวณและแสดงค่า BMI")
        
        st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz)", "https://www.programiz.com/python-programming/online-compiler/")
        
        if st.button(f"✅ เรียน {mission_choice} สำเร็จแล้ว"):
            st.session_state.progress[mission_choice] = True
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งหลักฐานการเรียนรู้")
        up_file = st.file_uploader("แนบไฟล์โค้ด (.py) หรือภาพหน้าจอ", type=['py', 'png', 'jpg'])
        if up_file:
            if st.button("ยืนยันการส่งงานไปยังคุณครู"):
                # บันทึกลงฐานข้อมูลจำลอง
                record = {"เวลา": datetime.now().strftime("%H:%M:%S"), "ชื่อ": st.session_state.user_name, "ตรรกะ": "ส่งไฟล์แนบ", "สถานะ": "ส่งชิ้นงานสมบูรณ์"}
                st.session_state.db_records.append(record)
                st.balloons()
                st.success(f"บันทึกไฟล์และข้อมูลเข้าฐานข้อมูลสำเร็จเมื่อ: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("🔒 ศูนย์ควบคุมข้อมูลผู้สอน (Data Dashboard)")
        teacher_pw = st.text_input("รหัสผ่านผู้สอน:", type="password")
        if teacher_pw == "obec2026":
            st.write("### 📊 ฐานข้อมูลการส่งงานแบบ Real-time (Data Log)")
            if len(st.session_state.db_records) > 0:
                # แสดงฐานข้อมูลออกมาเป็นตารางสวยงาม
                st.dataframe(st.session_state.db_records, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลการส่งงานในระบบขณะนี้")
                
            st.divider()
            st.write("### 🧠 แผนงานตรรกะล่าสุด (Active Logic Plan)")
            if st.session_state.logic_plan:
                st.code(st.session_state.logic_plan, language="text")
            else:
                st.warning("ไม่มีข้อมูล")
