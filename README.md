# Mali AI — Meta Llama 3.2 1B on Streamlit Cloud

เว็บ AI ผู้ช่วยภาษาไทยรันด้วย **Meta Llama 3.2 1B Instruct Q4_K_M** (ไฟล์ GGUF ประมาณ **808 MB**) บน CPU โดยไม่ต้องใช้ API Key แบบเสียเงิน

โมเดล: [bartowski/Llama-3.2-1B-Instruct-GGUF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF)

## เหตุผลที่เปลี่ยนค่าย
Qwen3.5-0.8B เคยมีอาการแสดงว่า "โมเดลไม่ได้ส่งข้อความกลับมา" และรุ่นนั้นอาจใช้ reasoning tokens หรือ chat template ที่ต่างจากโปรเจกต์เดิม คำตอบจึงถูกซ่อน/ว่างได้

แก้แล้ว:
- เปลี่ยนมาใช้ Meta Llama 3.2 1B (รองรับภาษาไทยตามเอกสารโมเดล) แทน Qwen
- **ลบการบังคับ `chat_format="chatml"`** เพื่อให้ llama-cpp-python อ่าน chat template ของโมเดลจาก GGUF
- **ลบตัวกรองแท็ก `<think>`** ซึ่งอาจซ่อนคำตอบจนหมด
- ถ้าสตรีมคำตอบว่าง จะลองสร้างข้อความอีกครั้งแบบไม่สตรีม (สูงสุด 1 ครั้ง) แล้วแจ้งข้อผิดพลาดให้ตรวจ Log หากยังว่างอยู่
- ย่อกฎตอบคำถาม ส่งข้อมูลจาก `knowledge.txt` ทุกคำถาม
- ดาวน์โหลดเฉพาะรุ่นใหม่และล้างแคชเฉพาะรุ่นเก่าที่เคยใช้ หากมีอยู่ใน instance
- โมเดลเดิมไม่ได้เก็บเป็นไฟล์ใน GitHub

**สำคัญ:** การเปลี่ยนรุ่นไม่ได้รับประกันว่า Llama 1B ฉลาดกว่ารุ่น 1.7B แต่เลือกเพื่อความเสถียรในการสร้างคำตอบบน CPU ฟรี ทดสอบคุณภาพอีกครั้งหลัง Deploy

## Deploy

1. เปิด https://share.streamlit.io แล้วเลือก Repository `chaiyananrih-ship-it/my-ai-api`
2. Branch `main`, Main file path `app.py`, แนะนำ Python 3.11
3. หากเคย Deploy แล้ว เข้า Manage app → Reboot app
4. เปิดแชตและกด **เริ่มการสนทนาใหม่**
5. ลองถาม `ถ้าผมแจ้งเรื่องวันเสาร์ จะมีเจ้าหน้าที่ดำเนินการให้ทันทีไหม?`

การโหลดครั้งแรกจะดาวน์โหลดโมเดล ~808 MB จาก Hugging Face อาจใช้เวลานาน และเครื่องฟรีอาจมีปัญหา RAM/CPU ให้ดู Manage app → Logs

## ข้อมูลที่ AI ต้องใช้ตอบ

แก้ไข [knowledge.txt](knowledge.txt) ใน GitHub ข้อมูลที่ไม่ขึ้นต้นด้วย `#` จะถูกแนบไปในคำถามทุกครั้ง ตอนนี้เป็นข้อมูลจำลองเกี่ยวกับการแจ้งเรื่องวันเสาร์ ไม่ใช่ข้อมูลจริงของโรงเรียนหรือหน่วยงาน

โปรดแทนที่ด้วยข้อมูลที่ตรวจสอบแล้วก่อนนำไปใช้จริง และห้ามใส่รหัสผ่าน/ข้อมูลส่วนบุคคลใน Repository สาธารณะ

## ข้อจำกัด

- Llama 3.2 1B รองรับภาษาไทย แต่ยังเป็นโมเดลเล็ก ความสามารถในการวิเคราะห์ซับซ้อนมีขีดจำกัด
- Streamlit Cloud ฟรีไม่รับประกันรัน 24 ชั่วโมงหรือความเร็ว
- ค่าเริ่มต้นจำกัดการตอบ 160 tokens ประวัติล่าสุด 6 ข้อความและ context 2048 tokens
- โมเดลไม่ได้ท่องเว็บ เรียก API จากภายนอก หรือมีความจำข้ามเซสชัน
- ยังไม่ได้ยืนยันการทำงานของโมเดลจริงบนเครื่อง Streamlit Cloud ของคุณ

## ไฟล์

`app.py` หน้าเว็บ, `model.py` โหลดโมเดลและประมวลผล, `knowledge.txt` ข้อมูลอ้างอิง, `requirements.txt` dependencies และ `tests/test_source.py` ตรวจสอบโครงสร้าง

## License และเอกสาร

โมเดลนี้อยู่ภายใต้ [Meta Llama 3.2 Community License](https://www.llama.com/llama3_2/license/) ต้องปฏิบัติตามเงื่อนไขก่อนเผยแพร่หรือใช้งาน
อ้างอิง: [Llama GGUF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) · [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
