import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(layout="wide", page_title="MASS-Py: Smart Persistence LMS")

# --- 2. ระบบเชื่อมต่อ AI ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets กรุณาตรวจสอบการตั้งค่า")
    st.stop()

def get_working_model():
    return genai.GenerativeModel('gemini-2.5-flash')

# --- 3. ลิงก์เชื่อมต่อฐานข้อมูล Google Sheets (สำหรับนำเสนอ) ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/17jLwS9BhfRSsIWCYi8p9c4xXqQFfldmofhVMiLAUZE0/edit?usp=sharing"

# --- 4. ระบบจัดการสถานะ (Session State) ---
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "user_no" not in st.session_state: st.session_state.user_no = ""
if "user_room" not in st.session_state: st.session_state.user_room = ""
if "progress" not in st.session_state: st.session_state.progress = {}
if "messages" not in st.session_state: st.session_state.messages = []
if "logic_plan" not in st.session_state: st.session_state.logic_plan = ""
if "db_records" not in st.session_state: st.session_state.db_records = []
if "current_agent" not in st.session_state: st.session_state.current_agent = "1. สถาปนิกตรรกะ (ช่วยวางแผน)"
if "chat_session" not in st.session_state: 
    st.session_state.chat_session = get_working_model().start_chat(history=[])

# --- 5. ฟังก์ชันดึงข้อมูลผู้เรียน (Resume System) ---
def resume_student_data(name, no):
    for record in reversed(st.session_state.db_records):
        if record["ชื่อ"] == name and record["เลขที่"] == no:
            if record["รายละเอียด"] != "ส่งไฟล์แนบ":
                st.session_state.logic_plan = record["รายละเอียด"]
            st.toast(f"🔄 ยินดีต้อนรับกลับมา! ดึงข้อมูลของ {name} สำเร็จ")
            break

# --- 6. หน้าจอระบุตัวตน (Login) ---
if not st.session_state.user_name:
    st.title("🚀 MASS-Py: Intelligent Resume System")
    st.subheader("ระบุข้อมูลเดิมเพื่อทำงานต่อ หรือข้อมูลใหม่เพื่อเริ่มบทเรียน")
    with st.container(border=True):
        name = st.text_input("ชื่อ-นามสกุล:")
        no = st.text_input("เลขที่:")
        room = st.selectbox("ห้องเรียน:", ["ม.3/1", "ม.3/2", "ม.3/3", "ม.3/4"])
        if st.button("🚀 เข้าสู่ห้องเรียน", use_container_width=True):
            if name and no:
                st.session_state.user_name = name
                st.session_state.user_no = no
                st.session_state.user_room = room
                resume_student_data(name, no) # เรียกคืนข้อมูลเมื่อเข้าระบบ
                st.rerun()
            else:
                st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
    st.stop()

