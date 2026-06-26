import time

import pyautogui
from pycaw.pycaw import AudioUtilities
import comtypes 

import win32gui
import win32con
import win32com.client

from src.states.procces_status import switch_proccesstate

#getting the browser tab by search for its name 
def get_window_handle(title_part):
    title_part = title_part.lower()
    matches = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        if title and title_part in title.lower():
            matches.append(hwnd)

    win32gui.EnumWindows(enum_handler, None)

    if not matches:
        return None

    return matches[0]

#clicking the right top button in the ziggo app that will activate the picture in picture mode
def overlay_ziggo():
    hwnd = get_window_handle("Ziggo")

    if hwnd is None:
        print("No Ziggo window found")
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # Click the icon near the top-right of Ziggo player
    pyautogui.click(right - 250, top + 20)
    time.sleep(0.3)
    pyautogui.click(right - 250, top + 20)

    return True

#clicking the go back button in the ziggo picture in picture overlay  
def remove_overlay_ziggo():
    hwnd = get_window_handle("Youtube")

    if hwnd is None:
        print("No Youtube window found")
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # Click the icon near the top-right of Ziggo player
    pyautogui.click(right - 500, top + 1150)

    return True

def scale_ziggo():
    hwnd = get_window_handle("Ziggo")

    if hwnd is None:
        print("No Ziggo window found")
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # Click the icon near the top-right of Ziggo player
    pyautogui.click(right - 100, top + 200)
    time.sleep(0.2)
    pyautogui.click(right - 100, top + 200)

    return True

#muting a procces on windows 
def set_app_mute(process_name, mute=True):
    comtypes.CoInitialize()

    found = False

    try:
        sessions = AudioUtilities.GetAllSessions()

        for session in sessions:
            if session.Process:
                name = session.Process.name().lower()

                if name == process_name.lower():
                    found = True
                    volume = session.SimpleAudioVolume
                    volume.SetMute(1 if mute else 0, None)
                    volume.SetMasterVolume(0.0 if mute else 1.0, None)
                    print("Changed:", name)

        if not found:
            print("No audio session found for", process_name)

    finally:
        comtypes.CoUninitialize()

#redirecting input to a browser name by search for its name 
def focus_window(title_part):
    title_part = title_part.lower()

    matches = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        if title and title_part in title.lower():
            matches.append(hwnd)

    win32gui.EnumWindows(enum_handler, None)

    if not matches:
        print(f"No window found with title: {title_part}")
        return False

    hwnd = matches[0]

    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)

        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        time.sleep(0.2)

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')  # unlock Windows focus rules

        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)

        return True

    except Exception as e:
        print(f"Could not focus window '{title_part}': {e}")

        # fallback: click roughly in the middle of the window
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            pyautogui.click(left + 300, top + 200)
            time.sleep(0.2)
            return True
        except Exception as e2:
            print(f"Fallback click failed: {e2}")
            return False


def focus_chrome():
    return focus_window("YouTube")


def focus_edge():
    return focus_window("Ziggo")

#switching to youtube 
def switch_to_youtube():
    switch_proccesstate(True)
    overlay_ziggo()
    set_app_mute("svchost.exe", True)
    time.sleep(1)
    focus_chrome()
    switch_proccesstate(False)

#switching back to ziggo 
def switch_to_ziggo():
    switch_proccesstate(True)
    focus_chrome()
    time.sleep(0.3)
    set_app_mute("svchost.exe", False)
    remove_overlay_ziggo()
    time.sleep(1)
    focus_edge()
    switch_proccesstate(False)