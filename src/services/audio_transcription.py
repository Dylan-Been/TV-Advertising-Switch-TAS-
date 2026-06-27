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

# helper function to find the correct audio device 
def find_audio_device():
    # check if audio device is set in env (this can be set by running: $env:ADSKIPPER_AUDIO_DEVICE="your device number" before starting)
    preferred = os.getenv(DEVICE_ENV_VAR)

    devices = sd.query_devices()

    # 1. Manual override by index
    if preferred:
        return int(preferred)

    # 2. Auto select exact wanted device/backend
    for i, device in enumerate(devices):
        name = device["name"].lower()
        hostapi = sd.query_hostapis(device["hostapi"])["name"].lower()

        if (
            "cable output" in name
            and "vb-audio" in name
            and "wasapi" in hostapi
            and device["max_input_channels"] >= 2
        ):
            return i

    raise RuntimeError("Could not find VB-Audio CABLE Output WASAPI input device")

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

#getting the status of the vm cable 
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


def start_transcription():
    server_url = get_server_url()
    audio_device = find_audio_device()
    print("Using audio device:", audio_device, sd.query_devices(audio_device))

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
                #print output of transcription 
                #print(text)
               
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
