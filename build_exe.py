import PyInstaller.__main__
import platform

options = [
    'main.py',
    '--name=narou_capture',
    '--onefile',
    '--hidden-import=selenium.webdriver.chrome.options',
]

def is_linux():
    return platform.system() == 'Linux'

if is_linux():
    options.append('--add-data=config.json:.')
else:
    options.append('--add-data=config.json;.')

PyInstaller.__main__.run(options)
