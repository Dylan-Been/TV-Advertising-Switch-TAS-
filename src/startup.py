import subprocess
import sys
import time
import psutil
import os
import pygetwindow as gw
from src.app import start_apps
from src.cursor.cursor_behavior import cursor_auto_hide
from src.services.audio_transcription import start_transcription
import threading
from src.states.procces_status import switch_proccesstate
import win32gui
import pyautogui
from src.cursor.custum_cursor import safe_cursor_loop, hide_normal_cursor
import traceback

# directing to the browser that needs to be opened  
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
# getting the absolute path to the main directiory 
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
# getting the path to the custum cursor 
CURSOR_PATH = os.path.join(
    BASE_DIR,
    "static",
    "cursors",
    "whitesphere.cur"
)

# url of webpages 
ZIGGO_URL = "https://www.ziggogo.tv/nl/home"
YOUTUBE_URL = "https://www.youtube.com/tv"

DO_NOT_CLOSE = {
    "code.exe",
    "explorer.exe",
    "cmd.exe",
    "powershell.exe",
    "WindowsTerminal.exe",
    "conhost.exe",
}

#clossing all open apps to prevent controdictions when switching 
def close_apps():
    current_pid = os.getpid()

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"]

            if not name:
                continue

            if proc.info["pid"] == current_pid:
                continue

            if name.lower() in {p.lower() for p in DO_NOT_CLOSE}:
                continue

            # Close common user apps only
            if name.lower() in [
                "chrome.exe",
                "msedge.exe",
                "firefox.exe",
                "spotify.exe",
                "discord.exe",
                "steam.exe",
                "notepad.exe",
                "vlc.exe",
            ]:
                print("Closing:", name)
                proc.terminate()

        except Exception:
            pass

    time.sleep(3)

#opening the desired web pages in chrome and edge 
def open_apps():
    subprocess.Popen([
    CHROME_PATH,
    "--kiosk",
    "http://192.168.68.63:5000/startup",
    "--new-window",
    "--disable-session-crashed-bubble",
    "--disable-infobars",
])
    #waiting 10 seconds so that the user can scan the qr code to the remote page 
    time.sleep(10)
    subprocess.Popen([
    CHROME_PATH,
    "--kiosk",
    YOUTUBE_URL,
    "--new-window",
    "--disable-session-crashed-bubble",
    "--disable-infobars",
    ])
    time.sleep(3)
    #finding the youtube page and maximaizing if needed 
    Windows = gw.getWindowsWithTitle("YouTube")
    if len(Windows) > 0:
        window = Windows[0]
        
        try:
            if window.isMinimized:
                window.restore()
                time.sleep(0.2)

            window.activate()
            time.sleep(0.2)
            window.maximize()

        except Exception as e:
            print(f"Could not focus window 'YouTube': {e}")
    else: 
        print("Could not find window 'YouTube'")
    
    time.sleep(1)
    subprocess.Popen([
    EDGE_PATH,
    "--kiosk",
    ZIGGO_URL,
    r"--C:\Users\NUC\AppData\Local\Microsoft\Edge\User Data",
    "--profile-directory=Profile 1"
    ])
    time.sleep(1)
    Windows = gw.getWindowsWithTitle("Ziggo")
    #finding the ziggo page and maximaizing if needed 
    if len(Windows) > 0:
        window = Windows[0]
        try:
            if window.isMinimized:
                window.restore()
                time.sleep(0.2)

            window.activate()
            time.sleep(0.2)
            window.maximize()

        except Exception as e:
            print(f"Could not focus window 'Ziggo': {e}")
    else:
        print("Could not find window 'Ziggo'")
    time.sleep(1)
        
if __name__ == "__main__":
    #initializing every thing 
    try:
        switch_proccesstate(True)
        close_apps()
        pyautogui.FAILSAFE = False
        hide_normal_cursor()

        threading.Thread(target=safe_cursor_loop,daemon=True).start()
        threading.Thread(target=cursor_auto_hide, daemon=True).start()
        threading.Thread(target=start_apps, daemon=True).start()
        threading.Thread(target=start_transcription, daemon=True).start()
        time.sleep(3)
        open_apps()
        print("Startup done")
        switch_proccesstate(False)
    
        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Stopping startup cleanly...")
            subprocess.run([
                sys.executable,
                os.path.join(BASE_DIR, "tests", "r.py")
            ])
            os._exit(0)
    except Exception as e:
        print("Startup failed:")
        print(e)
        traceback.print_exc()

        subprocess.run([
            sys.executable,
            os.path.join(BASE_DIR, "tests", "r.py")
        ])

        os._exit(1)