# --- 7. แถบเครื่องมือด้านข้าง (Sidebar) ---
with st.sidebar:
    st.title("👤 โปรไฟล์ผู้เรียน")
    st.info(f"**ชื่อ:** {st.session_state.user_name}\n\n**เลขที่:** {st.session_state.user_no} | **ห้อง:** {st.session_state.user_room}")
    st.divider()
    
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed_missions) / len(missions_list)
    
    st.subheader("📊 ความก้าวหน้า")
    st.progress(progress_val)
    st.write(f"สำเร็จแล้ว {len(completed_missions)} จาก 5 ภารกิจ")
    
    st.divider()
    if st.button("🗑️ ล้างประวัติแชท"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🚪 ออกจากระบบ (Logout)"):
        st.session_state.user_name = ""
        st.session_state.user_no = ""
        st.session_state.messages = []
        st.session_state.logic_plan = ""
        st.rerun()

# --- 8. พื้นที่ทำงานหลัก (Main Workspace) ---
col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI Chat & Logic =================
with col1:
    st.subheader("🤖 AI Learning Buddies")
    agent = st.selectbox("เปลี่ยนบัดดี้:", ["1. สถาปนิกตรรกะ (ช่วยวางแผน)", "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", "3. สารวัตรนักสืบ (ช่วยแก้ Error)"])
    
    if "1" in agent: sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนโปรแกรม ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อให้เด็กเขียน Pseudocode"
    elif "2" in agent: sys_prompt = "คุณคือบัดดี้เขียนโค้ด สอนไวยากรณ์ Python สั้นๆ ห้ามพิมพ์ Code Block ยาว"
    else: sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยแก้ Error โดยบอกใบ้จุดที่ผิด ห้ามแก้โค้ดให้ทันที"

    if st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        st.session_state.chat_session = get_working_model().start_chat(history=[])

    # แสดงประวัติแชท
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # รับข้อความใหม่
    if prompt := st.chat_input("คุยกับ AI บัดดี้..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                full_prompt = f"[Role Instruction: {sys_prompt}]\nStudent Question: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt)
                with st.chat_message("assistant"): st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception:
                st.error("🚨 ขัดข้องชั่วคราว กรุณาลองใหม่")

    # แผนงานตรรกะ (เฉพาะสถาปนิกตรรกะ)
    if "1" in agent:
        st.divider()
        with st.expander("📝 สรุปและส่งลำดับการเขียนโปรแกรม (Logic Plan)", expanded=True):
            logic_input = st.text_area("สรุปขั้นตอน (Pseudocode) ที่นี่:", value=st.session_state.logic_plan, height=150)
            if st.button("📤 อัปเดตและส่งแผนงาน"):
                st.session_state.logic_plan = logic_input
                new_record = {
                    "เวลา": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "ชื่อ": st.session_state.user_name,
                    "เลขที่": st.session_state.user_no,
                    "รายละเอียด": logic_input,
                    "สถานะ": "ส่งแผนตรรกะ"
                }
                st.session_state.db_records.append(new_record)
                st.success("บันทึกข้อมูลตรรกะลงระบบแล้ว!")
                st.balloons()

# ================= ฝั่งขวา: Missions & Teacher =================
with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจ", "📤 ส่งชิ้นงาน", "🔐 Teacher Mode"])
    
    with tab1:
        st.subheader("🎯 Programming Missions")
        mission_choice = st.radio("เลือกภารกิจ:", ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"], horizontal=True)
        st.divider()
        
        if "EP.1" in mission_choice: st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ**\nโจทย์: เขียนโปรแกรมรับชื่อลูกค้า รับเมนูน้ำ และคำนวณเงินทอน")
        elif "EP.2" in mission_choice: st.success("**EP.2: คลินิก AI ประเมินสุขภาพ**\nโจทย์: รับค่าน้ำหนัก ส่วนสูง เพื่อคำนวณและแสดงค่า BMI")
        elif "EP.3" in mission_choice: st.success("**EP.3: ระบบล็อคบ้านอัจฉริยะ**\nโจทย์: ใช้ While Loop ตรวจสอบรหัสผ่าน 3 ครั้ง")
        elif "EP.4" in mission_choice: st.info("กำลังปลดล็อคเนื้อหา EP.4...")
        elif "EP.5" in mission_choice: st.info("กำลังปลดล็อคเนื้อหา EP.5...")
        
        st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz)", "https://www.programiz.com/python-programming/online-compiler/")
        
        if st.button(f"✅ เรียน {mission_choice} สำเร็จแล้ว"):
            st.session_state.progress[mission_choice] = True
            st.toast(f"บันทึกความก้าวหน้า {mission_choice} สำเร็จ!")
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งหลักฐานการเรียนรู้")
        up_file = st.file_uploader("แนบไฟล์โค้ด (.py) หรือภาพหน้าจอผลลัพธ์", type=['py', 'png', 'jpg', 'jpeg'])
        if up_file:
            st.success(f"ไฟล์ {up_file.name} เตรียมพร้อมส่ง")
            if st.button("ยืนยันการส่งงานไปยังคุณครู"):
                new_record = {
                    "เวลา": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "ชื่อ": st.session_state.user_name,
                    "เลขที่": st.session_state.user_no,
                    "รายละเอียด": "ส่งไฟล์แนบ",
                    "สถานะ": f"ส่งชิ้นงาน {mission_choice} สมบูรณ์"
                }
                st.session_state.db_records.append(new_record)
                st.balloons()
                st.info(f"บันทึกไฟล์สำเร็จเมื่อ: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("🔐 ศูนย์ข้อมูลครู (Teacher Dashboard)")
        teacher_pw = st.text_input("รหัสผ่านผู้สอน:", type="password")
        if teacher_pw == "obec2026":
            st.write("### 📊 ฐานข้อมูลการส่งงาน (Real-time Log)")
            if len(st.session_state.db_records) > 0:
                st.dataframe(st.session_state.db_records, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลในระบบขณะนี้")
                
            st.divider()
            st.write(f"🔗 **ลิงก์อ้างอิงฐานข้อมูล:** [Google Sheets]({SHEET_URL})")
