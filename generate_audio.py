# save as generate_audio.py
from gtts import gTTS
import os

os.makedirs('static/audio', exist_ok=True)

texts = [
    "Nur is busy right about now",
    "Liverpool is not winning anything this season.",
    "My favourite car is a g-wagon.",
    "One two three four five six seven eight nine ten.",
    "Squat Bench and Deadlift."
]

for i, text in enumerate(texts):
    tts = gTTS(text, lang='en')
    tts.save(f'static/audio/audio_{i}.mp3')
    print(f"Generated audio_{i}.mp3")