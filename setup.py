from setuptools import setup

APP = ['audiocipher.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pydub', 'pygame', 'PyQt5', 'pdfminer.six', 'sounddevice', 'numpy', 'six'],
    'excludes': ['PyInstaller'],
}

setup(
    app=APP,
    name='audiocipher',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)