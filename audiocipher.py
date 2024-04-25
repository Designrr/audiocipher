import logging

# Setup logging at the top
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QComboBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTimer, Qt
import pygame
import sys
from combining_sounds import combining_sounds, play_sound
from recognize_text import recognize_text_from_sound
from morse_playback import read_scales_from_file, morse_code_to_musical_sequence, generate_audio_from_sequence
import os
import shutil
import atexit

logging.debug(os.environ)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.darkYellow)  # Set background color
        self.setPalette(p)
        self.setFixedHeight(15)  # Set height of the title bar

        # Mouse dragging functionality
        self.is_dragging = False
        self.drag_start_position = None

        # Add close button
        self.close_button = QPushButton("x", self)
        self.close_button.setGeometry(self.width() - -645, 0, 20, 10)
        self.close_button.clicked.connect(self.close_window)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPos() - self.parentWidget().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.parentWidget().move(event.globalPos() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def close_window(self):
        if self.parentWidget():
            self.parentWidget().close()


class TextToSoundConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Define the base directory for file paths
        # If the application is frozen (i.e., packaged by PyInstaller), use sys._MEIPASS
        # Otherwise, use the directory of this script file
        self.base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        audio_types = ['modulated', 'morse', 'non_human']
        for audio_type in audio_types:
            final_wav_path = os.path.join(self.base_dir, audio_type, 'final.wav')
            if os.path.exists(final_wav_path):
                os.remove(final_wav_path)
                print(f"Deleted {final_wav_path}")   

        # Construct the path to the scales_frequencies.txt file
        scales_frequencies_path = os.path.join(self.base_dir, 'morse', 'scales_frequencies.txt')

        # Now use the resolved path to read the scales from the file
        self.scales = read_scales_from_file(scales_frequencies_path)
        
        self.setWindowTitle("Text to Sound Converter")
        self.setGeometry(100, 100, 800, 600)
        
        self.selected_sound_file = None

        self.is_playing = False  # Initialize playback flag

        self.selected_sound_file_path = None

        # Set application icon
        icon_path = ".\icons\icon_for_windows.ico"  # Replace with the actual path to your icon file
        self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

        self.typing_timer = QTimer(self)  # Timer for typing effect
        self.typing_timer.timeout.connect(self.type_text)
        self.text_to_type = ""  # Store the text that needs to be typed out
        self.text_typed_for_current_file = False  # Tracks if text has been typed for the current file
        self.playback_source = 'text'  # Tracks the source of playback ('file' or 'text')
        self.current_typing_pos = 0  # Keep track of the current typing position
        self.duration_per_character = 100  # Duration for each character in ms
        self.gap_between_words = 200  # Additional gap between words in ms

    def init_ui(self):
        # Remove the default title bar provided by the operating system
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove all window decorations

        self.main_layout = QVBoxLayout(self)
        
        # Create custom title bar
        self.title_bar = CustomTitleBar(self)

        # Add the custom title bar to the top of the main layout
        self.main_layout.addWidget(self.title_bar)

        # Set a font for the QTextEdit
        font = QFont()
        font.setPointSize(12)
            # Set Stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: white;
            }
            QTextEdit {
                font-size: 14px;
                border: 1px solid #b58900;
            }
            QPushButton {
                background-color: #b58900;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0c000;
            }
            QComboBox {
                border: 1px solid #b58900;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 14px;
                background-color: #333;
            }

            QComboBox:hover {
                background-color: #333;
                border: 1px solid 
            }

            QComboBox:focus {
                border-color: #b58900;
                background-color: #333;
            }

             QComboBox:on {
                /* Optional: style for the selected item */
                background-color: #333;
                border: 1px solid #b58900
            }   
        """)

    

        self.text_entry = QTextEdit(self)
        self.text_entry.setFont(font)
        self.text_entry.setPlaceholderText("Enter your text here...")

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

        self.sound_type_combo.addItem("morse")
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
        if selected_text == "morse":
            self.morse_scale_combo.show()
        else:
            self.morse_scale_combo.hide()
        self.sound_type = selected_text

    def get_sound_type(self):
        selected_index = self.sound_type_combo.currentIndex()
        selected_text = self.sound_type_combo.itemText(selected_index)
        return selected_text

    def create_start_button(self):
        self.start_button = QPushButton("Start/Stop Playback", self)
        self.start_button.clicked.connect(self.start_playback)
        self.main_layout.addWidget(self.start_button)

    def start_playback(self):
        logging.debug("Start playback function called.")
        if self.is_playing:
            logging.debug("Stopping playback.")
            self.stop_playback()
        else:
            logging.debug("Starting playback.")
            text = self.text_entry.toPlainText()
            selected_text = self.get_sound_type()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if self.selected_sound_file and not self.text_typed_for_current_file:
                pygame.mixer.music.load(self.selected_sound_file)
                pygame.mixer.music.play()
                self.is_playing = True
                self.timer.start(100)
                self.selected_sound_file = None
                self.text_entry.clear()
                self.type_text()
                self.text_typed_for_current_file = True
            elif not self.selected_sound_file or self.playback_source == 'text':
                if selected_text == "morse":
                    selected_scale = self.morse_scale_combo.currentText()  # Get the selected scale
                    scale = self.scales[selected_scale]
                    sequence = morse_code_to_musical_sequence(text, scale)
                    audio = generate_audio_from_sequence(sequence, scale)
                    audio_file_path = self.resource_path(os.path.join(self.get_sound_type(), 'final.wav'))
                    audio.export(audio_file_path, format="wav")

                    # Play the audio file using Pygame
                    pygame.mixer.music.load(audio_file_path)
                    pygame.mixer.music.play()
                    
                    # Track the playback status
                    self.is_playing = True
                    self.timer.start(100)  # You might adjust or remove this timer depending on how you handle playback checking
                    logging.debug("Started morse playback.")
                else:
                    generated_sound = combining_sounds(text, sound_type=selected_text)
                    play_sound(generated_sound, sound_type=selected_text)
                    logging.debug(f"Starting playback for sound type: {selected_text}")
                    self.is_playing = True
                    self.timer.start(100)
                    logging.debug(f"Started {selected_text} playback.")
                    #print("recognized text:", recognize_text_from_sound(f"{selected_text}/final.wav", sound_type=selected_text))

    def check_status(self):
        logging.debug("Check status function called.")
        selected_text = self.get_sound_type()
        if pygame.mixer.music.get_busy():
            self.timer.start(100)
        else:
            self.stop_playback()

    def stop_playback(self):
        logging.debug("Stop playback function called.")
        selected_text = self.get_sound_type()
        if selected_text == "morse":
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                logging.debug("Mixer quit and playback stopped.")
        else: 
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                # Add this line to quit the mixer after stopping the music.
                pygame.mixer.quit()
                logging.debug("Mixer quit and playback stopped.")
        self.is_playing = False
        self.timer.stop()

    def create_download_button(self):
        download_button = QPushButton("Download WAV File", self)
        download_button.clicked.connect(self.download_wav_file)
        self.main_layout.addWidget(download_button)

    def download_wav_file(self):
        # Open a file dialog to get the location where the user wants to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save WAV File", "", "WAV files (*.wav)")
        if file_path:
            # Get the full path to the existing 'final.wav' based on the selected sound type
            source_path = os.path.join(self.base_dir, f'{self.get_sound_type()}', 'final.wav')
            
            # Check if the source file exists
            if os.path.exists(source_path):
                # Copy the file to the new location specified by the user
                shutil.copy(source_path, file_path)
                logging.debug(f"File saved successfully to: {file_path}")
            else:
                logging.debug("Source file does not exist.")
        else:
            logging.debug("File save operation canceled.")

    def create_sound_file_button(self):
        sound_file_button = QPushButton("Select Sound File", self)
        sound_file_button.clicked.connect(self.select_sound_file)
        self.main_layout.addWidget(sound_file_button)


    def select_sound_file(self):
        sound_file_path, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.wav;*.mp3)")
        if sound_file_path:
            self.selected_sound_file = sound_file_path
            recognized_text = recognize_text_from_sound(sound_file_path, sound_type=self.get_sound_type())
            self.text_to_type = recognized_text
            self.current_typing_pos = 0
    
    def type_text(self):
        if self.current_typing_pos < len(self.text_to_type):
            next_char = self.text_to_type[self.current_typing_pos]

            self.text_entry.insertPlainText(next_char)
            self.current_typing_pos += 1

            if next_char == " ":
                self.typing_timer.start(self.gap_between_words)
            else:
                self.typing_timer.start(self.duration_per_character)
        else:
            # Stop the timer if the entire text has been typed out
            self.typing_timer.stop()

    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for development and for Py2app """
        import os
        import sys
        if hasattr(sys, 'frozen'):
            # Path when running in a Py2app bundle
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Path when running in a development environment
            return os.path.join(os.path.abspath("."), relative_path)
                 
           


if __name__ == "__main__":
    app = QApplication([])
    root = TextToSoundConverterApp()
    root.show()
    app.exec_()
