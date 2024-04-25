import logging

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from scipy.io import wavfile
from scipy.signal import find_peaks
import numpy as np
from pydub import AudioSegment
from combining_sounds import mapping_sounds

def recognize_text_from_sound(sound_file_path, sound_type):
    if sound_type == "morse":
        recognized_text = analyze_morse_audio()
        print(recognized_text)
    else:
        sound_map = {k: AudioSegment.from_wav(v) for k, v in mapping_sounds(sound_type).items()}
        sound = AudioSegment.from_wav(sound_file_path)
        recognized_text = analyze_audio(sound, sound_map, sound_type)
        logging.debug(f"Recognizing text from sound for sound type: {sound_type}")
        # print("Recognized text:", recognized_text)
    return recognized_text

def analyze_audio(sound, sound_map, sound_type):
    recognized_text = ""
    consecutive_zeros = 0  # Counter for consecutive zeros
    window_size = 100  # Assuming sound files are 0.1 seconds long

    if sound_type == "modulated":
        gap_frequency = 495
    elif sound_type =="beeps":
        gap_frequency = 490
    elif sound_type == "non_human":
        gap_frequency = 20890

    for i in range(0, len(sound), window_size):
        # Extract the current segment
        segment = sound[i:i+window_size]

        if len(segment) > 0:
            # Convert the segment to a numpy array
            audio_data = np.array(segment.get_array_of_samples())

            # Calculate the spectrum
            sample_rate = segment.frame_rate
            frequencies, amplitudes = np.fft.fftfreq(len(audio_data), 1/sample_rate), np.abs(np.fft.fft(audio_data))

            # Find the dominant frequency
            dominant_frequency = abs(frequencies[np.argmax(amplitudes)])

            # Check if dominant frequency is zero or if the segment is silence
            if dominant_frequency < gap_frequency:
                consecutive_zeros += 1
                if consecutive_zeros == 1:  # Only add a space for the first zero/gap frequency encountered
                    recognized_text += ' '  # Add a space
            else:
                consecutive_zeros = 0  # Reset the counter since we have a non-zero frequency

                # Find the letter with the closest match in terms of dominant frequency
                min_difference = float('inf')
                closest_letter = 'silence'  # Default to silence if no match is found

                for letter, sound_segment in sound_map.items():
                    letter_audio_data = np.array(sound_segment.get_array_of_samples())
                    letter_frequencies, _ = np.fft.fftfreq(len(letter_audio_data), 1/sample_rate), np.abs(np.fft.fft(letter_audio_data))
                    letter_dominant_frequency = np.abs(letter_frequencies[np.argmax(_)])

                    frequency_difference = abs(letter_dominant_frequency - dominant_frequency)

                    if frequency_difference < min_difference:
                        min_difference = frequency_difference
                        closest_letter = letter

                # Check if the recognized letter is not 'silence'
                if closest_letter != 'silence':
                    recognized_text += closest_letter

    return recognized_text

def analyze_morse_audio(sound_file):
    morse_code = decode_morse_from_audio(sound_file)
    return translate_morse_to_text(morse_code)

def decode_morse_from_audio(file_path):
    samplerate, data = wavfile.read(file_path)
    if data.ndim > 1:
        data = data[:, 0]  # Take first channel if stereo

    # Convert data to a normalized amplitude
    data = np.abs(data.astype(float))
    data = data / np.max(data)

    # Threshold to detect presence of a tone
    threshold = 0.5
    is_tone = data > threshold

    # Convert is_tone to change points (edges) and measure durations
    changes = np.diff(is_tone.astype(int))
    change_points = np.where(changes != 0)[0]
    durations = np.diff(change_points) / samplerate

    # Translate durations into Morse code
    morse_code = ""
    last_value = is_tone[0]
    for duration in durations:
        if last_value:  # Tone was on
            if duration < 0.18:  # Duration slightly longer than a dot to accommodate inaccuracies
                morse_code += "."
            else:
                morse_code += "-"
        else:  # Tone was off
            if duration < 0.18:
                pass  # Ignore short gaps (within a letter)
            elif duration < 0.4:
                morse_code += " "  # Space between letters
            else:
                morse_code += "   "  # Space between words
        last_value = not last_value

    return morse_code

def translate_morse_to_text(morse_code):
    """
    Translate Morse code to text using the Morse code dictionary.
    """
    morse_to_text = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
        '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
        '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
        '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9', '/': ' ', '.-.-.-': '.', '--..--': ',',
        '---...': ':', '-.-.-.': ';', '-...-': '=', '.----.': '\'', '-..-.': '/',
        '-.-.--': '!', '..--..': '?', '.--.-.': '@', '-.--.': '('
    }
    words = []
    for word in morse_code.split("   "):  # Three spaces to split words
        letters = word.split()
        translated_word = ''.join(morse_to_text.get(letter) for letter in letters if letter in morse_to_text)
        words.append(translated_word)
    return ' '.join(words)