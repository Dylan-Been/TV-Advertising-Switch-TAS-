from flask import Flask, send_file, request, render_template
import pyautogui
from src.actions.switch import switch_to_youtube, switch_to_ziggo, get_window_handle, set_app_mute
from src.states.app_state import get_currentstate, switch_currentstate
from src.states.stop_flag_state import stop_recording, get_stop_flag
import time
import pydirectinput
import win32gui     
from src.states.procces_status import switch_proccesstate, get_proccesstate
from src.actions.restart import restart_program
import os
# getting the absolute path to the main directiory 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#setting up the flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

set_app_mute("svchost.exe", False)

currentstatetrack = 'ziggo'

#scrolling speed with touchpad 
last_arrow_press = 0
ARROW_INTERVAL = 0.25

@app.route("/startup")
def startup():
    return render_template("startup.html")

@app.route("/")
def home():
    return render_template("remote.html")
#arrow keys 
@app.route("/up")
def up():
    pyautogui.press("up")
    return "OK"

@app.route("/down")
def down():
    pyautogui.press("down")
    return "OK"

@app.route("/left")
def left():
    if currentstatetrack == "ziggo":
        pydirectinput.keyDown('shift')
        time.sleep(0.1)
        pydirectinput.press('tab')
        time.sleep(0.05)
        pydirectinput.keyUp('shift')
    else:
        pyautogui.press("left")
    return "OK"

@app.route("/right")
def right():
    print(currentstatetrack)
    if currentstatetrack == "ziggo":
        pyautogui.press("tab")
    else:
        pyautogui.press("right")
    return "OK"
# actions 
@app.route("/OK")
def ok():
    if get_proccesstate() == "Clear":
        pyautogui.press("enter")
    return "OK"

@app.route("/Back")
def back():
    if get_proccesstate() == "Clear":
        pyautogui.press("escape")
    return "OK"

@app.route("/switch")
def switch():
    if get_proccesstate() == "Clear":
        switch_proccesstate(True)
        global currentstatetrack
        currentstate = get_currentstate()
        if currentstate == "ziggo":
            switch_to_youtube()
            switch_currentstate("youtube")
            currentstatetrack = "youtube"
        else:
            switch_to_ziggo()
            switch_currentstate("ziggo")
            currentstatetrack = "ziggo"
    return "OK"

@app.route("/Scale")
def scale():
    if get_proccesstate() == "Clear":   
        if currentstatetrack == "ziggo":
            hwnd = get_window_handle("Ziggo")
            if hwnd is None:
                print("No Ziggo window found")
                return False

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)

            # Click the icon near the top-right of Ziggo player
            pyautogui.click(right - 100, top + 200)
            time.sleep(0.2)
            pyautogui.click(right - 100, top + 200)
        else:
            pyautogui.press("f11")
    return "OK"

@app.route("/removeoverlay")
def removeoverlay():
    if get_proccesstate() == "Clear":   
        if currentstatetrack == "youtube": 
            hwnd = get_window_handle("youtube")
            if hwnd is None:
                print("No youtube window found")
                return False

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)

            # Click the icon near the top-right of Ziggo player
            pyautogui.click(right - 100, top + 1150)
    return "OK"

@app.route("/record")
def record():
    stop_recording()
    return "OK"

@app.route("/icon")
def icon():
    print('switching icon')
    return "mic-off" if get_stop_flag() else "mic"
#restaring the entire pc 
@app.route("/Restart")
def restart():
    switch_proccesstate(True)
    print("restart")
    restart_program()
    return "OK"

@app.route("/Status_Restart")
def Status_Restart():              
    return get_proccesstate()
    
#mouse movement 
@app.route("/mouse_move")
def mouse_move():
    global last_arrow_press

    if get_proccesstate() == "Clear":
        dx = int(float(request.args.get("dx", 0)))
        dy = int(float(request.args.get("dy", 0)))

        pyautogui.PAUSE = 0
        pyautogui.moveRel(dx, dy, duration=0)

        x, y = pyautogui.position()
        _, screen_h = pyautogui.size()

        now = time.time()
        can_press_arrow = now - last_arrow_press >= ARROW_INTERVAL

        if y <= 600 and dy < 0:
            if currentstatetrack == "ziggo":
                pyautogui.scroll(100)

                if y <= 200 and can_press_arrow:
                    pyautogui.press("up")
                    last_arrow_press = now

            elif y <= 200 and can_press_arrow:
                pyautogui.press("up")
                last_arrow_press = now

        elif y >= screen_h - 200 and dy > 0:
            if currentstatetrack == "ziggo":
                pyautogui.scroll(-100)

                if can_press_arrow:
                    pyautogui.press("down")
                    last_arrow_press = now

            elif can_press_arrow:
                pyautogui.press("down")
                last_arrow_press = now

    return "OK"


@app.route("/mouse_click")
def mouse_click():
    if get_proccesstate() == "Clear":
        pyautogui.click()
    return "OK"

# routes for python processes 
@app.route("/youtube")
def youtube():
    global currentstatetrack
    switch_to_youtube()
    currentstatetrack = "youtube"
    return "OK"

@app.route("/ziggo")
def ziggo():
    global currentstatetrack
    switch_to_ziggo()
    currentstatetrack = "ziggo"
    return "OK"

def start_apps():
    print("Starting remote control server...")
    app.run(host="0.0.0.0", port=5000)
    
if __name__ == "__main__":
    start_apps()
