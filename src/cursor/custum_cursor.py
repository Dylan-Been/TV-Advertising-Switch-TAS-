import ctypes
import time
import os
import win32gui
import win32api
import win32con
import pyautogui
import subprocess
import traceback
import sys

from PIL import Image
import ctypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

AC_SRC_OVER = 0x00
AC_SRC_ALPHA = 0x01
ULW_ALPHA = 0x00000002
BI_RGB = 0
DIB_RGB_COLORS = 0

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]

class SIZE(ctypes.Structure):
    _fields_ = [
        ("cx", ctypes.c_long),
        ("cy", ctypes.c_long),
    ]

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ("BlendOp", ctypes.c_byte),
        ("BlendFlags", ctypes.c_byte),
        ("SourceConstantAlpha", ctypes.c_byte),
        ("AlphaFormat", ctypes.c_byte),
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_ushort),
        ("biBitCount", ctypes.c_ushort),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.c_uint32 * 3),
    ]

# getting the absolute path to the main directiory 
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

HIDDEN_CURSOR_PATH = os.path.join(
    BASE_DIR,
    "static",
    "cursors",
    "none.cur"
)

def hide_normal_cursor():

    cursor_ids = [
        32512,  # Arrow
        32513,  # I-Beam (text)
        32514,  # Wait
        32515,  # Crosshair
        32516,  # Up Arrow
        32642,  # Size NW-SE
        32643,  # Size NE-SW
        32644,  # Size WE
        32645,  # Size NS
        32646,  # Size All
        32648,  # Hand (links)
        32649,  # App Starting
        32650,  # Help
    ]

    for cursor_id in cursor_ids:
        cursor = ctypes.windll.user32.LoadCursorFromFileW(HIDDEN_CURSOR_PATH)

        if not cursor:
            raise Exception(f"Could not load cursor file: {HIDDEN_CURSOR_PATH}")

        ctypes.windll.user32.SetSystemCursor(cursor, cursor_id)

_cursor_visible = True

def hide_cursor():
    global _cursor_visible
    _cursor_visible = False

def show_cursor():
    global _cursor_visible
    _cursor_visible = True

def cursor_loop():
    global _cursor_visible

    cursor_path = os.path.join(
        BASE_DIR,
        "static",
        "cursors",
        "whitesphere.png"
    )

    img = Image.open(cursor_path).convert("RGBA")
    img = img.resize((80, 80), Image.LANCZOS)

    cursor_w, cursor_h = img.size

    h_instance = win32api.GetModuleHandle(None)

    wc = win32gui.WNDCLASS()
    wc.hInstance = h_instance
    wc.lpszClassName = "AdSkipperFakeCursorWindow"
    wc.lpfnWndProc = {
        win32con.WM_DESTROY: lambda hwnd, msg, wparam, lparam: win32gui.PostQuitMessage(0)
    }

    try:
        class_atom = win32gui.RegisterClass(wc)
    except win32gui.error:
        class_atom = wc.lpszClassName

    ex_style = (
        win32con.WS_EX_LAYERED |
        win32con.WS_EX_TRANSPARENT |
        win32con.WS_EX_TOPMOST |
        win32con.WS_EX_TOOLWINDOW |
        win32con.WS_EX_NOACTIVATE
    )

    hwnd = win32gui.CreateWindowEx(
        ex_style,
        class_atom,
        "AdSkipperFakeCursor",
        win32con.WS_POPUP,
        0,
        0,
        cursor_w,
        cursor_h,
        0,
        0,
        h_instance,
        None
    )

    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)

    screen_dc = win32gui.GetDC(0)
    hdc = win32gui.CreateCompatibleDC(screen_dc)

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = cursor_w
    bmi.bmiHeader.biHeight = -cursor_h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    bits = ctypes.c_void_p()

    hbitmap = gdi32.CreateDIBSection(
        hdc,
        ctypes.byref(bmi),
        DIB_RGB_COLORS,
        ctypes.byref(bits),
        None,
        0
    )

    old_bitmap = win32gui.SelectObject(hdc, hbitmap)

    # Convert RGBA to premultiplied BGRA for UpdateLayeredWindow
    pixels = bytearray()

    for r, g, b, a in img.getdata():
        r = (r * a) // 255
        g = (g * a) // 255
        b = (b * a) // 255

        pixels.extend([b, g, r, a])

    ctypes.memmove(bits, bytes(pixels), len(pixels))

    blend = BLENDFUNCTION()
    blend.BlendOp = AC_SRC_OVER
    blend.BlendFlags = 0
    blend.SourceConstantAlpha = 255
    blend.AlphaFormat = AC_SRC_ALPHA

    try:
        while True:
            win32gui.PumpWaitingMessages()

            if not _cursor_visible:
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    -1000,
                    -1000,
                    cursor_w,
                    cursor_h,
                    win32con.SWP_NOACTIVATE
                )
                time.sleep(1 / 60)
                continue

            x, y = pyautogui.position()

            ppt_dst = POINT(x - cursor_w // 2, y - cursor_h // 2)
            psize = SIZE(cursor_w, cursor_h)
            ppt_src = POINT(0, 0)

            user32.UpdateLayeredWindow(
                hwnd,
                screen_dc,
                ctypes.byref(ppt_dst),
                ctypes.byref(psize),
                hdc,
                ctypes.byref(ppt_src),
                0,
                ctypes.byref(blend),
                ULW_ALPHA
            )

            time.sleep(1 / 60)

    finally:
        win32gui.SelectObject(hdc, old_bitmap)
        gdi32.DeleteObject(hbitmap)
        win32gui.DeleteDC(hdc)
        win32gui.ReleaseDC(0, screen_dc)
        win32gui.DestroyWindow(hwnd)


def safe_cursor_loop():
    try:
        cursor_loop()
    except Exception as e:
        print("Cursor thread failed:")
        print(e)
        traceback.print_exc()

        subprocess.run([
            sys.executable,
            os.path.join(BASE_DIR, "tests", "r.py")
        ])

        os._exit(1)


