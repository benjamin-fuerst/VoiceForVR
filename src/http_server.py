import whisper
from flask import Flask, request

HOST = "127.0.0.1"
PORT = 8000

app = Flask(__name__)

model = whisper.load_model("tiny")


@app.route('/transcribe', methods=['POST'])
def transcribe():
    path = request.get_json(True)['path']
    print(path)
    result = model.transcribe(path)
    print(result['text'])
    return {
        "text": result['text']
    }


if __name__ == '__main__':
    app.run(debug=True)
