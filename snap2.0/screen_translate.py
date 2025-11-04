import sys
import io
import threading
import time
import keyboard
import pyautogui
import pytesseract
from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMessageBox, QVBoxLayout, QPushButton, QTextEdit, QDialog
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def translate_text(text, source='auto', target='th'):
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated
    except Exception as e:
        return f"[แปลไม่สำเร็จ: {e}]"

class CaptureWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("เลือกพื้นที่หน้าจอ")
        self.setWindowOpacity(0.3)
        self.showFullScreen()
        self.start = QPoint()
        self.end = QPoint()
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.setStyleSheet("background-color: rgba(0,0,0,100);")

    def paintEvent(self, event):
        if not self.start.isNull() and not self.end.isNull():
            qp = QPainter(self)
            qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            rect = QRect(self.start, self.end)
            qp.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.close()

    def get_region(self):
        x1, y1 = self.start.x(), self.start.y()
        x2, y2 = self.end.x(), self.end.y()
        return (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

class TranslateDialog(QDialog):
    def __init__(self, translated_text):
        super().__init__()
        self.setWindowTitle("คำแปลจากภาพ")
        self.resize(400, 300)

        layout = QVBoxLayout()
        label = QLabel("คำแปลจากภาพ:")
        layout.addWidget(label)

        self.output = QTextEdit()
        self.output.setPlainText(translated_text)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        label2 = QLabel("พิมพ์ภาษาไทยเพื่อแปลกลับเป็นอังกฤษ:")
        layout.addWidget(label2)

        self.input = QTextEdit()
        layout.addWidget(self.input)

        btn = QPushButton("แปลกลับเป็นอังกฤษ")
        btn.clicked.connect(self.translate_back)
        layout.addWidget(btn)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def translate_back(self):
        text = self.input.toPlainText().strip()
        if not text:
            self.result_box.setPlainText("[กรุณาพิมพ์ข้อความภาษาไทยก่อน]")
            return
        translated_back = translate_text(text, source='th', target='en')
        self.result_box.setPlainText(translated_back)

def do_capture_translate():
    app = QApplication.instance() or QApplication(sys.argv)
    capture = CaptureWindow()
    capture.show()
    app.exec_()
    region = capture.get_region()
    if region[2] == 0 or region[3] == 0:
        return
    image = pyautogui.screenshot(region=region)
    text = pytesseract.image_to_string(image, lang='eng').strip()
    if not text:
        show_popup("ไม่พบข้อความในภาพ")
        return
    translated = translate_text(text)
    show_dialog(translated)

def show_popup(message):
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setWindowTitle("คำแปลจากภาพ")
    msg.setText(message)
    msg.exec_()

def show_dialog(translated_text):
    app = QApplication.instance() or QApplication(sys.argv)
    dialog = TranslateDialog(translated_text)
    dialog.exec_()

def hotkey_listener():
    print("พร้อมแล้ว! กด Ctrl+T เพื่อเริ่มแคปและแปลภาษา")
    while True:
        keyboard.wait("ctrl+t")
        do_capture_translate()
        time.sleep(0.5)

if __name__ == "__main__":
    t = threading.Thread(target=hotkey_listener, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
