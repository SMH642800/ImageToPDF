import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QSpinBox, QHBoxLayout, QMessageBox,
    QTextEdit, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PIL import Image
import img2pdf

Image.MAX_IMAGE_PIXELS = None
SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
MM_TO_PX = 300 / 25.4

class PDFConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("Image To PDF tools")
        self.resize(450, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.folder_label = QLabel("未選擇資料夾 (可拖曳) ")
        self.layout.addWidget(self.folder_label)

        self.select_button = QPushButton("選擇主資料夾")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        self.output_folder_label = QLabel("未選擇輸出位置 (預設為原資料夾位置)")
        self.layout.addWidget(self.output_folder_label)

        self.output_button = QPushButton("選擇輸出資料夾")
        self.output_button.clicked.connect(self.select_output_folder)
        self.layout.addWidget(self.output_button)

        self.name_checkbox = QCheckBox("自訂輸出 PDF 名稱 (否則使用子資料夾名稱)")
        self.name_input = QLineEdit()
        self.name_input.setEnabled(False)
        self.name_checkbox.stateChanged.connect(
            lambda state: self.name_input.setEnabled(state == Qt.CheckState.Checked.value)
        )
        self.layout.addWidget(self.name_checkbox)
        self.layout.addWidget(self.name_input)

        self.margin_layout = QHBoxLayout()
        self.margins = {}
        for label in ["上", "下", "左", "右"]:
            box = QSpinBox()
            box.setRange(0, 50)
            box.setValue(0)
            self.margin_layout.addWidget(QLabel(f"{label}邊距(mm):"))
            self.margin_layout.addWidget(box)
            self.margins[label] = box
        self.layout.addLayout(self.margin_layout)

        self.progress = QProgressBar()
        self.progress.setStyleSheet('''
            QProgressBar {
                border: 2px solid #000;
                border-radius: 5px;
                text-align:center;
                height: 20px;
                width: 200px;
            }
            QProgressBar::chunk {
                background: #09c;
                width:1px;
            }
        ''')
        self.progress.setFormat('%p%')
        self.layout.addWidget(self.progress)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("開始轉換")
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_conversion)
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        self.cancelled = False
        self.folder_path = None
        self.output_folder = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        path = event.mimeData().urls()[0].toLocalFile()
        if os.path.isdir(path):
            self.folder_path = path
            self.folder_label.setText(path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇主資料夾")
        if folder:
            select_folder = f'檔案資料夾位置： {folder}'
            self.folder_label.setText(select_folder)
            self.folder_path = folder

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            output_folder = f'輸出資料夾位置： {folder}'
            self.output_folder_label.setText(output_folder)
            self.output_folder = folder

    def log(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def cancel_operation(self):
        self.progress.setValue(0)
        self.progress.setStyleSheet('''
            QProgressBar {
                border: 2px solid #000;
                border-radius: 5px;
                text-align:center;
                height: 20px;
                width: 200px;
            }
            QProgressBar::chunk {
                background: #09c;
                width:1px;
            }
        ''')
        self.progress.setFormat('%p%')

        self.cancelled = True
        self.log("\n⚠️ 使用者取消操作")

    def start_conversion(self):
        if not self.folder_path:
            QMessageBox.warning(self, "錯誤", "請先選擇主資料夾")
            return

        top_folder = self.folder_path
        output_base = self.output_folder or top_folder
        subfolders = [f for f in os.listdir(top_folder)
                      if os.path.isdir(os.path.join(top_folder, f))]

        self.cancelled = False
        self.progress.setMaximum(len(subfolders))
        self.progress.setValue(0)
        self.cancel_button.setEnabled(True)

        top_margin = int(self.margins["上"].value() * MM_TO_PX)
        bottom_margin = int(self.margins["下"].value() * MM_TO_PX)
        left_margin = int(self.margins["左"].value() * MM_TO_PX)
        right_margin = int(self.margins["右"].value() * MM_TO_PX)

        def natural_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split(r'(\d+)', s)]
        
        subfolders = sorted(subfolders, key=natural_key)
        for idx, sub in enumerate(subfolders):
            if self.cancelled:
                break

            self.log(f"\n▶️ 處理：{sub}")
            QApplication.processEvents()

            subfolder_path = os.path.join(top_folder, sub)
            images = sorted([
                os.path.join(subfolder_path, f)
                for f in os.listdir(subfolder_path)
                if f.lower().endswith(SUPPORTED_FORMATS)
            ], key=lambda x: natural_key(os.path.basename(x)))  # 使用自然排序

            if not images:
                self.log("⚠️ 無圖片，跳過")
                continue

            pdf_images = []

            for img_path in images:
                try:
                    img = Image.open(img_path).convert("RGB")
                    new_width = img.width + left_margin + right_margin
                    new_height = img.height + top_margin + bottom_margin
                    new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
                    new_img.paste(img, (left_margin, top_margin))

                    temp_path = os.path.join(subfolder_path, f"__temp_{os.path.basename(img_path)}.jpg")
                    new_img.save(temp_path, format="JPEG")
                    pdf_images.append(temp_path)
                except Exception as e:
                    self.log(f"❌ 圖片處理失敗：{img_path}，錯誤：{e}")

            if pdf_images:
                pdf_name = self.name_input.text().strip() if self.name_checkbox.isChecked() else sub
                output_path = os.path.join(output_base, f"{pdf_name}.pdf")
                try:
                    with open(output_path, "wb") as f:
                        f.write(img2pdf.convert(pdf_images))
                    self.log(f"✅ 已完成：{output_path}")
                except Exception as e:
                    self.log(f"❌ PDF 轉檔失敗：{sub}，錯誤：{e}")

                for tmp in pdf_images:
                    os.remove(tmp)

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.cancel_button.setEnabled(False)
        if not self.cancelled:
            self.log("\n🎉 所有子資料夾處理完成！")
            QMessageBox.information(self, "完成", "所有子資料夾皆已成功轉換為 PDF！")

if __name__ == "__main__":
    app = QApplication([])
    window = PDFConverter()
    window.show()
    app.exec()
