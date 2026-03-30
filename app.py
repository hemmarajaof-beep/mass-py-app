import streamlit as st
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="MASS-Py Workspace")

# --- 1. ดึงกุญแจจากตู้เซฟ ---
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

with col1:
    st.subheader("🤖 เรียกใช้ AI Agents")
    
    # เมนูเลือกบัดดี้
    agent = st.selectbox("เลือกบัดดี้ของคุณ:", ["1. สถาปนิกตรรกะ (ช่วยวางแผน)", "2. บัดดี้เขียนโค้ด (ช่วยไวยากรณ์)", "3. สารวัตรนักสืบ (ช่วยแก้ Error)"])
    
    # --- 2. ระบบความจำ (ถ้าเปลี่ยนตัวบัดดี้ ให้ล้างความจำใหม่) ---
    if "current_agent" not in st.session_state or st.session_state.current_agent != agent:
        st.session_state.current_agent = agent
        st.session_state.messages = [] # ล้างหน้าจอแชท
        model = get_working_model()
        # เปิดโหมด "แชทต่อเนื่อง" ของ Gemini
        st.session_state.chat_session = model.start_chat(history=[]) 

    # กำหนดนิสัย AI (System Prompt)
    if "1" in agent:
        sys_prompt = "คุณคือสถาปนิกตรรกะ ช่วยเด็ก ม.3 วางแผนตรรกะ Python ห้ามให้โค้ดเด็ดขาด ให้ถามนำเพื่อเขียน Pseudocode"
    elif "2" in agent:
        sys_prompt = "คุณคือบัดดี้เขียนโค้ด ช่วยเด็ก ม.3 เขียน Python ห้ามพิมพ์ Code Block ยาวๆ ให้บอกใบ้โครงสร้าง"
    else:
        sys_prompt = "คุณคือสารวัตรนักสืบ ช่วยเด็กวิเคราะห์ Error ห้ามแก้โค้ดให้ แต่ให้บอกใบ้ 3 ข้อว่าควรไปเช็คตรงไหน"

    # --- 3. แสดงประวัติการแชทบนหน้าจอ ---
    # โค้ดส่วนนี้จะดึงข้อความเก่าๆ มาวาดบนจอใหม่ทุกครั้ง ทำให้แชทไม่หาย
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- 4. ช่องแชทแบบใหม่ (เหมือน ChatGPT) ---
    if prompt := st.chat_input("พิมพ์ปรึกษาบัดดี้ที่นี่..."):
        # 4.1 แสดงข้อความที่เด็กพิมพ์
        with st.chat_message("user"):
            st.markdown(prompt)
        # บันทึกลงสมอง
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 4.2 ให้ AI คิดและตอบกลับ (จำบริบทเดิมได้)
        with st.spinner("บัดดี้กำลังคิด..."):
            try:
                # แอบแนบกฎเหล็กไปกับคำถามเด็กเสมอ เพื่อไม่ให้ AI หลุดบทบาท
                full_prompt = f"[คำสั่งบังคับ: {sys_prompt}]\nคำถามของนักเรียน: {prompt}"
                response = st.session_state.chat_session.send_message(full_prompt)
                
                # แสดงคำตอบ AI
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                # บันทึกคำตอบลงสมอง
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("🚨 เกิดข้อผิดพลาดในการประมวลผล")
                st.warning(str(e))

with col2:
    st.subheader("💻 พื้นที่ปฏิบัติการ (Coding Zone)")
    st.info("💡 เปิด Google Colab เพื่อเขียนโค้ด แล้วใช้ฟีเจอร์แบ่งครึ่งหน้าจอ (Split Screen) เพื่อคุยกับ AI ฝั่งซ้ายไปพร้อมๆ กัน")
    st.link_button("➡️ คลิกเปิด Google Colab สำหรับโจทย์วันนี้", "https://colab.research.google.com/")
    
    st.markdown("---")
    st.markdown("### 📝 คู่มือการถาม AI (Prompt Cheat Sheet)")
    st.markdown("- **สถาปนิก:** 'ช่วยออกแบบตรรกะโปรแกรมตัดเกรดให้หน่อย เริ่มยังไงดี?'")
    st.markdown("- **บัดดี้:** 'คำสั่งที่รับข้อมูลทางคีย์บอร์ดเขียนยังไงนะ ขอคำใบ้หน่อย'")
    st.markdown("- **นักสืบ:** 'รันแล้วขึ้น SyntaxError บรรทัดที่ 4 เกิดจากอะไร?'")
