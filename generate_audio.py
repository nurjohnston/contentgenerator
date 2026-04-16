# save as generate_audio.py
from gtts import gTTS
import os

os.makedirs('static/audio', exist_ok=True)

texts = [
    "Artificial intelligence is transforming the workplace, creating new opportunities in tech and data science.",
    "Python is the world's most popular programming language for beginners, with simple readable syntax.",
    "Space exploration is entering an exciting era, with plans to send humans to Mars within the decade.",
    "Climate change solutions exist, from renewable energy to electric vehicles and reforestation.",
    "Mental health awareness matters. Talking openly about anxiety and depression helps normalize these experiences."
]

for i, text in enumerate(texts):
    tts = gTTS(text, lang='en')
    tts.save(f'static/audio/audio_{i}.mp3')
    print(f"Generated audio_{i}.mp3")