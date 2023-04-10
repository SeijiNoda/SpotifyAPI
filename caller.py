import os
from dotenv import load_dotenv

import webbrowser
import pyautogui as gui
import time

load_dotenv()
port = os.getenv('PORT')

from requests import get

url = f'http://localhost:{port}'

webbrowser.open(url, 1, True)
time.sleep(5)
gui.hotkey('ctrl', 'w')
