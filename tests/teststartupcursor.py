import pygame
import win32gui
import win32con
import pyautogui
import os

pygame.init()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cursor_path = os.path.join(
    BASE_DIR,
    "static",
    "cursors",
    "whitesphere.png"
)

cursor_img = pygame.image.load(cursor_path)

cursor_img = pygame.transform.smoothscale(
    cursor_img,
    (80, 80)
)

cursor_w = cursor_img.get_width()
cursor_h = cursor_img.get_height()

screen = pygame.display.set_mode(
    (cursor_w, cursor_h),
    pygame.NOFRAME | pygame.SRCALPHA
)

hwnd = pygame.display.get_wm_info()["window"]

style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
style |= win32con.WS_EX_LAYERED
style |= win32con.WS_EX_TRANSPARENT
style |= win32con.WS_EX_TOPMOST
style |= win32con.WS_EX_TOOLWINDOW
style |= win32con.WS_EX_NOACTIVATE

win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

win32gui.SetLayeredWindowAttributes(
    hwnd,
    0,
    255,
    win32con.LWA_ALPHA
)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    x, y = pyautogui.position()

    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        x - cursor_w // 2,
        y - cursor_h // 2,
        cursor_w,
        cursor_h,
        win32con.SWP_NOACTIVATE
    )

    screen.fill((0, 0, 0, 0))
    screen.blit(cursor_img, (0, 0))
    pygame.display.flip()

    clock.tick(60)