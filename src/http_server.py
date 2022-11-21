import whisper
from voice_processing import *
from flask import Flask, request

HOST = "127.0.0.1"
PORT = 8000

app = Flask(__name__)

model = whisper.load_model("tiny") #base, small, medium, large, optionally with [*.en]
"""
Model comparison
Size	Parameters	English-only model	Multilingual model	Required VRAM	Relative speed
tiny	39 M	    tiny.en	            tiny	            ~1 GB	        ~32x
base	74 M	    base.en	            base	            ~1 GB	        ~16x
small	244 M	    small.en	        small	            ~2 GB	        ~6x
medium	769 M	    medium.en	        medium	            ~5 GB	        ~2x
large	1550 M	    N/A	large	                            ~10 GB	        1x
"""


@app.route('/transcribe', methods=['POST'])
def transcribe():
    path = request.get_json(True)['path']
    print(path)
    
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(path)
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
    else:
        # decode the audio
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        utterance = result.text
        intent = get_intent(utterance)
        #result = model.transcribe(path)
        
        # print the recognized text
        print(f"User said: {utterance}. Intent received: {intent}")
        
        return {
            "text": utterance
            "intent": intent
        }


if __name__ == '__main__':
    app.run(debug=True)´
