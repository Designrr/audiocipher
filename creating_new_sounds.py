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
        
    def append_waveform(
            self,
            waveform_type,  # Can be "sine", "triangle", "square", or "sawtooth"
            freq,
            duration_milliseconds=100,
            volume=.4,
            use_modulation=False,
            modulator_freq=5.0,
            modulation_factor=7.0,
            envelope=(0.25, 0.3, 0.4, 0.25)):  # Attack, decay, sustain, release
        num_samples = int(duration_milliseconds * (self.sample_rate / 1000.0))

        # Generate waveform based on type
        if waveform_type == "sine":
            waveform = [math.sin(2 * math.pi * freq * x / self.sample_rate) for x in range(num_samples)]
        elif waveform_type == "triangle":
            waveform = [4 * abs(2 * x / num_samples - 1) - 1 for x in range(num_samples)]
        elif waveform_type == "square":
            waveform = [math.copysign(1.0, math.sin(2 * math.pi * freq * x / self.sample_rate)) for x in range(num_samples)]
        elif waveform_type == "sawtooth":
            waveform = [(x / num_samples) for x in range(num_samples)]
        else:
            raise ValueError("Invalid waveform type:", waveform_type)

        # Apply modulation if needed
        if use_modulation:
            modulator = [math.sin(2 * math.pi * modulator_freq * x / self.sample_rate) for x in range(num_samples)]
            for x, modulator_amplitude in enumerate(modulator):
                waveform[x] *= 1 + modulation_factor * modulator_amplitude

        # Apply envelope
        for i, sample in enumerate(waveform):
            envelope_value = envelope[0] + (envelope[1] - envelope[0]) * (i / len(waveform))
            envelope_value = envelope_value * envelope[2] + envelope[3] * (1 - envelope_value)
            waveform[i] = volume * sample * envelope_value

        # Add the adjusted waveform to the audio buffer
        self.audio.extend(waveform)
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
def generate_sounds(wave_form, sound_folder, base_frequency, text_characters, symbol_filenames, text_symbols, use_modulation=False):
    if not os.path.exists(sound_folder):
        os.makedirs(sound_folder)
    
    bg = BeepGenerator()
    bg.append_waveform(wave_form, freq=base_frequency - 10, duration_milliseconds=200, use_modulation=use_modulation)
    bg.save_wav(f"{sound_folder}/gap.wav")

    for character in text_characters:
        bg = BeepGenerator()
        bg.append_waveform(wave_form, freq=base_frequency, duration_milliseconds=100, use_modulation=use_modulation)
        bg.save_wav(f"{sound_folder}/{character}.wav")
        base_frequency += 10

    for symbol in text_symbols:
        bg = BeepGenerator()
        bg.append_waveform(wave_form, freq=base_frequency, duration_milliseconds=100, use_modulation=use_modulation)
        base_frequency += 10
        filename = symbol_filenames.get(symbol, f"unknown_symbol_{ord(symbol)}")
        bg.save_wav(f"{sound_folder}/{filename}.wav")

    # Generate silence separately
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
    base_frequency1 = 500
    generate_sounds("sine", sound_folder1, base_frequency1, text_lowercase + text_numbers, symbol_filenames, text_symbols)

    sound_folder2 = "non_human"
    base_frequency2 = 20900
    generate_sounds("sine", sound_folder2, base_frequency2, text_lowercase + text_numbers, symbol_filenames, text_symbols)

    sound_folder4 = "modulated"
    base_frequency4 = 500
    wave_form4 = "sine"
    generate_sounds(wave_form4, sound_folder4, base_frequency4, text_lowercase + text_numbers, symbol_filenames, text_symbols, use_modulation=True)




    
