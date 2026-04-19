import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(layout="wide", page_title="MASS-Py Workspace V.4")

# --- 2. ระบบดึงกุญแจ API ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("🚨 ไม่พบกุญแจ API")
    st.stop()

def get_working_model():
    return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ส่วนการระบุตัวตน (Authentication) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_no" not in st.session_state:
    st.session_state.user_no = ""
if "progress" not in st.session_state:
    st.session_state.progress = {}

# หน้าจอ Login
if not st.session_state.user_name:
    st.title("🚀 ยินดีต้อนรับสู่ MASS-Py")
    st.subheader("กรุณาระบุข้อมูลเพื่อเข้าสู่ระบบการเรียน")
    name = st.text_input("ชื่อ-นามสกุล:")
    no = st.text_input("เลขที่:")
    room = st.selectbox("ห้อง:", ["ม.3/1", "ม.3/2", "ม.3/3"])
    
    if st.button("เข้าสู่บทเรียน"):
        if name and no:
            st.session_state.user_name = name
            st.session_state.user_no = no
            st.session_state.user_room = room
            st.rerun()
        else:
            st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
    st.stop()

# --- 4. ส่วนหน้าหลัก (Main App) ---
st.sidebar.title(f"👤 {st.session_state.user_name} (เลขที่ {st.session_state.user_no})")
st.sidebar.write(f"🏫 ห้อง: {st.session_state.user_room}")

# ระบบ Progress Bar
missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
progress_val = len(completed_missions) / len(missions_list)
st.sidebar.write("📊 ความก้าวหน้า")
st.sidebar.progress(progress_val)
st.sidebar.write(f"ทำสำเร็จแล้ว {len(completed_missions)} จาก 5 ภารกิจ")

col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI แชท =================
with col1:
    st.subheader("🤖 AI Buddies")
    agent = st.selectbox("เลือกบัดดี้:", ["1. สถาปนิกตรรกะ", "2. บัดดี้เขียนโค้ด", "3. สารวัตรนักสืบ"])
    
    if "messages" not in st.session_state: st.session_state.messages = []
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

 with st.spinner("บัดดี้กำลังคิด..."):
            try:
                # เพิ่มกฎเหล็กและส่งข้อความ
                full_prompt = f"[คำสั่งบังคับ: {sys_prompt}]\nคำถาม: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt)
                
                # แสดงคำตอบ
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                # หากเกิด Error ระบบจะไม่ล่ม แต่จะแสดงคำแนะนำแทน
                st.error("🚨 บัดดี้ขาดการติดต่อชั่วคราว (Connection Timeout)")
                st.warning("💡 วิธีแก้: 1. ตรวจสอบเน็ต 2. ลองพิมพ์ใหม่อีกครั้ง หรือ 3. กด 'Reboot App' ที่เมนูมุมขวา")
                # บันทึก log ข้อผิดพลาดไว้ดูเบื้องหลัง
                print(f"Error detail: {str(e)}")

# ================= ฝั่งขวา: ภารกิจ & ระบบส่งงาน =================
with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจวันนี้", "📤 ส่งงาน", "👨‍🏫 สำหรับครู"])
    
    with tab1:
        mission_choice = st.radio("เลือก EP:", missions_list, horizontal=True)
        st.divider()
        if "EP.1" in mission_choice:
            st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ** (รับค่า & แสดงผล)")
        elif "EP.2" in mission_choice:
            st.success("**EP.2: คลินิก AI ประเมินสุขภาพ** (If-Else)")
        # ... (เพิ่มเนื้อหา EP อื่นๆ ได้ตรงนี้)
        
        if st.button(f"✅ บันทึกว่าเรียน {mission_choice} สำเร็จแล้ว"):
            st.session_state.progress[mission_choice] = True
            st.toast(f"บันทึกความก้าวหน้า {mission_choice} เรียบร้อย!")
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งไฟล์งาน (Python / Screenshot)")
        uploaded_file = st.file_uploader("เลือกไฟล์ผลงานจากเครื่องของคุณ", type=['py', 'txt', 'png', 'jpg'])
        if uploaded_file is not None:
            st.success(f"ไฟล์ {uploaded_file.name} พร้อมส่งแล้ว!")
            if st.button("ยืนยันการส่งงาน"):
                # ในเวอร์ชันจริง ข้อมูลนี้จะถูกส่งเข้า Database หรือ Google Drive
                st.balloons()
                st.info(f"ระบบบันทึกเวลาส่ง: {datetime.now().strftime('%H:%M:%S')}")

    with tab3:
        st.subheader("🔒 ส่วนของผู้จัดการชั้นเรียน")
        pw = st.text_input("รหัสผ่านสำหรับครู:", type="password")
        if pw == "obec2026": # คุณครูเปลี่ยนรหัสได้ตรงนี้
            st.write("### สรุปข้อมูลผู้ใช้งานปัจจุบัน")
            st.table({
                "นักเรียน": [st.session_state.user_name],
                "เลขที่": [st.session_state.user_no],
                "สถานะการส่งงาน": ["พร้อมตรวจ" if uploaded_file else "ยังไม่ส่ง"],
                "ความก้าวหน้า": [f"{int(progress_val*100)}%"]
            })
            st.info("💡 ข้อมูลในหน้านี้สามารถเชื่อมต่อกับ Google Sheets เพื่อสรุปผลทั้งห้องได้ในอนาคต")
