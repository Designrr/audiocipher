import logging

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Rest of your imports
from pydub import AudioSegment
import pygame
import sys, os


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and for Py2app """
    import os
    import sys
    if hasattr(sys, 'frozen'):
        # Path when running in a Py2app bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Path when running in a development environment
        return os.path.join(os.path.abspath("."), relative_path)

def mapping_sounds(sound_type):
    # Use the resource_path function to get the correct path to the sound_type directory
    sounds_base_dir = resource_path(sound_type)

    letters = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '0123456789'
    symbols = '!@#$%^&*()_-+={<}>?/\'",.;:[]'
    
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

    # Combine mappings for letters, numbers, and symbols
    symbol_filenames.update({char: f'{char}' for char in letters})
    symbol_filenames.update({char: f'{char}' for char in numbers})
    
    # Construct full paths for sound files using resource_path to ensure correct paths in all environments
    sounds = {char: resource_path(os.path.join(sounds_base_dir, f"{filename}.wav")) for char, filename in symbol_filenames.items()}

    logging.debug(f"Sounds base directory: {sounds_base_dir}")
    logging.debug(f"Sound file paths: {sounds}")
    return sounds


def combining_sounds(text, sound_type):
    sound_file = AudioSegment.silent(duration=0)

    # Correctly resolve the path for gap.wav using resource_path
    gap_sound_path = resource_path(os.path.join(sound_type, 'gap.wav'))



    words = text.split()
    for i, word in enumerate(words):
        for j, letter in enumerate(word):
            file_path = mapping_sounds(sound_type).get(letter.lower())
            if file_path:
                try:
                    new_sound = AudioSegment.from_wav(file_path)
                    sound_file = sound_file.append(new_sound, crossfade=0)
                except Exception as e:
                    logging.debug(f"Error loading sound for letter '{letter}': {e}")

            # Check if it's the last letter of the last word
            if i == len(words) - 1 and j == len(word) - 1:
                break  # Skip adding silent interval after the last letter

        # Add silent interval between words
        if i < len(words) - 1:
            sound_file += AudioSegment.from_wav(gap_sound_path)

    return sound_file

import pygame


def play_sound(sound_file, sound_type):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    if sound_file:
        final_sound_path = resource_path(os.path.join(sound_type, 'final.wav'))
        sound_file.export(final_sound_path, format="wav")
        pygame.mixer.music.load(final_sound_path)
        pygame.mixer.music.play()
