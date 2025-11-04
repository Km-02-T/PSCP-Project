import sys
import threading
import time
import keyboard
import pyautogui
import pytesseract
import winsound
import os
from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QMessageBox, QVBoxLayout,
    QPushButton, QTextEdit, QDialog, QComboBox, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPainter, QPen, QFont, QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt, QPoint, QRectF

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
LANGUAGES_DICT = GoogleTranslator().get_supported_languages(as_dict=True)
languages_sort = sorted(LANGUAGES_DICT.items(), key=lambda item: item[0])
LANG_FULL_NAMES = [item[0].capitalize() for item in languages_sort]
LANG_CODES = [item[1] for item in languages_sort]
english_index = LANG_FULL_NAMES.index("English")
    
def exit_program():
    print("กำลังปิดโปรแกรม...")
    QApplication.quit()
    sys.exit(0)

def translate_text(text, source='auto', target='th'):
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated
    except Exception as e:
        return f"[แปลไม่สำเร็จ: {e}]"

class CaptureWindow(QWidget):
    paint = QRectF()
    def __init__(self):
        super().__init__()
        self.is_pressing = False
        self.start = QPoint()
        self.end = QPoint()
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.background_pixmap = QPixmap()
        screen = QApplication.primaryScreen()
        self.background_pixmap = screen.grabWindow(0)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.showFullScreen()
        self.screen_rect = self.rect()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            exit_program() 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.is_pressing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_pressing:
            self.end = event.pos()
            self.paint = QRectF(self.start, self.end)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_pressing:
            self.end = event.pos()
            self.close()

    def get_region(self):
        x1, y1 = self.start.x(), self.start.y()
        x2, y2 = self.end.x(), self.end.y()
        return (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background_pixmap.isNull():
            painter.drawPixmap(self.rect(), self.background_pixmap)

        mask_pixmap = QPixmap(self.screen_rect.size())
        mask_pixmap.fill(Qt.transparent)

        mask_painter = QPainter(mask_pixmap)

        veil_color = QColor(0, 0, 0, 150)
        mask_painter.fillRect(mask_pixmap.rect(), veil_color)

        mask_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        if not self.paint.isNull(): 
            mask_painter.fillRect(self.paint, Qt.white)
        mask_painter.end()
        painter.drawPixmap(0, 0, mask_pixmap)
        
        painter.setPen(QPen(Qt.white, 2, Qt.SolidLine))
        if not self.paint.isNull():
            painter.drawRect(self.paint)

def load_theme_file(name):
    path = os.path.join(os.path.dirname(__file__), 'theme', name)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: QSS file '{name}' not found.")
        return ""

class TranslateDialog(QDialog):
    def __init__(self, translated_text):
        super().__init__()
        self.current_theme = "dark"

        self.light_theme = load_theme_file("light_theme.qss")
        self.dark_theme = load_theme_file("dark_theme.qss")

        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Screen Translator ✨")
        self.resize(520, 460)
        self.setStyleSheet(self.dark_theme)

        layout = QVBoxLayout()

        top_h_layout = QHBoxLayout()
        top_h_layout.setContentsMargins(15, 10, 15, 5)

        title = QLabel("คำแปลจากภาพ")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        top_h_layout.addWidget(title)

        top_h_layout.addStretch(1)

        self.btn_theme = QPushButton("Switch to Light Mode")
        self.btn_theme.clicked.connect(self.theme_switch)

        top_h_layout.addWidget(self.btn_theme)

        layout.addLayout(top_h_layout)

        self.output = QTextEdit()
        self.output.setPlainText(translated_text)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)

        sub_label = QLabel("พิมพ์ภาษาไทยเพื่อแปลกลับ ↓")
        layout.addWidget(sub_label)

        self.input = QTextEdit()
        layout.addWidget(self.input)

        h_layout = QHBoxLayout() 

        self.lang_select = QComboBox()
        self.lang_select.addItems(LANG_FULL_NAMES)
        self.lang_select.setCurrentIndex(english_index)
        h_layout.addWidget(self.lang_select)

        btn_translate = QPushButton("แปลกลับ")
        btn_translate.clicked.connect(self.translate_back)
        h_layout.addWidget(btn_translate)

        btn_copy = QPushButton("คัดลอกคำแปล")
        btn_copy.clicked.connect(self.copy_text)
        h_layout.addWidget(btn_copy)

        btn_exit = QPushButton("ออกจากโปรแกรม")
        btn_exit.clicked.connect(exit_program)
        h_layout.addWidget(btn_exit)

        layout.addLayout(h_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)
 
    def theme_switch(self):
        if self.current_theme == "light":
            self.setStyleSheet(self.dark_theme)
            self.current_theme = "dark"
            self.btn_theme.setText("Switch to Light Mode")
        else:
            self.setStyleSheet(self.light_theme)
            self.current_theme = "light"
            self.btn_theme.setText("Switch to Dark Mode")

    def translate_back(self):
        text = self.input.toPlainText().strip()
        if not text:
            self.result_box.setPlainText("[กรุณาพิมพ์ข้อความภาษาไทยก่อน]")
            return

        target_lang = self.lang_select.currentIndex()
        translated_back = translate_text(text, source='th', target=LANG_CODES[target_lang])
        self.result_box.setPlainText(translated_back)
        winsound.MessageBeep()
        save_history(text, translated_back, LANG_CODES[target_lang])

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_box.toPlainText())

def save_history(input_thai, output_translated, lang):
    with open("translate_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(f"TH: {input_thai}\n")
        f.write(f"{lang.upper()}: {output_translated}\n\n")

def do_capture_translate():
    app = QApplication(sys.argv)
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
    msg = QMessageBox()
    msg.setWindowTitle("คำแปลจากภาพ")
    msg.setText(message)
    msg.exec_()

def show_dialog(translated_text):
    dialog = TranslateDialog(translated_text)
    dialog.exec_()

def hotkey_listener():
    print("พร้อมแล้ว! กด Ctrl+T เพื่อเริ่มแคปและแปลภาษา (กด Esc เพื่อออก)")
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
