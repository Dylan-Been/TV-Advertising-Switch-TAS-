import ctypes

# Restore all default Windows cursors
ctypes.windll.user32.SystemParametersInfoW(
    0x0057,  # SPI_SETCURSORS
    0,
    None,
    0
)

print("Default Windows cursors restored.")