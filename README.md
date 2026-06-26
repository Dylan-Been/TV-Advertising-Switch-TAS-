# The Ad Skipper

Copyright (c) 2026 Dylan Been

Licensed under the MIT License. See the LICENSE file for details.

The Ad Skipper is a Windows tool for controlling Ziggo Go and YouTube TV from a phone or tablet on the same network. It starts a local Flask remote, opens the browser windows, listens to Ziggo audio with Vosk speech recognition, and automatically switches between Ziggo and YouTube when Dutch ad-break phrases are detected.

## Features

- Serves a remote control at `http://<computer-ip>:5000/`.
- Shows a startup page with a QR code for the current device IP.
- Opens YouTube TV in Chrome and Ziggo Go in Microsoft Edge.
- Sends keyboard and mouse input to the active player.
- Uses a touchpad area in the remote for mouse movement and clicks.
- Switches from Ziggo to YouTube when an ad break is detected.
- Switches back to Ziggo when the program resumes.
- Lets you pause or resume automatic switching from the remote.
- Can restart the running program from the remote.

## Requirements

This project is built for Windows. It depends on Windows window handles, browser automation, a virtual audio cable, and per-application audio control.

You need:

- Python 3.13.3. This is the version the project was tested with.
- Google Chrome installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Microsoft Edge installed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`.
- VB-CABLE installed so Ziggo audio can be captured by the transcription service while you still hear it through your speakers.
- The Dutch Vosk model folder `models/vosk-model-small-nl-0.22`.
- Windows firewall access for Python if you want to open the remote from another device.

Tested hardware:

| Component | Tested setup |
| --- | --- |
| CPU | Intel Core i5-7500T |
| RAM | 8 GB |
| OS | Windows |
| Network | Phone/tablet and computer on the same local network |
| Audio | VB-CABLE virtual audio device |

Recommended minimum hardware:

- Intel Core i5-class CPU or similar.
- 8 GB RAM.
- Stable local network connection.
- Audio output device such as speakers, headphones, HDMI TV, or default Windows playback device.

Install the Python packages:

```powershell
pip install flask pyautogui pydirectinput pywin32 pygetwindow psutil vosk sounddevice requests pycaw comtypes pygame pillow
```

Tested install versions:

| Tool or package | Tested version |
| --- | --- |
| Python | 3.13.3 |
| Flask | 1.1.2 |
| PyAutoGUI | 0.9.54 |
| PyDirectInput | 1.0.4 |
| pywin32 | 311 |
| PyGetWindow | 0.0.9 |
| psutil | 7.1.3 |
| vosk | 0.3.45 |
| sounddevice | 0.5.5 |
| requests | 2.32.5 |
| pycaw | 20251023 |
| comtypes | 1.4.16 |
| pygame | 2.6.1 |
| pillow | 11.3.0 |

VB-CABLE is available from:

```text
https://vb-audio.com/Cable/index.htm
```

## Project Layout

```text
.
|-- README.md
|-- scripts/
|   `-- tas.bat
|-- src/
|   |-- app.py                         # Flask routes and remote-control actions
|   |-- startup.py                     # Main launcher
|   |-- actions/
|   |   |-- restart.py                 # Program restart helper
|   |   `-- switch.py                  # Browser focus, switching, and audio mute helpers
|   |-- cursor/
|   |   |-- cursor_behavior.py         # Cursor auto-hide behavior
|   |   `-- custum_cursor.py           # Custom cursor overlay
|   |-- services/
|   |   |-- audio_transcription.py     # Vosk transcription and ad phrase detection
|   |   `-- network.py                 # Current-device IP detection
|   `-- states/
|       |-- app_state.py               # Current app state
|       |-- procces_status.py          # Busy or clear process state
|       `-- stop_flag_state.py         # Automatic switching pause state
|-- static/
|-- templates/
|   |-- remote.html                    # Phone/tablet remote UI
|   `-- startup.html                   # QR startup screen
`-- models/
    `-- vosk-model-small-nl-0.22/
```

## Setup

1. Install the Python packages from the Requirements section.
2. Install VB-CABLE.
3. Make sure the Dutch Vosk model exists at:

```text
models/vosk-model-small-nl-0.22
```

4. Configure VB-CABLE as described below.
5. Check browser paths in `src/startup.py` if Chrome or Edge are installed somewhere else:

