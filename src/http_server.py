import whisper
from threading import Lock
#from voice_processing import *
from flask import Flask, request
from pathlib import Path
import string
import re
import digit_replacer
from fuzzywuzzy import fuzz

app = Flask(__name__)
mutex = Lock()  # ensure whisper is only called once at a time

"""
Model comparison
Size	Parameters	English-only model	Multilingual model	Required VRAM	Relative speed
tiny	39 M	    tiny.en	            tiny	            ~1 GB	        ~32x
base	74 M	    base.en	            base	            ~1 GB	        ~16x
small	244 M	    small.en	        small	            ~2 GB	        ~6x
medium	769 M	    medium.en	        medium	            ~5 GB	        ~2x
large	1550 M	    N/A	large	                            ~10 GB	        1x
"""
model = whisper.load_model("base.en")

intents = ["world help", "world show keyboard", "app open (?P<param>\d+)"]


@app.route('/initIntents', methods=["POST"])
def setIntents():
    global intents
    intents = request.get_json(True)['intents']
    intents = sorted(intents, key=len, reverse=True)
    print(intents)
    return {
        "intents": intents
    }


@app.route('/transcribe', methods=['POST'])
def transcribe():
    mutex.acquire()

    path = request.get_json(True)['path']
    p = Path(path)
    audio = whisper.load_audio(p)
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio)

    # lowercase and remove puncation
    utterance = result["text"].lower()
    utterance = utterance.translate(str.maketrans('', '', string.punctuation))

    # whisper understands "x 1" as "x1", which we don't want:
    utterance = " ".join(re.split("(\d+)", utterance))

    utterance = digit_replacer.replaceSimilarWithNumbers(utterance)
    utterance = digit_replacer.replaceNumberAsWordsWithDigits(utterance)
    utterance = re.sub(r"minus +", "-", utterance)
    utterance = digit_replacer.clearWhitespace(utterance)

    # succesively, try to replace wildcards in intents with fitting occurances in utterance
    intentsReplaced = digit_replacer.intentsNumbersReplaced(utterance, intents)
    intentsReplaced = digit_replacer.intentsRestReplaced(
        utterance, intentsReplaced)

    matches = [(intent, digit_replacer.similarity(utterance, replaced.strip()), numbersInUtterance) for (
        intent, replaced, numbersInUtterance) in intentsReplaced]
    matches = sorted(matches, key=lambda tuple: tuple[1], reverse=True)

    minThreshold = 50
    matches = list(filter(lambda t: t[1] > minThreshold, matches))

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
