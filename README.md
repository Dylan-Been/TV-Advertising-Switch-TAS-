# The Ad Skipper

Copyright (c) 2026 Dylan Been

Licensed under the GNU General Public License v3.0.
See the LICENSE file for details.

TheAdSkipper is a Windows-based remote control and automatic switching tool for watching Ziggo and YouTube TV from the same machine. It starts a local Flask remote, opens the required browser windows, listens to Ziggo audio with Vosk speech recognition, and switches between Ziggo and YouTube when Dutch ad-break transition phrases are detected.

## What It Does

- Serves a browser remote control at `http://<your-ip>:5000/`.
- Opens YouTube TV in Chrome and Ziggo Go in Microsoft Edge.
- Sends keyboard and mouse input to the active player.
- Switches from Ziggo to YouTube when an ad break is detected.
- Switches back to Ziggo when the program resumes.
- Can pause automatic recording/switch detection from the remote.
- Can restart the running program from the remote.

## Project Structure

```text
.
|-- app.py                  # Flask server and remote-control routes
|-- startup.py              # Main launcher for the server, transcription, and browsers
|-- audio_transcription.py  # Vosk microphone transcription and phrase detection
|-- switch.py               # Window focus, scaling, overlay, and audio mute helpers
|-- app_state.py            # Tracks whether Ziggo or YouTube is active
|-- stop_flag_state.py      # Tracks whether automatic switching is paused
|-- procces_status.py       # Tracks whether a switch/startup process is busy
|-- restart.py              # Restarts the Python program
|-- remote.html             # Main remote-control UI
|-- startup.html            # Startup screen
|-- static/                 # Static files used by the HTML pages
`-- Vosk models/            # Local speech recognition model folder
```

## Requirements

This project is built for Windows because it depends on Windows window handles, browser automation, and per-application audio control.

Install Python dependencies:

```powershell
pip install flask pyautogui pydirectinput pywin32 pygetwindow psutil vosk sounddevice requests pycaw comtypes
```

You also need:

- Google Chrome installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Microsoft Edge installed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- A Dutch Vosk model, such as `vosk-model-small-nl-0.22`
- A working audio input device that captures the Ziggo audio

## Configuration

Before running, check the hard-coded machine-specific values:

- In `startup.py`, update `CHROME_PATH` and `EDGE_PATH` if your browsers are installed somewhere else.
- In `startup.py`, update the IP address used for the startup page:

```python
"http://192.168.68.61:5000/startup"
```

- In `audio_transcription.py`, update `MODEL_PATH` to point to your local Vosk model.
- In `audio_transcription.py`, update `DEVICE` to the correct input device number for your machine.

To find available audio devices, you can run:

```powershell
python -m sounddevice
```

## Running The Project

Start the full application with:

```powershell
python startup.py
```

This will:

1. Start the Flask remote server on port `5000`.
2. Start the transcription thread.
3. Close selected apps such as Chrome, Edge, Firefox, Spotify, Discord, Steam, Notepad, and VLC.
4. Open the startup page, YouTube TV, and Ziggo Go.
5. Focus and maximize the browser windows.
6. Begin listening for transition phrases.

Open the remote from another device on the same network:

```text
http://<computer-ip>:5000/
```

For example:

```text
http://192.168.68.61:5000/
```

## Remote Routes

The Flask app exposes these routes:

| Route | Action |
| --- | --- |
| `/` | Opens the main remote UI |
| `/startup` | Opens the startup screen |
| `/up` | Presses arrow up |
| `/down` | Presses arrow down |
| `/left` | Navigates left, or Shift+Tab while in Ziggo |
| `/right` | Navigates right, or Tab while in Ziggo |
| `/OK` | Presses Enter when no process is busy |
| `/Back` | Presses Escape when no process is busy |
| `/switch` | Toggles between Ziggo and YouTube |
| `/Scale` | Toggles fullscreen/scaling for the active player |
| `/record` | Toggles automatic switching pause/resume |
| `/icon` | Returns the current record icon state |
| `/Restart` | Restarts the program |
| `/Status_Restart` | Returns the current process status |
| `/youtube` | Switches directly to YouTube |
| `/ziggo` | Switches directly to Ziggo |

## Automatic Switching

`audio_transcription.py` listens to the configured audio input and transcribes Dutch speech with Vosk. It watches for simple transition phrases:

- Switch to YouTube when Ziggo says phrases like `reclame`, `tot zo`, or `we zijn zo terug`.
- Switch back to Ziggo when it hears phrases like `welkom terug` or `we zijn terug`.

The automatic switching can be paused or resumed with the remote's record control.

## Notes

- Keep the computer awake while the tool is running.
- Make sure Windows allows Python through the firewall if you want to access the remote from another device.
- Browser window titles must include `YouTube` and `Ziggo` for the window switching helpers to find them.
- The app uses screen coordinates for some Ziggo controls, so browser layout or display scaling changes may require small coordinate adjustments in `switch.py` or `app.py`.

## Troubleshooting

If the remote does not load:

- Confirm `python startup.py` is still running.
- Check that port `5000` is not blocked.
- Use the computer's local network IP address, not `localhost`, from another device.

If switching does not work:

- Confirm Chrome and Edge are open with YouTube and Ziggo.
- Confirm the window titles contain `YouTube` and `Ziggo`.
- Check whether the process state is stuck by opening `/Status_Restart`.

If transcription does not work:

- Confirm `MODEL_PATH` points to the Vosk model folder.
- Confirm `DEVICE` matches the correct audio input.
- Run `python -m sounddevice` to inspect available devices.
