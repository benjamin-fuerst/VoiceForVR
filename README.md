# VoiceForVR  
To start the server, run
`python3 -m flask --app ./src/http_server.py run --port 8000`

The server listens for POST requests on `/transcribe` and expects a json file like

```ts
{
    path: // global path to voice recording
}
```

# prerequisites

- python 3.x
- ffmpeg

## installing whisper

Make sure you have python 3.x and ffmpeg installed.

Then run in your command line:

```
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