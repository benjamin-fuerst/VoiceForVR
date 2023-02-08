# VoiceForVR 

![Image of a farm build using voice intents](Screenshot%202023-02-06%20201903.png?raw=true)

This project provides a simple intent matching server for python, based on whisper. You send a json pointing to your audio file, and the server responses with a list of matched intents and their accuracies.

The project was developed during the Programming in VR project seminar at HPI.

To start the server, run
`python3 -m flask --app ./src/http_server.py run`

or

```python
python3 ./src/http_server.py
```

for a debug server.

The server listens for POST requests on `/transcribe` and expects a json file like

```ts
{
    path: // global path to voice recording
}
```

To initialize intents, send a POST request on `\initIntents` with a body like

```ts
{
    intents: ["one intent"]
}
```

# prerequisites

- python 3.x
- ffmpeg

## installing whisper

Make sure you have python 3.x and ffmpeg installed.

Then run in your command line:

```sh
//install whisper
pip install git+https://github.com/openai/whisper.git 
//confirm whisper works, start python interpreter
python
>>>import whisper
>>>model = whisper.load_model("tiny")
>>>result = model.transcribe("audio.mp3")
>>>print(result["text"])
>>>exit()
```

# tests
the functions in [digit_replacer.py](src/digit_replacer.py), have doctests. You can run them using
```py
python3 -m doctest digit_replacer.py
```
