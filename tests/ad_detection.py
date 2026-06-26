import requests
import subprocess
import time
#local llm ad detection (work in progress, maybe not in progress)
def ensure_ollama_running():
    try:
        r = requests.get("http://localhost:11434", timeout=2)

        if r.status_code == 200:
            print("Ollama already running")
            return True

    except Exception:
        print("Ollama not running, starting it...")

    subprocess.Popen(
        ["C:\\Users\\Dylan\\AppData\\Local\\Programs\\Ollama\\ollama.exe", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait up to 15 seconds
    for _ in range(15):
        try:
            r = requests.get("http://localhost:11434", timeout=2)

            if r.status_code == 200:
                print("Ollama started successfully")
                return True

        except Exception:
            pass

        time.sleep(1)

    print("Failed to start Ollama")
    return False


def classify_ad(text):
    prompt = f"""
You are a strict Dutch TV transition detector.

Classify ONLY based on whether the transcript contains a clear transition phrase.

Return:
AD = the presenter/channel says the program is going to commercials or will be back soon.
CONTENT = the presenter/channel welcomes viewers back after commercials.
END = the program is clearly ending.
FILLER = anything else, including normal ads, brand names, news, conversation, or unclear text.

Important:
- Do NOT classify normal advertisements as AD.
- AD only means: the show is starting a commercial break.
- CONTENT only means: the show has resumed after a commercial break.
- If unsure, return FILLER.

Examples:
"we zijn zo terug" -> AD
"tot zo" -> AD
"tijd voor reclame" -> AD
"tot zo reclame"-> AD
"welkom terug" -> CONTENT
"we zijn terug" -> CONTENT
"dit programma wordt mede mogelijk gemaakt door marktplaats" -> FILLER
"nu bij coolblue korting" -> FILLER

Transcript:
{text}

Answer only one word:
AD
CONTENT
END
FILTER
"""

    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 3
        }
    })

    answer = r.json()["response"].strip().upper()

    if "AD" in answer:
        return "AD"
    if "CONTENT" in answer:
        return "CONTENT"
    if "END" in answer:
        return "END"
    return "FILLER"