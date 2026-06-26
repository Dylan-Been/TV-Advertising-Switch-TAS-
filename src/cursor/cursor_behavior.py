import ctypes
import time
import threading
import pyautogui
from src.cursor.custum_cursor import hide_cursor, show_cursor
import os

#hidding the cursor after 3 seconds when there is no movement by setting the cursor to a empty image 
last_pos = pyautogui.position()
last_move_time = time.time()
hidden = False

def cursor_auto_hide():
    global last_pos, last_move_time, hidden

    while True:
        pos = pyautogui.position()

        if pos != last_pos:
            last_pos = pos
            last_move_time = time.time()

            if hidden:
                show_cursor()
                hidden = False

        if not hidden and time.time() - last_move_time > 3:
            hide_cursor()
            hidden = True

        time.sleep(0.1)