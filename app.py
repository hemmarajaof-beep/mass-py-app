import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ (Layout) ---
st.set_page_config(layout="wide", page_title="MASS-Py: Mission Control V.4")

# --- 2. ระบบดึงกุญแจ API อย่างปลอดภัย ---
try:
    # แก้ไขบรรทัดนี้: ให้ใช้ชื่อตัวแปร "API_KEY" (ชื่อสมมติที่ตรงกับหน้า Secrets)
    API_KEY = st.secrets["API_KEY"] 
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🚨 ไม่พบกุญแจ API ในระบบ Secrets กรุณาตรวจสอบการตั้งค่าหลังบ้าน")
    st.stop()

# ฟังก์ชันดึงโมเดล AI
# แก้ไขฟังก์ชันดึงโมเดลให้ฉลาดขึ้น
def get_working_model():
    # ลองใช้ชื่อเต็มรูปแบบที่ระบบเก่าก็น่าจะรู้จัก
    return genai.GenerativeModel('models/gemini-pro')
    try:
        # ตรวจสอบรายชื่อโมเดลที่รองรับในระบบปัจจุบัน
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # ถ้ามีชื่อที่ยาวกว่า (เช่น models/...) ให้ใช้ชื่อนั้น
        for m in available_models:
            if 'gemini-1.5-flash' in m:
                model_name = m
                break
    except:
        pass
    return genai.GenerativeModel(model_name)

# --- 3. ระบบจัดการสถานะผู้เรียน (Session State) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_no" not in st.session_state:
    st.session_state.user_no = ""
if "progress" not in st.session_state:
    st.session_state.progress = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. หน้าจอระบุตัวตน (Identity Interface) ---
if not st.session_state.user_name:
    st.title("🚀 ยินดีต้อนรับสู่ MASS-Py")
    st.subheader("กรุณาระบุข้อมูลนักเรียนเพื่อเข้าสู่ระบบการเรียนรู้")
    
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
                st.warning("⚠️ กรุณากรอกชื่อและเลขที่ให้ครบถ้วนก่อนเข้าใช้งาน")
    st.stop()

