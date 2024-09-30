import sys
import os
import re
import shutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class DownloadWorker(QObject):
    progress = pyqtSignal(int)  # Emits download progress percentage
    status = pyqtSignal(str)  # Emits status messages
    finished = pyqtSignal()  # Emits when download is finished
    error = pyqtSignal(str)  # Emits error messages

    def __init__(self, youtube_url, output_dir, filename_template, audio_quality):
        super().__init__()
        self.youtube_url = youtube_url
        self.output_dir = output_dir
        self.filename_template = filename_template
        self.audio_quality = audio_quality

    def validate_youtube_url(self, url):
        """
        Validate if the provided URL is a valid YouTube URL.
        """
        youtube_regex = re.compile(
            r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$"
        )
        return youtube_regex.match(url) is not None

    def run(self):
        if not self.validate_youtube_url(self.youtube_url):
            self.error.emit("Invalid YouTube URL.")
            return

        # Define output template
        if not self.filename_template:
            self.filename_template = "%(title)s.%(ext)s"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.output_dir, self.filename_template),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self.audio_quality,
                }
            ],
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
            "nocolor": True,  # Disable colored output
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                self.status.emit("Starting download...")
                ydl.download([self.youtube_url])
            self.status.emit("Download and conversion completed successfully!")
            self.finished.emit()
        except DownloadError as e:
            self.error.emit(f"DownloadError: {e}")
        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent_str = d.get("_percent_str", "0.0%").strip()
            # Remove any non-numeric characters except the decimal point
            sanitized_percent_str = re.sub(r"[^\d.]", "", percent_str)
            try:
                percent = float(sanitized_percent_str)
                self.progress.emit(int(percent))
                eta = d.get("eta", "Unknown")
                speed = d.get("_speed_str", "Unknown speed")
                self.status.emit(
                    f"Downloading: {percent_str} - ETA: {eta} - Speed: {speed}"
                )
            except ValueError:
                # If conversion fails, skip updating the progress
                self.status.emit(
                    f"Downloading: {percent_str} - ETA: {d.get('eta', 'Unknown')} - Speed: {d.get('_speed_str', 'Unknown speed')}"
                )
        elif d["status"] == "finished":
            self.status.emit("Download finished, now converting...")


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Downloader")
        self.setGeometry(100, 100, 600, 200)
        self.init_ui()

    def init_ui(self):
        # YouTube URL Input
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video URL here")

        url_layout = QHBoxLayout()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # Output Directory Selection
        output_label = QLabel("Output Directory:")
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_folder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_button)

        # Filename Template and Quality (Optional)
        filename_label = QLabel("Filename Template:")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("%(title)s.%(ext)s")

        quality_label = QLabel("Audio Quality (kbps):")
        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("192")

        optional_layout = QHBoxLayout()
        optional_layout.addWidget(filename_label)
        optional_layout.addWidget(self.filename_input)
        optional_layout.addWidget(quality_label)
        optional_layout.addWidget(self.quality_input)

        # Download Button
        self.download_button = QPushButton("Download MP3")
        self.download_button.clicked.connect(self.start_download)

        # Progress Bar and Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(optional_layout)
        main_layout.addWidget(self.download_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", os.getcwd()
        )
        if folder:
            self.output_path.setText(folder)

    def start_download(self):
        youtube_url = self.url_input.text().strip()
        output_dir = self.output_path.text().strip() or os.getcwd()
        filename_template = self.filename_input.text().strip()
        audio_quality = self.quality_input.text().strip() or "192"

        if not youtube_url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.warning(
                self, "Input Error", "Please select a valid output directory."
            )
            return

        if not re.match(r"^\d+$", audio_quality):
            QMessageBox.warning(
                self, "Input Error", "Audio quality must be a number (e.g., 192)."
            )
            return

        # Disable UI elements during download
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Initializing...")

        # Set up worker and thread
        self.thread = QThread()
        self.worker = DownloadWorker(
            youtube_url=youtube_url,
            output_dir=output_dir,
            filename_template=filename_template,
            audio_quality=audio_quality,
        )
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.thread.quit)

        # Start the thread
        self.thread.start()

    def update_progress(self, percent):
        self.progress_bar.setValue(percent)

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def download_finished(self):
        QMessageBox.information(
            self, "Success", "Download and conversion completed successfully!"
        )
        self.download_button.setEnabled(True)
        self.status_label.setText("Status: Completed")
        self.progress_bar.setValue(100)

    def download_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.download_button.setEnabled(True)
        self.status_label.setText("Status: Error")
        self.progress_bar.setValue(0)


def check_dependency(command, name):
    """
    Check if a command-line tool is available.
    """
    if shutil.which(command) is None:
        app = QApplication(sys.argv)  # Initialize QApplication to use QMessageBox
        QMessageBox.critical(
            None, "Dependency Error", f"{name} is not installed or not found in PATH."
        )
        sys.exit(1)


def main():
    app = QApplication(sys.argv)

    # Check dependencies
    check_dependency("yt-dlp", "yt-dlp")
    check_dependency("ffmpeg", "FFmpeg")

    downloader = YouTubeDownloader()
    downloader.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
