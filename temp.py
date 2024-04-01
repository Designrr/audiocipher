from pydub import AudioSegment

def get_sound_length(file_path):
    audio = AudioSegment.from_file(file_path)
    length_seconds = len(audio) / 1000.0  # AudioSegment.length is in milliseconds
    return length_seconds

# Example usage
file_path = 'modulated\gap.wav'
length = get_sound_length(file_path)
print(f"The length of the sound file is: {length} seconds")