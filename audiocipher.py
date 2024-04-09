import logging

# Setup logging at the top
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QComboBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTimer
import pygame
from pyo import *
from combining_sounds import combining_sounds, play_sound
from recognize_text import recognize_text_from_sound, recognize_text_from_mic
from morse_playback import read_scales_from_file, morse_code_to_musical_sequence, play_sequence
from pdfminer.high_level import extract_text
import os

# Now use logging.debug() instead of print() throughout your script
logging.debug(os.environ)


class TextToSoundConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Define the base directory for file paths
        # If the application is frozen (i.e., packaged by PyInstaller), use sys._MEIPASS
        # Otherwise, use the directory of this script file
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # Construct the path to the scales_frequencies.txt file
        scales_frequencies_path = os.path.join(base_dir, 'morse', 'scales_frequencies.txt')

        # Now use the resolved path to read the scales from the file
        self.scales = read_scales_from_file(scales_frequencies_path)
        
        self.setWindowTitle("Text to Sound Converter")
        self.setGeometry(100, 100, 800, 600)
        

        self.is_playing = False  # Initialize is_playing flag
        self.server = Server().boot()
        self.server.start()

        # Set application icon
        icon_path = "MusicEncoderIcon.png"  # Replace with the actual path to your icon file
        self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        # Set a font for the QTextEdit
        font = QFont()
        font.setPointSize(12)
            # Set Stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #333;
            }
            QTextEdit {
                font-size: 14px;
            }
            QPushButton {
                background-color: #4579a0;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4591a0;
            }
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 14px;
                background-color: #eee;
            }

            QComboBox:hover {
                background-color: #e0e0e0;
            }

            QComboBox:focus {
                border-color: #999;
            }

             QComboBox:on {
                /* Optional: style for the selected item */
                background-color: #ddd;
            }   
        """)

    

        self.text_entry = QTextEdit(self)
        self.text_entry.setFont(font)
        self.text_entry.setPlaceholderText("Enter your text here...")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.text_entry)

        # Create dropdown menu
        self.sound_type_combo = QComboBox(self)
        self.sound_type_combo.addItem("modulated")
        #self.sound_type_combo.addItem("beeps")
        self.sound_type_combo.addItem("non_human")
        
        # Morse dropdown
        self.morse_scale_combo = QComboBox(self)
        self.morse_scale_combo.addItems(self.scales.keys())
        self.main_layout.addWidget(self.morse_scale_combo)

        self.sound_type_combo.addItem("morse (select scale)")
        self.main_layout.addWidget(self.sound_type_combo)
        self.morse_scale_combo.hide()  # Initially hide the Morse scale combo box

        self.sound_type_combo.currentIndexChanged.connect(self.update_sound_type)

        # self.create_pdf_button()
        self.create_start_button()
        self.create_download_button()
        self.create_sound_file_button()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_status)

    def update_sound_type(self, index):
        selected_text = self.sound_type_combo.itemText(index)
        if selected_text == "morse (select scale)":
            self.morse_scale_combo.show()
        else:
            self.morse_scale_combo.hide()
        self.sound_type = selected_text

    """"
    def create_pdf_button(self):
        pdf_button = QPushButton("Open PDF", self)
        pdf_button.clicked.connect(self.open_pdf)
        self.main_layout.addWidget(pdf_button)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF files (*.pdf)")
        if file_path:
            text = extract_text(file_path)
            self.text_entry.clear()
            self.text_entry.setPlainText(text)
    """


    def create_start_button(self):
        self.start_button = QPushButton("Start/Stop Playback", self)
        self.start_button.clicked.connect(self.start_playback)
        self.main_layout.addWidget(self.start_button)

    def start_playback(self):
        if self.is_playing:
            self.stop_playback()
        else:
            text = self.text_entry.toPlainText()
            selected_index = self.sound_type_combo.currentIndex()  # Get the current index
            selected_text = self.sound_type_combo.itemText(selected_index)  # Get the text at that index
            if selected_text == "morse (select scale)":
                selected_scale = self.morse_scale_combo.currentText()  # Get the selected scale
                scale = self.scales[selected_scale]
                sines = {note: Sine(freq=freq, mul=1) for note, freq in scale.items()}
                sequence = morse_code_to_musical_sequence(text, scale)
                play_sequence(sequence, sines)

            else:
                generated_sound = combining_sounds(text, sound_type=selected_text)
                play_sound(generated_sound, sound_type=selected_text)
                logging.debug(f"Starting playback for sound type: {selected_text}")
                recognize_text_from_sound(f'{selected_text}/final.wav', sound_type=selected_text)
                self.is_playing = True
                self.timer.start(100)

    def check_status(self):
        if pygame.mixer.music.get_busy():
            self.timer.start(100)
        else:
            self.stop_playback()

    def stop_playback(self):
        pygame.mixer.music.stop()
        # Add this line to quit the mixer after stopping the music.
        pygame.mixer.quit()
        self.is_playing = False
        self.timer.stop()
        logging.debug("Mixer quit and playback stopped.")

    def create_download_button(self):
        download_button = QPushButton("Download WAV File", self)
        download_button.clicked.connect(self.download_wav_file)
        self.main_layout.addWidget(download_button)

    def download_wav_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save WAV File", "", "WAV files (*.wav)")
        if file_path:
            text = self.text_entry.toPlainText()  # Use toPlainText() instead of get("1.0", tk.END)
            generated_sound = combining_sounds(text)

            self.save_wav(file_path, generated_sound)
            print(f"Saving .wav file to: {file_path}")

    def create_sound_file_button(self):
        sound_file_button = QPushButton("Select Sound File", self)
        sound_file_button.clicked.connect(self.select_sound_file)
        self.main_layout.addWidget(sound_file_button)

    def select_sound_file(self):
        sound_file_path, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.wav;*.mp3)")
        if sound_file_path:
            recognize_text_from_sound(sound_file_path)

if __name__ == "__main__":
    app = QApplication([])
    root = TextToSoundConverterApp()
    root.show()
    app.exec_()
