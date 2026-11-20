# Mali AI — AI ขนาดเล็กสำหรับ Streamlit

Mali AI ใช้ **Qwen3.5-0.8B** แบบ **Q5_K_M GGUF** (~650 MB) จาก
[bartowski/Qwen_Qwen3.5-0.8B-GGUF](https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF)
ทำงานบน CPU ของ Streamlit Community Cloud โดยไม่ต้องมี API Key

โมเดลใหม่เล็กกว่า Qwen3-1.7B (~1.28 GB) แต่ **ไม่รับประกันว่าฉลาดกว่าทุกงาน**
จุดเน้นคือความเร็วและการตอบโดยยึดข้อมูลอ้างอิงที่กำหนด ไม่ใช่การคิดยาวโดยไม่จำเป็น

## Deploy ผ่าน GitHub

1. เข้า https://share.streamlit.io แล้วเชื่อม GitHub
2. Repository: `chaiyananrih-ship-it/my-ai-api` · Branch: `main`
3. Main file path: `app.py` · Python 3.11 แนะนำ
4. กด Deploy แล้วทดลองส่งคำถาม (ครั้งแรกจะดาวน์โหลดโมเดล ~650 MB)
5. ถ้ามีแอปอยู่แล้ว เข้า **Manage app → Reboot app** และกด **เริ่มการสนทนาใหม่**

> Streamlit Cloud ฟรีไม่รับประกัน RAM/CPU, ความเร็ว หรือการเปิดตลอด 24 ชั่วโมง
> หากโหลดโมเดลไม่ได้ ให้ตรวจ Logs ใน Manage app

## ปรับข้อมูลที่ให้ AI รู้

แก้ไฟล์ [knowledge.txt](knowledge.txt) ใน GitHub
โดยแต่ละบรรทัดที่ **ไม่ขึ้นต้นด้วย `#`** จะถูกส่งพร้อมกฎสั้นๆ ทุกคำถาม
ข้อมูลปัจจุบันเป็น **สถานการณ์จำลอง** เกี่ยวกับเวลาแจ้งเรื่องและเวลาทำงานของเจ้าหน้าที่

ตัวอย่างคำถามทดสอบ:

```text
ถ้าผมแจ้งเรื่องวันเสาร์ จะมีเจ้าหน้าที่ดำเนินการให้ทันทีไหม?
```

คำตอบที่เหมาะสม:

```text
ส่งคำร้องวันเสาร์ได้ครับ เพราะเว็บไซต์รับคำร้องตลอด 24 ชั่วโมง
แต่เจ้าหน้าที่ให้บริการตามเวลาปกติวันจันทร์–ศุกร์
จึงยังยืนยันไม่ได้ว่าจะมีเจ้าหน้าที่ดำเนินการทันทีในวันเสาร์ครับ
```

เมื่อใช้งานจริงให้ลบข้อมูลจำลองและแทนด้วยข้อมูลที่ตรวจสอบแล้ว
ห้ามใส่ข้อมูลส่วนบุคคลหรือข้อมูลลับ เพราะ GitHub Repository เป็น Public

## ปรับความเร็ว

- ระบบใช้ system prompt แบบย่อเพื่อให้ AI อ่านกฎเร็วขึ้น
- ส่งประวัติแชตล่าสุดสูงสุด **6 ข้อความ** และเนื้อหาจาก `knowledge.txt` ไม่เกิน **1,200 ตัวอักษร**
- ค่าเริ่มต้นจำกัดการตอบที่ **160 tokens** และมี slider ให้ปรับได้
- โมเดลแชร์ร่วมกันในเซิร์ฟเวอร์ผ่าน `st.cache_resource`
- ใช้ `n_ctx=2048`, `n_batch=64`, 2 CPU threads สูงสุด
- ล้างแคชเฉพาะโมเดลรุ่นเก่าที่เคยใช้ หากยังอยู่ใน instance โดยไม่ลบไฟล์อื่น

**ข้อจำกัด:** คำตอบสั้นไม่ได้แปลว่า AI มีเหตุผลถูกต้องเสมอ และ 0.8B อาจด้อยกว่าโมเดลใหญ่ในโจทย์ยาก
โมเดลนี้เป็นเว็บแชต Streamlit ไม่ใช่ API Server

## ไฟล์สำคัญ

- `app.py`: หน้าเว็บแชต
- `model.py`: โหลดโมเดล กฎและการประมวลผล
- `knowledge.txt`: ข้อมูลอ้างอิงสำหรับทุกคำถาม
- `requirements.txt`: ไลบรารี Python
- `tests/test_source.py`: ทดสอบโครงสร้างโปรเจกต์

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

แหล่งอ้างอิง: [Qwen3.5-0.8B model card](https://huggingface.co/Qwen/Qwen3.5-0.8B)
· [GGUF download](https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF)
· [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
