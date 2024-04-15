import math
import wave
import struct
from playsound import playsound
import os 

class BeepGenerator:
    def __init__(self):
        self.audio = []
        self.sample_rate = 44100.0

    def append_silence(self, duration_milliseconds=500):
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)

        for x in range(int(num_samples)): 
            self.audio.append(0.0)

        return    
        
    def append_sinewave(
            self,
            freq, 
            duration_milliseconds=100, 
            volume=1.0,
            use_modulation=False,
            modulator_freq=5.0,
            modulation_factor=5.0):
        
        num_samples = int(duration_milliseconds * (self.sample_rate / 1000.0))

        if use_modulation:
            # Generate modulator waveform (e.g., a sine wave)
            modulator = [math.sin(2 * math.pi * modulator_freq * x / self.sample_rate) for x in range(num_samples)]

            for x, modulator_amplitude in enumerate(modulator):
                current_frequency = freq + modulation_factor * modulator_amplitude
                self.audio.append(volume * math.sin(2 * math.pi * current_frequency * (x / self.sample_rate)))
        else:
            # Generate plain sine wave
            for x in range(num_samples):
                self.audio.append(volume * math.sin(2 * math.pi * freq * (x / self.sample_rate)))

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
def generate_sounds(sound_folder, base_frequency, text_characters, symbol_filenames, text_symbols, use_modulation=False):
    if not os.path.exists(sound_folder):
        os.makedirs(sound_folder)

    for character in text_characters:
        bg = BeepGenerator()
        bg.append_sinewave(freq=base_frequency, volume=0.5, duration_milliseconds=100, use_modulation=use_modulation)
        bg.save_wav(f"{sound_folder}/{character}.wav")
        base_frequency += 10

    for symbol in text_symbols:
        bg = BeepGenerator()
        bg.append_sinewave(freq=base_frequency, volume=0.5, duration_milliseconds=100, use_modulation=use_modulation)
        base_frequency += 10
        filename = symbol_filenames.get(symbol, f"unknown_symbol_{ord(symbol)}")
        bg.save_wav(f"{sound_folder}/{filename}.wav")

    # Generate silence separately
    bg = BeepGenerator()
    bg.append_silence(duration_milliseconds=200)
    bg.save_wav(f"{sound_folder}/silence.wav")


if __name__ == "__main__": 
    text_lowercase = "abcdefghijklmnopqrstuvwxyz"
    text_numbers = "0123456789"
    text_symbols = '!@#$%^&*()_-+={<}>?/\'",.;:[]'
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

    sound_folder1 = "beeps"
    base_frequency1 = 300
    generate_sounds(sound_folder1, base_frequency1, text_lowercase + text_numbers, symbol_filenames, text_symbols)

    sound_folder2 = "non_human"
    base_frequency2 = 80000
    generate_sounds(sound_folder2, base_frequency2, text_lowercase + text_numbers, symbol_filenames, text_symbols)

    sound_folder3 = "wavy"
    base_frequency3 = 300
    generate_sounds(sound_folder3, base_frequency3, text_lowercase + text_numbers, symbol_filenames, text_symbols, use_modulation=True)




    