```python
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

You do not need to hard-code the computer IP. The app detects the current device IP when it starts.

You usually do not need to hard-code the audio input device either. The transcription service searches for an input device containing `cable output` or `vb-audio`.

If auto-detection picks the wrong audio device, set an override before starting:

```powershell
$env:ADSKIPPER_AUDIO_DEVICE="18"
python -m src.startup
```

To list audio devices:

```powershell
python -m sounddevice
```

## Configure VB-CABLE

VB-CABLE creates two Windows audio devices:

- `CABLE Input` is the playback device. Send Edge/Ziggo audio into this device.
- `CABLE Output` is the recording device. The Ad Skipper listens to this device for transcription.

To make this work, Edge should play Ziggo audio into `CABLE Input`, and Windows should listen to `CABLE Output` through your real speakers or TV. That gives the app a clean audio feed while you can still hear Ziggo normally.

### Route Edge Audio To VB-CABLE

1. Start playing Ziggo Go in Microsoft Edge.
2. Open Windows Settings.
3. Go to `System` > `Sound` > `Volume mixer`.
4. Find `Microsoft Edge` in the apps list.
5. Set the Edge output device to `CABLE Input (VB-Audio Virtual Cable)`.

If Edge does not appear in the Volume mixer yet, play audio in Edge and reopen the Volume mixer.

### Listen To VB-CABLE Through Speakers

1. Open Windows Settings.
2. Go to `System` > `Sound` > `More sound settings`.
3. Open the `Recording` tab.
4. Select `CABLE Output (VB-Audio Virtual Cable)`.
5. Click `Properties`.
6. Open the `Listen` tab.
7. Enable `Listen to this device`.
8. In `Playback through this device`, choose your real speakers, headphones, HDMI TV, or default playback device.
9. Click `Apply`, then `OK`.

After this setup:

- Edge sends Ziggo audio to `CABLE Input`.
- VB-CABLE exposes that audio as `CABLE Output`.
- The Ad Skipper records from `CABLE Output`.
- Windows plays `CABLE Output` back through your real speakers or TV.

## Running

Start the full application from the project root:

```powershell
python -m src.startup
```

Or use the batch file:

```powershell
.\scripts\tas.bat
```

On startup, the program will:

1. Mark the process state as busy.
2. Close selected apps such as Chrome, Edge, Firefox, Spotify, Discord, Steam, Notepad, and VLC.
3. Start the Flask remote server on port `5000`.
4. Start the custom cursor helpers.
5. Start the audio transcription thread.
6. Open the startup QR page in Chrome.
7. Open YouTube TV in Chrome.
8. Open Ziggo Go in Microsoft Edge.
9. Focus and maximize the browser windows.
10. Mark the process state as clear.

Open the remote from another device on the same network:

```text
http://<computer-ip>:5000/
```

The startup page shows a QR code for the detected URL.

## Remote Routes

| Route | Action |
| --- | --- |
| `/` | Opens the main remote UI |
| `/startup` | Opens the startup QR page |
| `/up` | Presses Arrow Up |
| `/down` | Presses Arrow Down |
| `/left` | Presses Arrow Left, or Shift+Tab while Ziggo is active |
| `/right` | Presses Arrow Right, or Tab while Ziggo is active |
| `/OK` | Presses Enter when the process state is clear |
| `/Back` | Presses Escape when the process state is clear |
| `/switch` | Toggles between Ziggo and YouTube |
| `/removeoverlay` | Clicks to remove the YouTube overlay |
| `/record` | Pauses or resumes automatic switching |
| `/icon` | Returns the current microphone icon name |
| `/Restart` | Restarts the running program |
| `/Status_Restart` | Returns the current process state |
| `/mouse_move` | Moves the mouse cursor and scrolls near vertical screen edges |
| `/mouse_click` | Clicks the left mouse button |
| `/youtube` | Switches directly to YouTube |
| `/ziggo` | Switches directly to Ziggo |

## Automatic Switching

`src/services/audio_transcription.py` listens to the VB-CABLE input and transcribes Dutch audio with Vosk.

It switches from Ziggo to YouTube when it detects phrases such as:

- `reclame`
- `tot zo`
- `we zijn zo terug`

It switches from YouTube back to Ziggo when it detects phrases such as:

- `welkom terug`
- `we zijn terug`

Automatic switching can be paused or resumed with the microphone button in the remote.

## Notes

- Keep the computer awake while the tool is running.
- The phone or tablet remote must be on the same network as the computer.
- Browser window titles must include `YouTube` and `Ziggo` so the switching helpers can find them.
- Some actions use screen coordinates, so display scaling or browser layout changes may require coordinate adjustments in `src/app.py` or `src/actions/switch.py`.
- The startup QR code is generated from the detected local IP.

## Troubleshooting

If the remote does not load:

- Confirm the program is running with `python -m src.startup` or `.\scripts\tas.bat`.
- Confirm Windows firewall allows Python on the local network.
- Confirm port `5000` is not blocked or already in use.
- Use the computer's local network IP from another device, not `localhost`.

If the QR code opens the wrong address:

- Make sure the computer is connected to the same network as the phone or tablet.
- Restart the app after changing Wi-Fi or Ethernet networks.

If switching does not work:

- Confirm Chrome and Edge are open with YouTube TV and Ziggo Go.
- Confirm the window titles contain `YouTube` and `Ziggo`.
- Open `/Status_Restart` and check whether the process state is stuck.

If transcription does not work:

- Confirm VB-CABLE is installed.
- Confirm Edge output is set to `CABLE Input (VB-Audio Virtual Cable)` in Windows Volume mixer.
- Confirm `CABLE Output (VB-Audio Virtual Cable)` has `Listen to this device` enabled.
- Confirm the Vosk model folder exists at `models/vosk-model-small-nl-0.22`.
- Run `python -m sounddevice` and check whether a `CABLE Output` or `VB-Audio` input device appears.
- Set `ADSKIPPER_AUDIO_DEVICE` if auto-detection finds the wrong device.