# --- 5. ส่วนหน้าจอหลัก (Main Interface) ---
# Sidebar สำหรับแสดงโปรไฟล์และความก้าวหน้า
with st.sidebar:
    st.title("👤 ข้อมูลผู้เรียน")
    st.info(f"**นักเรียน:** {st.session_state.user_name}\n\n**เลขที่:** {st.session_state.user_no} | **ห้อง:** {st.session_state.user_room}")
    
    st.divider()
    
    # ระบบ Progress Bar
    missions_list = ["EP.1", "EP.2", "EP.3", "EP.4", "EP.5"]
    completed_missions = [m for m in missions_list if st.session_state.progress.get(m)]
    progress_val = len(completed_missions) / len(missions_list)
    
    st.subheader("📊 ความก้าวหน้า")
    st.progress(progress_val)
    st.write(f"ทำสำเร็จแล้ว {len(completed_missions)} จาก {len(missions_list)} ภารกิจ")
    
    if st.button("ล้างประวัติการแชท (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

# แบ่งหน้าจอเป็น 2 ฝั่ง
col1, col2 = st.columns([0.4, 0.6])

# ================= ฝั่งซ้าย: AI แชทอัจฉริยะ =================
with col1:
    st.subheader("🤖 เรียกใช้ AI Agents")
    
    agent = st.selectbox("เลือกบัดดี้ของคุณ:", [
        "1. สถาปนิกตรรกะ (ช่วยวางแผน)", 
        "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", 
        "3. สารวัตรนักสืบ (ช่วยแก้ Error)"
    ])
    
    # กำหนดบทบาท AI (System Prompt)
    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนตรรกะ Python ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อให้เด็กเขียน Pseudocode"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด ช่วยสอนไวยากรณ์ Python ห้ามพิมพ์ Code Block ยาวๆ ให้บอกใบ้โครงสร้าง"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยเด็กวิเคราะห์ Error ห้ามแก้โค้ดให้ แต่ให้บอกใบ้ 3 ข้อว่าควรไปเช็คตรงไหน"

    # ระบบจัดการห้องแชท
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        model = get_working_model()
        st.session_state.chat_session = model.start_chat(history=[])

    # แสดงประวัติการแชท
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ช่องรับคำถาม (พร้อมระบบดัก Error)
    if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                # ส่งคำสั่งลับ (System Prompt) แนบไปกับคำถาม
                full_query = f"[คำสั่งสำหรับ AI: {sys_prompt}]\n\nคำถามจากนักเรียน: {prompt}"
                response = st.session_state.chat_session.send_message(full_query)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                # แสดงข้อความเมื่อเกิด Error แทนหน้าจอสีแดง
                st.error("🚨 บัดดี้ขาดการติดต่อชั่วคราว (Connection Error)")
                st.warning("กรุณาลองพิมพ์คำถามใหม่อีกครั้ง หรือตรวจสอบสัญญาณอินเทอร์เน็ต")
                st.caption(f"Error Code: {str(e)[:50]}...")

# ================= ฝั่งขวา: ภารกิจและระบบจัดการงาน =================
with col2:
    tab1, tab2, tab3 = st.tabs(["🎯 ภารกิจวันนี้", "📤 ส่งผลงาน", "🔐 ส่วนของครู"])
    
    with tab1:
        st.subheader("🎯 Mission Details")
        mission_choice = st.radio("เลือกภารกิจ:", missions_list, horizontal=True)
        
        st.divider()
        # คำอธิบายโจทย์ตามภารกิจ
        if "EP.1" in mission_choice:
            st.success("**EP.1: ตู้สั่งน้ำอัจฉริยะ**\n\nเขียนโปรแกรมรับชื่อลูกค้า รับเมนู และคำนวณเงินทอน")
        elif "EP.2" in mission_choice:
            st.success("**EP.2: คลินิก AI ประเมินสุขภาพ**\n\nคำนวณค่า BMI และแสดงเกณฑ์ อ้วน/ผอม/ปกติ")
        elif "EP.3" in mission_choice:
            st.success("**EP.3: ระบบรักษาความปลอดภัย**\n\nจำลองการรับรหัสผ่านด้วยการวนลูป While Loop")
        elif "EP.4" in mission_choice:
            st.success("**EP.4: ตะกร้าสินค้า**\n\nการเพิ่มและลบข้อมูลใน List")
        elif "EP.5" in mission_choice:
            st.info("**EP.5: โครงงานอิสระ**\n\nสร้างนวัตกรรมแก้ปัญหาด้วย Python ด้วยตัวเอง")
            
        st.link_button("➡️ เปิดพื้นที่เขียนโค้ด (Programiz)", "https://www.programiz.com/python-programming/online-compiler/")
        
        if st.button(f"✅ บันทึกว่าทำ {mission_choice} สำเร็จแล้ว", use_container_width=True):
            st.session_state.progress[mission_choice] = True
            st.toast("บันทึกความก้าวหน้าสำเร็จ!")
            st.rerun()

    with tab2:
        st.subheader("📤 ส่งหลักฐานการเรียนรู้")
        uploaded_file = st.file_uploader("แนบไฟล์โค้ด (.py) หรือภาพถ่ายหน้าจอผลลัพธ์", type=['py', 'txt', 'png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.success(f"เตรียมส่งไฟล์: {uploaded_file.name}")
            if st.button("ยืนยันการส่งงานไปยังระบบ"):
                st.balloons()
                st.success("ส่งงานสำเร็จ! ระบบบันทึกเวลาที่: " + datetime.now().strftime("%H:%M:%S"))

    with tab3:
        st.subheader("🔒 Teacher Dashboard")
        admin_pw = st.text_input("ระบุรหัสผ่านครู:", type="password")
        if admin_pw == "obec2026":
            st.write("📋 **สรุปสถานะผู้เรียนรายบุคคล**")
            # แสดงตารางสรุปข้อมูล
            teacher_data = {
                "ชื่อผู้เรียน": [st.session_state.user_name],
                "เลขที่": [st.session_state.user_no],
                "ห้อง": [st.session_state.user_room],
                "ความก้าวหน้า": [f"{int(progress_val*100)}%"],
                "ส่งงานแล้ว": ["✅ ใช่" if uploaded_file else "❌ ยังไม่ส่ง"]
            }
            st.table(teacher_data)
        elif admin_pw:
            st.error("รหัสผ่านไม่ถูกต้อง")
