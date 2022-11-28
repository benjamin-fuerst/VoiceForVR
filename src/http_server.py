import whisper
from threading import Lock
#from voice_processing import *
from flask import Flask, request
from pathlib import Path
import string
import re

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
    print(intents)
    return {
        "intents": intents
    }


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if mutex.locked():
        print("Currently locked, waiting")
    mutex.acquire()
    print(request.get_json(True))
    path = request.get_json(True)['path']
    print(path)

    p = Path(path)
    # load audio and pad/trim it to fit 30 seconds
    print(p, p.exists())
    print(str(p))
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
            "text": "Please use either German or English"
        }

    # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)
    utterance = result.text.lower()
    utterance = utterance.translate(str.maketrans('', '', string.punctuation))

    jsn = None
    for i in range(len(intents)):
        intents[i] = re.compile(intents[i])
        print(intents)

    for i in range(len(intents)):
        match = intents[i].match(utterance)
        if match is not None:
            search = intents[i].search(utterance)
            if search.groups() == ():
                jsn = {"intent": utterance,
                       "text": utterance}
            else:
                params = search.groupdict()
                intent = utterance.split(" " + params[list(params.keys())[0]])[0]
                jsn = {"intent": intent,
                       "text": utterance}
                jsn = jsn | params
    
    mutex.release()
    print("Lock free again")
    if jsn is not None:
        return jsn
    else:
        print("no match")
        return {"intent": "null",
                "text": "null"}



if __name__ == '__main__':
    app.run(debug=True, threaded=True)
