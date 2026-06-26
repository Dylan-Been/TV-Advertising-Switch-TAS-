import sounddevice as sd
#find all input devices 
for i, dev in enumerate(sd.query_devices()):
    api = sd.query_hostapis()[dev["hostapi"]]["name"]

    print(
        f"{i:2d} | "
        f"{api:15s} | "
        f"In:{dev['max_input_channels']} "
        f"Out:{dev['max_output_channels']} | "
        f"{dev['name']}"
    )

import comtypes
from pycaw.pycaw import AudioUtilities

comtypes.CoInitialize()

for i, session in enumerate(AudioUtilities.GetAllSessions()):
    print("-----", i)
    print("Process:", session.Process.name() if session.Process else None)
    print("DisplayName:", session.DisplayName)
    print("IconPath:", session.IconPath)

comtypes.CoUninitialize()
#test the rate that is correct for te device 
DEVICE = 15

for rate in [16000, 44100, 48000]:
    try:
        sd.check_input_settings(
            device=DEVICE,
            samplerate=rate,
            channels=1,
            dtype="int16"
        )
        print("Works:", rate)
    except Exception as e:
        print("Fails:", rate, e)