import whisper
from threading import Lock
#from voice_processing import *
from flask import Flask, request
from pathlib import Path
import string
import re
import digit_replacer
from fuzzywuzzy import fuzz
import webbrowser

HOST = "127.0.0.1"
PORT = 8000

app = Flask(__name__)
mutex = Lock()

# base, small, medium, large, optionally with [*.en]
model = whisper.load_model("tiny")
"""
Model comparison
Size	Parameters	English-only model	Multilingual model	Required VRAM	Relative speed
tiny	39 M	    tiny.en	            tiny	            ~1 GB	        ~32x
base	74 M	    base.en	            base	            ~1 GB	        ~16x
small	244 M	    small.en	        small	            ~2 GB	        ~6x
medium	769 M	    medium.en	        medium	            ~5 GB	        ~2x
large	1550 M	    N/A	large	                            ~10 GB	        1x
"""

#intents = ["show", "hide", "help"]
intents = ["world help", "world show keyboard", "app open (?P<param>\d+)"]


@app.route('/initIntents', methods=["POST"])
def setIntents():
    global intents
    intents = request.get_json(True)['intents']
    intents.append("merry christmas")
    intents = sorted(intents, key=len, reverse=True)
    print(intents)
    return {
        "intents": intents
    }


@app.route('/transcribe', methods=['POST'])
def transcribe():
    mutex.acquire()
    print(request.get_json(True))
    path = request.get_json(True)['path']

    p = Path(path)
    audio = whisper.load_audio(p)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    print(f"Detected language: {lang}")
    if lang != "en" and lang != "de":
        print("Please use either German or English")

        return {
            "text": "Please use either German or English",
            "matches": []
        }

    # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)
    utterance = result.text.lower()
    utterance = utterance.translate(str.maketrans('', '', string.punctuation))

    # whisper understands "x 1" as "x1", which we don't want,
    # so we split each number here:
    utterance = re.split("(\d+)", utterance)
    utterance = " ".join(utterance)

    # 1. cleaning: replace words with keyword numbers if similar
    # e.g. "for" -> "four"
    utterance = digit_replacer.replaceSimilarWithNumbers(utterance)

    # 2. map string numbers to numbers
    # e.g. "one point 3" -> "1.3"
    utterance = digit_replacer.replaceNumberAsWordsWithDigits(utterance)

    # replace "minus number" with -num
    utterance = re.sub(r"minus +", "-", utterance)

    intentsReplaced = digit_replacer.intentsNumbersReplaced(utterance, intents)
    print("replaced: ")
    print([r for (_, r, __) in intentsReplaced])

    matches = sorted([(intent, fuzz.ratio(utterance, replaced), numbersInUtterance) for (
        intent, replaced, numbersInUtterance) in intentsReplaced], key=lambda tuple: tuple[1], reverse=True)
    
    minThreshold = 50
    matches = list(filter(lambda t: t[1] > minThreshold, matches))

    if (len(matches) >= 1 and matches[0][0] == "merry christmas"):
        webbrowser.open("https://www.youtube.com/watch?v=td4OryjWWMQ&list=PLIUr8pawQYegwEmt4xO87dPvjhrQUxU-W", 1)

    mutex.release()

    matches = [{"intent": matchedIntent,
            "params": params,
            "accuracy": accuracy
            } for (matchedIntent, accuracy, params) in matches]
    
    json = {
        "text": utterance,
        "matches": matches
    }
    print(json)
    return json

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
