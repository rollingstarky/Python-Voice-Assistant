import time
import os
import pyaudio
import wave

import speech_recognition as sr
from aip import AipSpeech

import requests
import json

# Baidu Speech API, replace with your personal key
APP_ID = 'Your AppID'
API_KEY = 'Your API Key'
SECRET_KEY = 'Your Secret Key'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


# Turing API, replace with your personal key
TURING_KEY = "Your appkey"
URL = "http://openapi.tuling123.com/openapi/api/v2"
HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}


# Use SpeechRecognition to record
def rec(rate=16000):
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:
        print("please say something")
        audio = r.listen(source)

    with open("recording.wav", "wb") as f:
        f.write(audio.get_wav_data())


# Use Baidu Speech as STT engine
def listen():
    with open('recording.wav', 'rb') as f:
        audio_data = f.read()

    result = client.asr(audio_data, 'wav', 16000, {
        'dev_pid': 1536,
    })

    result_text = result["result"][0]

    print("you said: " + result_text)

    return result_text


# The Turing chatbot
def robot(text=""):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": ""
            },
            "selfInfo": {
                "location": {
                    "city": "杭州",
                    "street": "网商路"
                }
            }
        },
        "userInfo": {
            "apiKey": TURING_KEY,
            "userId": "starky"
        }
    }

    data["perception"]["inputText"]["text"] = text
    response = requests.request("post", URL, json=data, headers=HEADERS)
    response_dict = json.loads(response.text)

    result = response_dict["results"][0]["values"]["text"]
    print("the AI said: " + result)
    return result


# Baidu Speech as TTS engine
def speak(text=""):
    result = client.synthesis(text, 'zh', 1, {
        'spd': 4,
        'vol': 5,
        'per': 4,
    })

    if not isinstance(result, dict):
        with open('audio.mp3', 'wb') as f:
            f.write(result)


# Pyaudio to play mp3 file
def play():
    os.system('sox audio.mp3 audio.wav')
    wf = wave.open('audio.wav', 'rb')
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    stream.start_stream()

    while stream.is_active():
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    wf.close()

    p.terminate()


while True:
    rec()
    request = listen()
    response = robot(request)
    speak(response)
    play()
