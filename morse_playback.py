import random
import time
from pydub import AudioSegment
from pydub.generators import Sine

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

# Generate the audio for a sequence of notes
def generate_audio_from_sequence(sequence, scale):
    total_audio = AudioSegment.silent(duration=0)  # Start with a silent segment
    for note, duration in sequence:
        if note == 'R':
            silence_duration = int(duration * 1000)  # Convert to milliseconds
            total_audio += AudioSegment.silent(duration=silence_duration)
        else:
            frequency = scale[note]
            tone_duration = int(duration * 1000)  # Convert to milliseconds
            tone = Sine(frequency).to_audio_segment(duration=tone_duration)
            total_audio += tone
    return total_audio