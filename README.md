## TV Advertising Switch (TAS) 

Copyright (c) 2026 Dylan Been

Licensed under the MIT License. See the LICENSE file for details.

The Ad Skipper is a Windows tool for controlling a streaming app and YouTube TV from a phone or tablet on the same network. It is tested with Ziggo Go as the main streaming app, but another app or website can be used if you update the startup URL, window title matching, audio routing, and detection phrases. It starts a local Flask remote, opens the browser windows, listens to streaming audio with Vosk speech recognition, and automatically switches between the streaming app and YouTube when ad-break phrases are detected.

## Features

- Serves a remote control at `http://<computer-ip>:5000/`.
- Shows a startup page with a QR code for the current device IP.
- Opens YouTube TV in Chrome and the configured streaming app in Microsoft Edge.
- Sends keyboard and mouse input to the active player.
- Uses a touchpad area in the remote for mouse movement and clicks.
- Switches from the configured streaming app to YouTube when an ad break is detected.
- Switches back to the configured streaming app when the program resumes.
- Lets you pause or resume automatic switching from the remote.
- Can restart the running program from the remote.

## Requirements

This project is built for Windows. It depends on Windows window handles, browser automation, a virtual audio cable, and per-application audio control.

You need:

- Python 3.13.3. This is the version the project was tested with.
- Google Chrome installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Install the YouTube TV on PC Chrome extension for a better YouTube experience at `https://chromewebstore.google.com/detail/youtube-tv-on-pc/jldjbkccldgbegjpggphaeikombjmnkh`
- Microsoft Edge installed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`.
- VB-CABLE installed so streaming-app audio can be captured by the transcription service while you still hear it through your speakers.
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

- `CABLE Input` is the playback device. Send Edge/streaming-app audio into this device.
- `CABLE Output` is the recording device. The Ad Skipper listens to this device for transcription.

To make this work, Edge should play the streaming-app audio into `CABLE Input`, and Windows should listen to `CABLE Output` through your real speakers or TV. That gives the app a clean audio feed while you can still hear the stream normally.

### Route Edge Audio To VB-CABLE

1. Start playing Ziggo Go, or your chosen streaming app, in Microsoft Edge.
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

- Edge sends streaming-app audio to `CABLE Input`.
- VB-CABLE exposes that audio as `CABLE Output`.
- The Ad Skipper records from `CABLE Output`.
- Windows plays `CABLE Output` back through your real speakers or TV.

## Using Another Streaming App

Ziggo Go is the tested default, but the same setup can be adapted for another streaming app or website. The important part is that the app plays audio through Microsoft Edge, because the startup flow, audio routing instructions, and switching helpers are built around Edge for the main streaming app.

To replace Ziggo with another app, update the Ziggo-specific values and helpers:

- In `src/startup.py`, change `ZIGGO_URL` to the website you want to open.
- In `src/actions/switch.py`, update the window title checks that look for `Ziggo`.
- In `src/app.py`, update routes or behavior that check whether the current state is `ziggo`.
- In `src/services/audio_transcription.py`, update the phrases used to detect ad breaks and content returning.
- In Windows Volume mixer, route Edge audio to `CABLE Input` for the app you are using.

The `/removeoverlay` route is also app-specific. It currently clicks a fixed screen position to remove a YouTube overlay. If your chosen app does not have a similar overlay, or if the click position does not make sense for that app, remove the overlay button from `templates/remote.html` or change the `/removeoverlay` behavior in `src/app.py`.

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
8. Open Ziggo Go, or the configured streaming app, in Microsoft Edge.
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
| `/left` | Presses Arrow Left, or Shift+Tab while the streaming app is active |
| `/right` | Presses Arrow Right, or Tab while the streaming app is active |
| `/OK` | Presses Enter when the process state is clear |
| `/Back` | Presses Escape when the process state is clear |
| `/switch` | Toggles between the streaming app and YouTube |
| `/removeoverlay` | Clicks a fixed overlay-removal position; remove or change this if your app does not need it |
| `/record` | Pauses or resumes automatic switching |
| `/icon` | Returns the current microphone icon name |
| `/Restart` | Restarts the running program |
| `/Status_Restart` | Returns the current process state |
| `/mouse_move` | Moves the mouse cursor and scrolls near vertical screen edges |
| `/mouse_click` | Clicks the left mouse button |
| `/youtube` | Switches directly to YouTube |
| `/ziggo` | Switches directly to the configured streaming app; Ziggo is the default state name in code |

## Automatic Switching

`src/services/audio_transcription.py` listens to the VB-CABLE input and transcribes Dutch audio with Vosk. The default phrases are written for Ziggo Go, but they can be changed for another app or language.

It switches from the streaming app to YouTube when it detects phrases such as:

- `reclame`
- `tot zo`
- `we zijn zo terug`

It switches from YouTube back to the streaming app when it detects phrases such as:

- `welkom terug`
- `we zijn terug`

Automatic switching can be paused or resumed with the microphone button in the remote.

## Future Updates And Ideas

The current ad detection uses simple phrase matching on the transcribed audio. A future improvement is local AI-based ad detection with a local LLM, which should make ad detection more accurate and less dependent on fixed phrases.

Suggestions, improvements, and ideas are welcome. If you notice a better way to detect ads, route audio, support more streaming apps, improve the remote UI, or make setup easier, I would be glad to hear it.

## Notes

- Keep the computer awake while the tool is running.
- The phone or tablet remote must be on the same network as the computer.
- Browser window titles must match the names used by the switching helpers. By default, those are `YouTube` and `Ziggo`.
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

- Confirm Chrome and Edge are open with YouTube TV and the configured streaming app.
- Confirm the window titles match the names used by the switching helpers. By default, those are `YouTube` and `Ziggo`.
- Open `/Status_Restart` and check whether the process state is stuck.

If transcription does not work:

- Confirm VB-CABLE is installed.
- Confirm Edge output is set to `CABLE Input (VB-Audio Virtual Cable)` in Windows Volume mixer.
- Confirm `CABLE Output (VB-Audio Virtual Cable)` has `Listen to this device` enabled.
- Confirm the Vosk model folder exists at `models/vosk-model-small-nl-0.22`.
- Run `python -m sounddevice` and check whether a `CABLE Output` or `VB-Audio` input device appears.
- Set `ADSKIPPER_AUDIO_DEVICE` if auto-detection finds the wrong device.
