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

app = Flask(__name__)
mutex = Lock()

# base, small, medium, large, optionally with [*.en]
model = whisper.load_model("tiny.en")
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

    # decode the audio
    #options = whisper.DecodingOptions(fp16=False)
    result = model.transcribe(audio)

    # lowercase and remove puncation
    utterance = result["text"].lower()
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
    intentsReplaced = digit_replacer.intentsRestReplaced(utterance, intentsReplaced)

    matches = [(intent, digit_replacer.similarity(utterance.strip(), replaced.strip()), numbersInUtterance) for (
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
