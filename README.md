This was just a personal project trying a multi-modal generator powered by AI. It does 
text, images, and audio through a Flask web interface, and all three have fallback knowledge built 
in. Text generation uses the Gemini API (falls back to hardcoded VW TDI blog posts), image generation 
uses Pollinations API (falls back to pre-generated local images), and audio generation uses gTTS 
(falls back to pre-generated local audio files). No API keys are exposed — you need to add your own 
Gemini and Pollinations keys to a .env file that the Python script reads.


To run it:

git clone https://github.com/NurJohnston/ContentGenerator.git

cd ContentGenerator

pip install -r requirements.txt

python app.py
