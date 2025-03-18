from setuptools import setup

APP = ['beyond_hunger.py']
DATA_FILES = [('assets', ['assets/BeyondHunger.png'])]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6'],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets'
    ],
    'iconfile': 'assets/BeyondHunger.png',
    'plist': {
        'CFBundleName': 'Beyond Hunger',
        'CFBundleDisplayName': 'Beyond Hunger',
        'CFBundleIdentifier': 'org.beyondhunger.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True
    }
}

setup(
    app=APP,
    name="Beyond Hunger",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 