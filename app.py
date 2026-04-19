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
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets")
    st.stop()

# --- 3. ระบบเชื่อมต่อฐานข้อมูล (โปรดใส่ลิงก์ของคุณครู) ---
# แก้ไข: วางลิงก์ที่นี่ที่เดียว ห้ามวางในส่วน Session State
SHEET_URL = "https://docs.google.com/spreadsheets/d/17jLwS9BhfRSsIWCYi8p9c4xXqQFfldmofhVMiLAUZE0/edit?usp=sharing"

# --- 4. ระบบจัดการสถานะ (Session State) ---
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "user_no" not in st.session_state: st.session_state.user_no = ""
if "progress" not in st.session_state: st.session_state.progress = {}
if "messages" not in st.session_state: st.session_state.messages = []
if "logic_plan" not in st.session_state: st.session_state.logic_plan = ""
if "db_records" not in st.session_state: st.session_state.db_records = [] 

# --- 5. ฟังก์ชันพิเศษ: ระบบดึงข้อมูลเก่า (Resume Function) ---
def resume_student_data(name, no):
    # ค้นหาในประวัติ (db_records) ว่าเคยมีชื่อและเลขที่นี้ไหม
    for record in st.session_state.db_records:
        if record["ชื่อ"] == name and record["เลขที่"] == no:
            # ถ้าเจอ ให้ดึงข้อมูลตรรกะล่าสุดกลับมา
            st.session_state.logic_plan = record["ตรรกะ"]
            # จำลองการโหลด Progress (ในระบบจริงจะดึงจากคอลัมน์ EP)
            st.toast(f"🔄 ยินดีต้อนรับกลับมา! ระบบดึงข้อมูลเดิมของ {name} สำเร็จ")
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
                # เรียกใช้ระบบดึงข้อมูลเก่าทันทีที่ Login
                resume_student_data(name, no)
                st.rerun()
            else:
                st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
    st.stop()

# --- 7. พื้นที่ทำงานหลัก ---
with st.sidebar:
    st.title("👤 โปรไฟล์ผู้เรียน")
    st.info(f"**ชื่อ:** {st.session_state.user_name}\n**เลขที่:** {st.session_state.user_no}")
    st.divider()
    
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed_missions) / len(missions_list)
    st.subheader("📊 ความก้าวหน้า")
    st.progress(progress_val)
    
    if st.button("🗑️ ล้างประวัติแชท"):
        st.session_state.messages = []
        st.rerun()

col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.subheader("🤖 AI Buddies")
    agent = st.selectbox("เปลี่ยนบัดดี้:", ["1. สถาปนิกตรรกะ", "2. บัดดี้เขียนโค้ด", "3. สารวัตรนักสืบ"])
    
    # ดึงประวัติแชทมาแสดง
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("คุยกับ AI..."):
        with st.chat_message("user"): st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        # (ส่วนส่งข้อความหา AI Gemini 2.5 Flash เหมือนเดิม...)
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            with st.chat_message("assistant"): st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except: st.error("ขัดข้อง")

    if "1" in agent:
        st.divider()
        st.write("📝 **แผนงานตรรกะของคุณ (บันทึกอัตโนมัติ)**")
        logic_input = st.text_area("สรุปขั้นตอนที่นี่:", value=st.session_state.logic_plan, height=150)
        if st.button("📤 อัปเดตและบันทึกลงฐานข้อมูล"):
            st.session_state.logic_plan = logic_input
            # จำลองการเขียนลง DB
            new_record = {
                "เวลา": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "ชื่อ": st.session_state.user_name,
                "เลขที่": st.session_state.user_no,
                "ตรรกะ": logic_input,
                "สถานะ": "อัปเดตงาน"
            }
            st.session_state.db_records.append(new_record)
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจ", "📤 ส่งชิ้นงาน", "🔐 Teacher Mode"])
    with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจ", "📤 ส่งชิ้นงาน", "🔐 Teacher Mode"])
    
    with tab1:
        st.subheader("🎯 Programming Missions")
        # ดึงรายชื่อภารกิจมาแสดง
        mission_choice = st.radio("เลือกภารกิจ:", ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"], horizontal=True)
        st.divider()
        
        # แสดงโจทย์ตาม EP ที่เลือก
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
                # จำลองการเขียนลง DB
                record = {
                    "เวลา": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ชื่อ": st.session_state.user_name,
                    "เลขที่": st.session_state.user_no,
                    "ตรรกะ": "ส่งไฟล์แนบ",
                    "สถานะ": f"ส่งชิ้นงาน {mission_choice} สมบูรณ์"
                }
                st.session_state.db_records.append(record)
                st.balloons()
                st.info(f"บันทึกข้อมูลสำเร็จเมื่อ: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("🔐 ศูนย์ข้อมูลครู (Teacher Mode)")
        teacher_pw = st.text_input("รหัสผ่านผู้สอน:", type="password")
        if teacher_pw == "obec2026":
            st.write("### 📊 ฐานข้อมูลการส่งงาน (Data Log)")
            if len(st.session_state.db_records) > 0:
                st.dataframe(st.session_state.db_records, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลการส่งงานในระบบขณะนี้")
    with tab3:
        st.subheader("🔐 ศูนย์ข้อมูลครู")
        if st.text_input("รหัสผ่าน:", type="password") == "obec2026":
            st.dataframe(st.session_state.db_records)
