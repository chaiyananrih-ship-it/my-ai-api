# ✦ Mali AI — Free Thai Chat on Streamlit

แชตบอต AI ที่รันโมเดล **Qwen2.5-0.5B-Instruct (4-bit GGUF)** บน **CPU ของ Streamlit Community Cloud** โดยตรง ไม่เรียก API แบบเสียเงิน ไม่ต้องใส่ API Key และไม่ต้องผูกบัตรเครดิตสำหรับการเริ่มใช้แพลตฟอร์มฟรี

> ⚠️ โมเดลเล็ก (~0.5B พารามิเตอร์) รองรับภาษาไทย แต่ความแม่นยำและความเร็วมีข้อจำกัด โดยเฉพาะงานใช้เหตุผลซับซ้อน บริการฟรีไม่รับประกันว่าจะทำงาน 24/7 และ Cloud อาจมีข้อจำกัด RAM/CPU

## 🚀 วิธี Deploy ผ่าน GitHub (ไม่ต้องติดตั้ง Python ในเครื่อง)

1. เข้า [share.streamlit.io](https://share.streamlit.io) → ลงชื่อเข้าใช้ด้วย GitHub
2. กด **Create app / New app** → **Deploy a public app from GitHub** แล้วเลือก repository `chaiyananrih-ship-it/my-ai-api`
3. กำหนด **Main file path:** `app.py`
4. ใน **Advanced settings** เลือก **Python 3.11** (แนะนำ) แล้วกด Deploy
5. เปิดเว็บที่ได้รับและพิมพ์คำถามแรกเพื่อโหลดโมเดล

**ครั้งแรกที่ส่งข้อความ:** ระบบจะดาวน์โหลดโมเดล `qwen2.5-0.5b-instruct-q4_k_m.gguf` (~491 MB) จาก Hugging Face โดยอัตโนมัติ อาจช้าหรือโหลดไม่ผ่านหาก Cloud จำกัดทรัพยากร/อินเทอร์เน็ต เมื่อ instance รีสตาร์ตไฟล์ cache อาจหายและต้องดาวน์โหลดใหม่

## 📁 โครงสร้างไฟล์

```text
my-ai-api/
├── app.py                 # UI แชต Streamlit
├── model.py               # ดาวน์โหลด GGUF, โหลดโมเดล และ stream คำตอบ
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # สีธีม
├── .gitignore
├── tests/
│   └── test_source.py
└── README.md
```

## 💻 รันบนคอมพิวเตอร์

แนะนำ Python 3.11 บน Linux x86_64 หรือแพลตฟอร์มที่ติดตั้ง `llama-cpp-python` ได้

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 🔧 ปรับแต่ง

- เปลี่ยนชื่อเว็บ หน้าแรก และข้อความ UI ที่ `app.py`
- เปลี่ยน system prompt ใน `model.py` ตัวแปร `SYSTEM_PROMPT`
- ปรับความยาวคำตอบและ temperature ได้ที่ sidebar
- ไฟล์โมเดลไม่รวมใน repo เพราะมีขนาดใหญ่ โหลดจาก Hugging Face ตอนใช้งาน
- แชร์โมเดลตัวเดียวกันระหว่างผู้ใช้ เพื่อลด RAM และใช้ lock ป้องกันรันอนุมานพร้อมกัน

## ⚠️ ข้อจำกัดที่ควรทราบ

- **ไม่มี API endpoint สำหรับเว็บไซต์ภายนอก:** Streamlit เป็นเว็บ UI ไม่ใช่ FastAPI hosting แม้ repo จะชื่อ `my-ai-api`
- CPU ฟรีตอบช้าได้ และมีการจำกัด context 2048 tokens เพื่อควบคุม RAM
- ระบบจำบทสนทนาเฉพาะ session ของผู้ใช้ ไม่บันทึกถาวร
- หากมีผู้ใช้หลายคนพร้อมกัน คำตอบจะต่อคิวกัน
- การติดตั้ง wheel อาจล้มเหลวตามความพร้อมของเครือข่าย/ระบบ
- ยังไม่ได้ยืนยันการ deploy จริงบน Streamlit Cloud
- ไม่ควรใช้กับข้อมูลส่วนบุคคลที่อ่อนไหว หรือคาดหวังคำตอบถูกต้อง 100%

## 🔗 แหล่งอ้างอิง

- [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Qwen2.5-0.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- [Official Qwen GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)

Model weights are distributed separately by their publisher. Review the model's license for your intended use.
