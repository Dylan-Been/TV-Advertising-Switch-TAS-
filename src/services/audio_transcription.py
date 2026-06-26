import requests
import vosk
import sounddevice as sd
import queue
import json
import time
import os

from src.states.app_state import switch_currentstate, get_currentstate
from src.states.stop_flag_state import get_stop_flag
from src.services.network import get_server_url

DEVICE_ENV_VAR = "ADSKIPPER_AUDIO_DEVICE"
AUDIO_DEVICE_NAMES = ("cable output", "vb-audio")
q = queue.Queue()


# getting the absolute path to the main directiory 
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
#getting the transcribe model
MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "vosk-model-small-nl-0.22"
)
#setting the transcribe model up 
model_Dutch = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model_Dutch, 48000)
recognizer.SetWords(True)


def get_audio_device():
    override = os.getenv(DEVICE_ENV_VAR)
    if override:
        try:
            return int(override)
        except ValueError as exc:
            raise RuntimeError(
                f"{DEVICE_ENV_VAR} must be a device number, got {override!r}"
            ) from exc

    devices = sd.query_devices()
    available_inputs = []

    for index, device in enumerate(devices):
        if device["max_input_channels"] <= 0:
            continue

        name = device["name"]
        available_inputs.append(f"{index}: {name}")

        if any(match in name.lower() for match in AUDIO_DEVICE_NAMES):
            print(f"Using audio device {index}: {name}")
            return index

    raise RuntimeError(
        "Could not find the VB-CABLE input device automatically. "
        f"Set {DEVICE_ENV_VAR} to the device number. Available input devices: "
        + ", ".join(available_inputs)
    )


#getting the status of the vm cable 
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


def start_transcription():
    server_url = get_server_url()
    audio_device = get_audio_device()

    #start the listing to the vm cable 
    with sd.RawInputStream(
        samplerate=48000,
        blocksize=8000,
        device=audio_device,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        print("Listening to Ziggo audio...")
        
        #detecting ad with a simple bag of words method
        while True:
            data = q.get()
            stop_flag = get_stop_flag()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(text)
               
                if (
                    "reclame" in text or "tot zo" in text or "we zijn zo terug" in text
                ) and get_currentstate() == "ziggo":
                    print("Ad detected")

                    if not stop_flag:
                        print("switch to youtube...")
                        requests.get(f"{server_url}/youtube")
                        switch_currentstate("youtube")

                if (
                    "welkom terug" in text or "we zijn terug" in text
                ) and get_currentstate() == "youtube":
                    print("Content resumed")

                    if not stop_flag:
                        print("switch back to ziggo...")
                        requests.get(f"{server_url}/ziggo")
                        switch_currentstate("ziggo")
