import requests
import vosk
import sounddevice as sd
import queue
import json
import time
import os

from src.states.app_state import switch_currentstate, get_currentstate
from src.states.stop_flag_state import get_stop_flag
# 
DEVICE = 18 #change this to the correct device test it with tests/testaudio.py find the device connected to VM CABLE INPUT 
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
    #start the listing to the vm cable 
    with sd.RawInputStream(
        samplerate=48000,
        blocksize=8000,
        device=DEVICE,
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
                #print(text)
               
                if (
                    "reclame" in text or "tot zo" in text or "we zijn zo terug" in text
                ) and get_currentstate() == "ziggo":
                    print("Ad detected")

                    if not stop_flag:
                        print("switch to youtube...")
                        requests.get("http://192.168.68.63:5000/youtube")
                        switch_currentstate("youtube")

                if (
                    "welkom terug" in text or "we zijn terug" in text
                ) and get_currentstate() == "youtube":
                    print("Content resumed")

                    if not stop_flag:
                        print("switch back to ziggo...")
                        requests.get("http://192.168.68.63:5000/ziggo")
                        switch_currentstate("ziggo")
