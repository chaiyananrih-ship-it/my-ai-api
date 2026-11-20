# Mali AI — Streamlit + Qwen3-1.7B

AI Assistant ภาษาไทยที่รันบน CPU ของ Streamlit Community Cloud โดยไม่ต้องมี API Key ใช้โมเดล **Qwen3-1.7B-Q4_K_M** จาก [ggml-org](https://huggingface.co/ggml-org/Qwen3-1.7B-GGUF) ขนาดประมาณ **1.28 GB** (โมเดล Qwen2.5 เดิมไม่ถูกใช้งานแล้ว)

> Streamlit Community Cloud ฟรีมีหน่วยความจำที่จัดสรรตามเครื่อง (สูงสุดราว 2.7 GB ไม่ได้รับประกัน) โมเดลนี้อาจโหลดไม่ได้ในบาง instance และอาจตอบช้าบน CPU

## Deploy

1. เข้า https://share.streamlit.io แล้วเข้าระบบด้วย GitHub
2. เลือก Repository `chaiyananrih-ship-it/my-ai-api` และ Branch `main`
3. Main file path: `app.py`; แนะนำ Python 3.11
4. Deploy แล้วเปิดเว็บเพื่อทดลองส่งคำถาม
5. หากเคย Deploy แล้ว ให้ใช้ Manage app → Reboot app เพื่อโหลดโมเดลใหม่

**ครั้งแรก** ระบบดาวน์โหลด `Qwen3-1.7B-Q4_K_M.gguf` (~1.28 GB) จาก Hugging Face ตอนส่งข้อความครั้งแรก และจะลบแคชของโมเดล Qwen2.5-0.5B / 1.5B ที่เคยดาวน์โหลดใน instance นี้เท่านั้น (หากมี) ไม่มีไฟล์โมเดลใหญ่บน GitHub

## ปรับให้ AI ตอบตามข้อมูลของเรา

เปิด [knowledge.txt](knowledge.txt) ใน GitHub → กด Edit (รูปดินสอ) → เพิ่ม **ข้อเท็จจริงขององค์กร** แบบ 1 ข้อต่อบรรทัด → Commit changes

**สำคัญ:** ข้อมูลที่ขึ้นต้นด้วย `#` เป็นเพียงคอมเมนต์ ไม่ถูกส่งให้ AI ต้องลบเครื่องหมาย `#` หน้าบรรทัดที่ต้องการเปิดใช้งานก่อน ตัวอย่าง:

```text
ระบบเปิดรับคำร้องได้ตลอด 24 ชั่วโมง
เจ้าหน้าที่ทำงานวันจันทร์–ศุกร์ เวลา 08.30–16.30 น.
วันเสาร์และวันอาทิตย์ไม่มีเจ้าหน้าที่ให้บริการตามปกติ
```

แอปจะโหลดกฎจาก `model.py` และข้อเท็จจริงจาก `knowledge.txt` ประกอบกับคำถาม **ทุกครั้ง** ไม่ต้องให้ผู้ใช้งานพิมพ์กฎใหม่ เมื่อแก้ `knowledge.txt` บน GitHub ให้รอ Streamlit redeploy ก่อนทดสอบอีกครั้ง

เพื่อควบคุม RAM และ context จะส่งข้อมูลอ้างอิงได้สูงสุด 2,000 ตัวอักษร และมี context 2,048 tokens; ควรเขียนข้อมูลให้สั้น ชัดเจน อย่าใส่ข้อมูลส่วนบุคคล รหัสผ่าน หรือ API Key เพราะ Repository นี้เป็น Public

## โครงสร้าง

```
app.py                  Streamlit Chat UI
model.py                โหลด Qwen3, system prompt, knowledge, inference
knowledge.txt           ข้อมูลที่ผู้ดูแลเพิ่มเพื่อให้ AI ใช้ตอบคำถาม
requirements.txt        Python packages
.streamlit/config.toml  Theme
tests/test_source.py    โครงสร้างและสเปกโมเดล
```

## รันบนเครื่องส่วนตัว

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## ข้อจำกัด

- โมเดล 1.7B คาดว่าตอบและทำตามคำสั่งได้ดีกว่า Qwen2.5-1.5B โดยทั่วไป แต่ไม่ได้รับประกันว่าจะตอบถูกทุกเรื่อง
- ระบบตั้งใจให้ตอบแบบตรงประเด็น ไม่แสดงเนื้อหาภายในแท็ก `<think>`; โหมดไม่แสดงกระบวนการคิดช่วยให้ใช้ CPU ฟรีได้เร็วขึ้น
- ไม่มีอินเทอร์เน็ตให้ AI ค้นหาข้อมูลสด และไม่มี API endpoint ภายนอก: Streamlit เป็นเว็บแชต
- ประวัติแชตเก็บใน Session ของ browser และไม่ถาวร
- ยังไม่ได้ยืนยันว่ารุ่นใหม่นี้รันได้จริงบน instance Streamlit Cloud ของผู้ใช้ ให้ตรวจ Manage app → Logs หากมีปัญหา
- รุ่น Qwen3.5 ที่ใหญ่กว่านี้มีความสามารถสูงขึ้นได้ แต่ใช้ทรัพยากรและความเข้ากันได้ของ runtime เพิ่มขึ้น

อ้างอิง: [Qwen3-1.7B GGUF](https://huggingface.co/ggml-org/Qwen3-1.7B-GGUF) · [Streamlit Deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
