import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox,
    QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QColor
import yt_dlp
import os

class DownloadThread(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, format_option, quality, destination_folder):
        super().__init__()
        self.url = url
        self.format_option = format_option
        self.quality = quality
        self.destination_folder = destination_folder
        self.output_file = ""

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                percentage = (downloaded_bytes / total_bytes) * 100
                self.progress.emit(percentage)

    def run(self):
        try:
            # Crear el nombre del archivo de salida con la ruta completa
            output_template = os.path.join(self.destination_folder, '%(title)s.%(ext)s')

            if self.format_option == "MP3":
                audio_quality = {
                    "Alta (320kbps)": "320",
                    "Media (192kbps)": "192",
                    "Baja (128kbps)": "128"
                }.get(self.quality, "128")

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_quality,
                    }],
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'quiet': False,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'progress_hooks': [self.progress_hook]
                }
            else:  # MP4
                format_str = {
                    "Alta (1080p)": "best[ext=mp4][height<=1080]",
                    "Media (720p)": "best[ext=mp4][height<=720]",
                    "Baja (480p)": "best[ext=mp4][height<=480]"
                }.get(self.quality, "best[ext=mp4]")

                ydl_opts = {
                    'format': format_str,
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'quiet': False,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'progress_hooks': [self.progress_hook]
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                self.output_file = ydl.prepare_filename(info)
                if self.format_option == "MP3":
                    self.output_file = os.path.splitext(self.output_file)[0] + ".mp3"
                else:
                    self.output_file = os.path.splitext(self.output_file)[0] + ".mp4"

            self.finished.emit(self.output_file)
        except Exception as e:
            self.error.emit(str(e))

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GufiPlay")
        self.setGeometry(100, 100, 600, 300)
        self.setStyleSheet("background-color: white;")
        
        # Carpeta de destino por defecto
        self.destination_folder = os.path.expanduser("~\\Downloads")

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Estilo común actualizado para ComboBox, LineEdit y botones
        self.common_style = """
            QComboBox, QLineEdit, QPushButton {
                background-color: #add8e6;
                border: none;
                border-radius: 15px;
                padding: 8px;
                color: white;
                font-weight: bold;
            }
            QComboBox:hover, QLineEdit:hover, QPushButton:hover {
                background-color: #87cefa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
                border-radius: 15px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #add8e6;
                border: none;
                selection-background-color: #87cefa;
                selection-color: white;
                outline: none;
                border-radius: 15px;
                padding: 8px;
            }
            QComboBox QAbstractItemView::item {
                height: 30px;
                padding-left: 10px;
                color: white;
                border-radius: 15px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #87cefa;
                border-radius: 15px;
            }
            QComboBox QScrollBar:vertical {
                border: none;
                background-color: #add8e6;
                width: 10px;
                border-radius: 5px;
                border-radius: 15px;
            }
            QComboBox QScrollBar::handle:vertical {
                background-color: #87cefa;
                border-radius: 5px;
            }
            QComboBox QScrollBar::add-line:vertical,
            QComboBox QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                border-radius: 15px;
            }
        """

        # Layout para URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(self.common_style)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # Layout para opciones
        options_layout = QHBoxLayout()

        # ComboBox para formato
        format_label = QLabel("Formato:")
        self.format_combo = QComboBox()
        self.format_combo.setStyleSheet(self.common_style)
        self.format_combo.addItems(["MP4", "MP3"])
        self.format_combo.currentTextChanged.connect(self.update_quality_options)
        options_layout.addWidget(format_label)
        options_layout.addWidget(self.format_combo)

        # ComboBox para calidad
        quality_label = QLabel("Calidad:")
        self.quality_combo = QComboBox()
        self.quality_combo.setStyleSheet(self.common_style)
        options_layout.addWidget(quality_label)
        options_layout.addWidget(self.quality_combo)

        # Layout para el botón de destino
        destination_layout = QHBoxLayout()
        self.destination_label = QLabel(f"Carpeta de destino: {self.destination_folder}")
        self.destination_button = QPushButton("Cambiar carpeta")
        self.destination_button.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;
                border: none;
                border-radius: 10px;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #87cefa;
            }
        """)
        self.destination_button.clicked.connect(self.select_destination)
        destination_layout.addWidget(self.destination_label)
        destination_layout.addWidget(self.destination_button)
        

        # Inicializar opciones de calidad
        self.update_quality_options()

        # Etiqueta de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: black; font-size: 14px;font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dce5f3;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #add8e6;
                border-radius: 8px;
            }
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        # Botón de descarga
        self.download_button = QPushButton("Descargar")
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #87cefa;
            }
        """)
        self.download_button.clicked.connect(self.start_download)

        # Agregar widgets al layout principal
        layout.addLayout(url_layout)
        layout.addLayout(options_layout)
        layout.addLayout(destination_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.download_button)

    def select_destination(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de destino",
            self.destination_folder
        )
        if folder:
            self.destination_folder = folder
            self.destination_label.setText(f"Carpeta de destino: {self.destination_folder}")

    def update_quality_options(self):
        self.quality_combo.clear()
        if self.format_combo.currentText() == "MP3":
            self.quality_combo.addItems([
                "Alta (320kbps)",
                "Media (192kbps)",
                "Baja (128kbps)"
            ])
        else:
            self.quality_combo.addItems([
                "Alta (1080p)",
                "Media (720p)",
                "Baja (480p)"
            ])

    def start_download(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Por favor, ingrese una URL válida")
            return

        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Descargando...")

        format_option = self.format_combo.currentText()
        quality = self.quality_combo.currentText()

        self.download_thread = DownloadThread(
            url, 
            format_option, 
            quality, 
            self.destination_folder
        )
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()

    def update_progress(self, percentage):
        self.progress_bar.setValue(int(percentage))

    def download_finished(self, file_path):
        try:
        # Obtener la marca de tiempo actual
            current_time = time.time()
            os.utime(file_path, (current_time, current_time))
            self.status_label.setText("¡Descarga completada!")
            self.download_button.setEnabled(True)
            self.progress_bar.setValue(100)
        except Exception as e:
            self.status_label.setText(f"Error al actualizar la fecha: {str(e)}")
            self.download_button.setEnabled(True)

    def download_error(self, error_msg):
        self.status_label.setText(f"Error: {error_msg}")
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())