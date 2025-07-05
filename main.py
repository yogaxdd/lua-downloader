import sys, os, subprocess, requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtCore import Qt, QUrl

STEAMTOOLS_PATH = r"C:\Program Files\SteamTools\SteamTools.exe"

class LuaDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YogaxD Lua Downloader")
        self.setGeometry(650, 390, 520, 325)
        self.default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.setup_ui()
        self.apply_custom_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("YogaxD Lua Downloader")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.appid_input = QLineEdit()
        self.appid_input.setPlaceholderText("Masukkan AppID (Contoh: 1401590)")
        self.appid_input.setFont(QFont("Segoe UI", 12))
        self.appid_input.textChanged.connect(self.check_validity)

        self.status_label = QLabel("Silahkan masukkan AppID.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        self.download_button = QPushButton("⬇️ Download ZIP")
        self.download_button.clicked.connect(self.download_lua)

        self.choose_folder_button = QPushButton("📁 Ganti Folder Simpan")
        self.choose_folder_button.clicked.connect(self.choose_folder)

        self.steamdb_button = QPushButton("🌐 Buka SteamDB")
        self.steamdb_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://steamdb.info/")))

        self.open_steamtools_button = QPushButton("🛠️ Buka SteamTools")
        self.open_steamtools_button.clicked.connect(self.open_steamtools)

        layout.addWidget(title)
        layout.addWidget(self.appid_input)
        layout.addWidget(self.status_label)
        layout.addWidget(self.download_button)
        layout.addWidget(self.choose_folder_button)
        layout.addWidget(self.steamdb_button)
        layout.addWidget(self.open_steamtools_button)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def apply_custom_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #2e2e2e;
                border: 1px solid #555;
                padding: 6px;
                border-radius: 6px;
                color: #fff;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QProgressBar {
                background-color: #2e2e2e;
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00bc8c;
                border-radius: 5px;
            }
        """)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Simpan")
        if folder:
            self.default_folder = folder
            QMessageBox.information(self, "Folder Diganti", f"Folder simpan diubah ke:\n{folder}")

    def check_validity(self):
        appid = self.appid_input.text().strip()
        if not appid.isdigit():
            self.status_label.setText("❌ AppID tidak valid")
            return

        zip_url = f"https://steamdatabase.s3.eu-north-1.amazonaws.com/{appid}.zip"
        try:
            head = requests.head(zip_url, timeout=5)
            if head.status_code == 200:
                self.status_label.setText(f"✅ AppID ditemukan!")
            else:
                self.status_label.setText("❌ AppID tidak tersedia.")
        except:
            self.status_label.setText("⚠️ Gagal menghubungi server")

    def download_lua(self):
        appid = self.appid_input.text().strip()
        if not appid.isdigit():
            QMessageBox.warning(self, "Error", "AppID harus berupa angka!")
            return

        url = f"https://steamdatabase.s3.eu-north-1.amazonaws.com/{appid}.zip"
        save_path = os.path.join(self.default_folder, f"{appid}.zip")

        try:
            head = requests.head(url)
            if head.status_code != 200:
                QMessageBox.information(self, "Not Found", f"AppID {appid} tidak ditemukan.")
                return

            self.progress.setVisible(True)
            self.progress.setValue(0)

            with requests.get(url, stream=True) as r:
                total = int(r.headers.get('content-length', 0))
                with open(save_path, 'wb') as f:
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int(downloaded * 100 / total)
                            self.progress.setValue(percent)

            QMessageBox.information(self, "Sukses", f"Download selesai ke:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal download: {e}")
        finally:
            self.progress.setVisible(False)

    def open_steamtools(self):
        if os.path.exists(STEAMTOOLS_PATH):
            try:
                subprocess.Popen([STEAMTOOLS_PATH])
            except Exception as e:
                QMessageBox.critical(self, "Gagal", f"Gagal membuka SteamTools:\n{e}")
        else:
            QMessageBox.warning(self, "Tidak Ditemukan", f"SteamTools tidak ditemukan di:\n{STEAMTOOLS_PATH}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = LuaDownloader()
    downloader.show()
    sys.exit(app.exec())
