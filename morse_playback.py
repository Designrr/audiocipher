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