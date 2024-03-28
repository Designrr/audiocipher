import logging

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from combining_sounds import mapping_sounds

def recognize_text_from_sound(sound_file_path, sound_type):
    sound_map = {k: AudioSegment.from_wav(v) for k, v in mapping_sounds(sound_type).items()}
    sound = AudioSegment.from_wav(sound_file_path)
    recognized_text = analyze_audio(sound, sound_map, sound_type)
    logging.debug(f"Recognizing text from sound for sound type: {sound_type}")
    print("Recognized text:", recognized_text)

def recognize_text_from_mic():
    sound_map = {k: AudioSegment.from_wav(v) for k, v in mapping_sounds().items()}

    # Set parameters for audio input
    duration = 0.1  # Duration of each captured segment (in seconds)
    sample_rate = 44100  # Adjust based on your microphone's capabilities

    recognized_text = ""
    consecutive_zeros = 0  # Counter for consecutive zeros

    with sd.InputStream(channels=1, samplerate=sample_rate, blocksize=int(duration * sample_rate)) as stream:
        print("Listening... (Press Ctrl+C to stop)")
        try:
            while True:
                # Read audio data from the microphone
                audio_data, overflowed = stream.read(int(duration * sample_rate))

                # Convert the audio data to a numpy array
                audio_data = np.array(audio_data)

                # Calculate the spectrum
                frequencies, amplitudes = np.fft.fftfreq(len(audio_data), 1/sample_rate), np.abs(np.fft.fft(audio_data))

                # Find the dominant frequency
                dominant_frequency = abs(frequencies[np.argmax(amplitudes)])

                # Check if dominant frequency is zero or if the segment is silence
                if dominant_frequency == 0 or recognized_text.endswith('silence'):
                    consecutive_zeros += 1
                    if consecutive_zeros == 1:  # Only add a space for the first zero frequency encountered
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

        except KeyboardInterrupt:
            print("\nRecognition stopped. Recognized text:", recognized_text)

def analyze_audio(sound, sound_map, sound_type):
    recognized_text = ""
    consecutive_zeros = 0  # Counter for consecutive zeros
    window_size = 100  # Assuming sound files are 0.1 seconds long

    if sound_type == "beeps" or sound_type == "modulated":
        gap_frequency = 500
    elif sound_type == "non_human":
        gap_frequency = 20900
    
    if sound_type == "morse":
        segment
    else: 

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
                    if consecutive_zeros == 1:  # Only add a space for the first zero frequency encountered
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

if __name__ == "__main__":
    # Example usage: recognize from a sound file
    sound_file_path = "path/to/your/sound/file.wav"
    recognize_text_from_sound(sound_file_path)

    # Uncomment the line below to recognize from the microphone
    recognize_text_from_mic()
