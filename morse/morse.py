import tkinter as tk
from pyo import *
import random
import time

# Function to read scales and frequencies from a text file
def read_scales_from_file(file_path):
    scales = {}
    with open(file_path, 'r') as file:
        for line in file:
            scale_name, freq_str = line.strip().split(': ')
            frequencies = [float(freq) for freq in freq_str.split(', ')]
            scales[scale_name] = dict(zip(['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C5'], frequencies))
    return scales

# Morse code representations
morse_code = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..', ' ': ' ',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
}


# Convert Morse code to a sequence of notes and durations
def morse_code_to_musical_sequence(message, scale):
    sequence = []
    for char in message.upper():
        if char == ' ':
            sequence.append(('R', 0.25))
        elif char in morse_code:
            for symbol in morse_code[char]:
                note = random.choice(list(scale.keys()))
                duration = 0.125 if symbol == '.' else 0.25
                sequence.append((note, duration))
            sequence.append(('R', 0.125))
    sequence.append(('C', 0.5))
    return sequence

# Function to play a note
def play_note(note, duration, sines):
    sines[note].out()
    time.sleep(duration)
    sines[note].stop()

# Play the musical sequence
def play_sequence(sequence, sines):
    for note, duration in sequence:
        if note == 'R':
            time.sleep(duration)
        else:
            play_note(note, duration, sines)

class MorseCodeMusicApp:
    def __init__(self, window, scales):
        self.window = window
        self.window.title("Morse Code Melody Generator")
        
        # Adjust the window size here
        self.window.geometry('375x150')
        
        self.scales = scales

        # Initialize Pyo server
        self.server = Server().boot()
        self.server.start()

        self.setup_widgets()

    def setup_widgets(self):
        # User input field
        tk.Label(self.window, text="Enter a phrase:").pack()
        
        # Adjust the width of the text entry here
        self.user_input = tk.Entry(self.window, width=50)
        self.user_input.pack()

        # Scale selection
        tk.Label(self.window, text="Select a scale:").pack()
        self.scale_var = tk.StringVar(self.window)
        self.scale_var.set("C Major")  # default
        
        # Adjust the width of the dropdown menu (OptionMenu) indirectly via the width of the variable it's tied to
        self.scale_menu = tk.OptionMenu(self.window, self.scale_var, *self.scales.keys())
        self.scale_menu.config(width=11)  # Adjust the width of the OptionMenu here
        self.scale_menu.pack()

        # Play button
        self.play_button = tk.Button(self.window, text="Play", command=self.generate_and_play_sequence)
        self.play_button.pack()

    def generate_and_play_sequence(self):
        user_text = self.user_input.get()
        selected_scale = self.scale_var.get()
        scale = self.scales[selected_scale]
        sines = {note: Sine(freq=freq, mul=1) for note, freq in scale.items()} 
        sequence = morse_code_to_musical_sequence(user_text, scale)
        play_sequence(sequence, sines)
    
    def on_close(self):
        self.server.stop()
        self.server.shutdown()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    all_scales = read_scales_from_file('.\morse\scales_frequencies.txt')
    app = MorseCodeMusicApp(root, all_scales)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
