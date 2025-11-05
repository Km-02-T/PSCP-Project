# วิธีการติดตั้งและใช้งาน
clone จาก github ไปบนเครื่อง
  1.1 ให้ติดตั้ง python 3.6 ขึ้นไป
  1.2 ติดตั้ง Tesseract OCR Engine และต้องตรวงสอบแก้โค้ด pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
      โดยการตั้ง Path ตามที่ตัวเองติดตั้ง tesseract.exe ไว้
  1.3 Command Prompt (CMD) หรือ Terminal ในโฟลเดอร์ที่เก็บไฟล์โค้ด จากนั้นให้ผู้ใช้รันคำสั่ง pip install -r requirements.txt=
