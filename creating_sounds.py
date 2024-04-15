import math
import wave
import struct
from playsound import playsound
class BeepGenerator:
    def __init__(self):
        self.audio = []
        self.sample_rate = 44100.0

    def append_silence(self, duration_milliseconds=200):
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
        print("num1: ", num_samples)

        for x in range(int(num_samples)): 
            self.audio.append(0.0)

        return    
        
    def append_sinewave(
        self,
        freq, 
        duration_milliseconds=100, 
        volume=1.0):
        print(freq)
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
    

        for x in range(int(num_samples)):
            self.audio.append(volume * math.sin(2 * math.pi * freq * ( x / self.sample_rate )))

        return

    def save_wav(self, file_name):
        # Open up a wav file
        wav_file=wave.open(file_name,"w")

        # wav params
        nchannels = 1

        sampwidth = 2

        nframes = len(self.audio)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((nchannels, sampwidth, self.sample_rate, nframes, comptype, compname))

        for sample in self.audio:
            wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

        wav_file.close()

        return    

if __name__ == "__main__":
    sound_folder = "generated_sounds"
    base_frequency = 350

    text_lowercase = "abcdefghijklmnopqrstuvwxyz"
    text_numbers = '0123456789'
    text_symbols = '!@#$%^&*()_-+={<}>?/\'",.;:[]'

    # Map symbols to their corresponding filenames
    symbol_filenames = {
        '!': 'exclamation',
        '@': 'at',
        '#': 'hash',
        '$': 'dollar',
        '%': 'percent',
        '^': 'caret',
        '&': 'ampersand',
        '*': 'asterisk',
        '(': 'left_parenthesis',
        ')': 'right_parenthesis',
        '_': 'underscore',
        '-': 'hyphen',
        '+': 'plus',
        '=': 'equals',
        '{': 'left_brace',
        '<': 'less_than',
        '[': 'left_square_bracket',
        '}': 'right_brace',
        '>': 'greater_than',
        '?': 'question_mark',
        '/': 'forward_slash',
        '\'': 'single_quote',
        '"': 'double_quote',
        ',': 'comma',
        '.': 'period',
        ';': 'semicolon',
        ':': 'colon',
        ']': 'right_square_bracket'
    }

    for symbol in text_symbols:
        base_frequency += 10
        bg = BeepGenerator()
        bg.append_sinewave(freq=base_frequency, volume=0.5, duration_milliseconds=100)

        # Use the mapped filename instead of the symbol
        filename = symbol_filenames.get(symbol, f"unknown_symbol_{ord(symbol)}")
        bg.save_wav(f"{sound_folder}/{filename}.wav")

    # Generate silence
    bg = BeepGenerator()
    bg.append_sinewave(freq=0, volume=0.5, duration_milliseconds=500)
    bg.save_wav(f"{sound_folder}/silence.wav")

