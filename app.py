"""Minimal Thai-friendly, CPU-only Qwen chat on Streamlit Community Cloud."""
from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from model import MODEL_NAME, create_prompt, generate_chunks, load_engine

st.set_page_config(
    page_title="Mali AI · แชตบอตส่วนตัว",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], [data-testid="stApp"] { font-family: 'Prompt', sans-serif; }
    .block-container { max-width: 840px; padding-top: 2rem; padding-bottom: 6rem; }
    .brand-label { letter-spacing: .19em; color: #9b8ef7; font-weight: 700; font-size: .75rem; }
    .hero-title { font-weight: 700; font-size: clamp(2.25rem, 6vw, 3.45rem); line-height: 1.24; margin: .45rem 0 .5rem; }
    .hero-title span { color: #a99aff; }
    .hero-subtitle { color: #9fa1b1; font-size: .94rem; max-width: 550px; margin-bottom: 1.5rem; }
    .mini-tag { display: inline-block; background: rgba(157, 143, 250,.11); border: 1px solid rgba(157, 143, 250,.25); color:#b5abff; border-radius: 999px; padding: .3rem .68rem; font-size: .75rem; margin-bottom: .45rem; }
    .stChatMessage { border: 1px solid rgba(155, 143, 247, 0.10); border-radius: 18px; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(160, 160, 170, .12); }
    .fine-print { color: #85899b; font-size: .76rem; line-height: 1.6; }
    @media (max-width: 650px) { .block-container { padding-top: 1.15rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### ✦ Mali AI")
    st.caption("AI รันบน CPU ของเซิร์ฟเวอร์ · ไม่ใช้ API Key")
    st.divider()
    st.markdown("**การตั้งค่าการตอบ**")
    max_tokens = st.slider("ความยาวสูงสุด", min_value=64, max_value=256, value=160, step=32)
    temperature = st.slider("ความสร้างสรรค์", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
    st.markdown("**โมเดล**")
    st.code(MODEL_NAME, language=None)
    st.caption("Qwen3.5 · 0.8B · Q5_K_M · CPU")
    st.caption("ใช้กฎแบบสั้นและข้อมูลอ้างอิงทุกคำถาม · ส่งประวัติล่าสุดไม่เกิน 6 ข้อความ")
    st.warning("ข้อมูลใน knowledge.txt ตอนนี้เป็นสถานการณ์สมมติสำหรับทดสอบ ไม่ใช่ข้อมูลบริการจริง")
    st.divider()
    if st.button("↺ เริ่มการสนทนาใหม่", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.messages:
        content = json.dumps(
            {"exported_at": datetime.now().isoformat(timespec="seconds"),
             "model": MODEL_NAME, "messages": st.session_state.messages},
            ensure_ascii=False,
            indent=2,
        )
        st.download_button(
            "↓ บันทึกบทสนทนา (.json)",
            data=content,
            file_name="mali-ai-chat.json",
            mime="application/json",
            use_container_width=True,
        )
    st.markdown(
        '<p class="fine-print">ไฟล์โมเดลจะดาวน์โหลดจาก Hugging Face ในครั้งแรกที่เริ่มแชต '
        'และอาจต้องดาวน์โหลดใหม่เมื่อ Cloud รีสตาร์ต</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="brand-label">YOUR SMALL AI, REAL LOCAL INFERENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">สวัสดี เราคือ <span>Mali AI</span> ✦</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">แชตบอต AI รุ่นเล็กที่ประมวลผลบนเซิร์ฟเวอร์ Streamlit '
    'โดยไม่ต้องมีคีย์ API หรือบัตรเครดิต</div>',
    unsafe_allow_html=True,
)
st.markdown('<span class="mini-tag">● CPU only</span> &nbsp; <span class="mini-tag">✦ รองรับภาษาไทย</span> &nbsp; <span class="mini-tag">◈ Open model</span>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.info("💡 ลองถามว่า 'ช่วยแนะนำไอเดียทำเว็บโรงเรียน 3 แบบ' หรือ 'อธิบาย Python ให้เข้าใจง่าย' — โมเดลขนาดเล็กอาจตอบช้าและผิดพลาดได้")

for item in st.session_state.messages:
    with st.chat_message(item["role"], avatar="🤖" if item["role"] == "assistant" else "👤"):
        st.markdown(item["content"])

question = st.chat_input("พิมพ์ข้อความถึง Mali AI...", max_chars=500)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("กำลังเตรียมโมเดล AI (ครั้งแรกอาจดาวน์โหลดประมาณ 650 MB)..."):
                engine, engine_lock = load_engine()
            messages = create_prompt(engine, st.session_state.messages, max_tokens)
            answer = st.write_stream(
                generate_chunks(engine, engine_lock, messages, temperature, max_tokens)
            )
            if not answer.strip():
                answer = "ขออภัย โมเดลไม่ได้ส่งข้อความกลับมา กรุณาลองใหม่อีกครั้ง"
                st.warning(answer)
        except ValueError as exc:
            st.warning(str(exc))
        except Exception as exc:
            st.error("โหลดโมเดลหรือประมวลผลไม่สำเร็จ ตรวจสอบ Logs ใน Streamlit Cloud แล้วลองอีกครั้ง")
            with st.expander("รายละเอียดทางเทคนิค"):
                st.code(f"{type(exc).__name__}: {exc}")
        else:
            st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown('<p class="fine-print" style="text-align:center;margin-top:2rem;">Mali AI • Qwen3.5-0.8B • คำตอบอาจคลาดเคลื่อน • ไม่เหมาะกับข้อมูลอ่อนไหว</p>', unsafe_allow_html=True)
