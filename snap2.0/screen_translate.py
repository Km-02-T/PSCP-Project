import sys
import io
import threading
import time
import keyboard
import pyautogui
import pytesseract
import winsound
from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QMessageBox, QVBoxLayout,
    QPushButton, QTextEdit, QDialog, QComboBox, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPainter, QPen, QFont, QColor
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
            qp.setPen(QPen(Qt.cyan, 2, Qt.SolidLine))
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
        self.setWindowTitle("Screen Translator ✨")
        self.resize(520, 460)
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f5f7;
                color: #222;
                border-radius: 12px;
            }
            QLabel {
                font-size: 15px;
                font-weight: 500;
                color: #2c3e50;
            }
            QTextEdit {
                border: 1px solid #ccd2d8;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 6px;
                font-size: 14px;
                font-family: "Segoe UI";
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QComboBox {
                border: 1px solid #ccd2d8;
                border-radius: 6px;
                padding: 4px 6px;
                background-color: white;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout()
        title = QLabel("คำแปลจากภาพ")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setPlainText(translated_text)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #d0d6db;")
        layout.addWidget(separator)

        sub_label = QLabel("พิมพ์ภาษาไทยเพื่อแปลกลับ ↓")
        layout.addWidget(sub_label)

        self.input = QTextEdit()
        layout.addWidget(self.input)

        h_layout = QHBoxLayout()
        self.lang_select = QComboBox()
        self.lang_select.addItems(["en", "ja", "ko", "zh-CN", "fr", "de"])
        h_layout.addWidget(self.lang_select)

        btn_translate = QPushButton("แปลกลับ")
        btn_translate.clicked.connect(self.translate_back)
        h_layout.addWidget(btn_translate)

        btn_copy = QPushButton("คัดลอกคำแปล")
        btn_copy.clicked.connect(self.copy_text)
        h_layout.addWidget(btn_copy)

        layout.addLayout(h_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def translate_back(self):
        text = self.input.toPlainText().strip()
        if not text:
            self.result_box.setPlainText("[กรุณาพิมพ์ข้อความภาษาไทยก่อน]")
            return

        target_lang = self.lang_select.currentText()
        translated_back = translate_text(text, source='th', target=target_lang)
        self.result_box.setPlainText(translated_back)
        winsound.MessageBeep()

        save_history(text, translated_back, target_lang)

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_box.toPlainText())

def save_history(input_thai, output_translated, lang):
    with open("translate_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(f"TH: {input_thai}\n")
        f.write(f"{lang.upper()}: {output_translated}\n\n")

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
    winsound.MessageBeep()
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
