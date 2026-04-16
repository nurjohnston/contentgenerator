from flask import Flask, render_template, request, jsonify, send_from_directory
import urllib.request
import json
import os
import time
import urllib.parse
from gtts import gTTS
import uuid

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load Gemini API key
API_KEY = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                API_KEY = line.strip().split('=')[1]
                print("✓ Loaded Gemini API key")
                break
except FileNotFoundError:
    pass

if not API_KEY:
    API_KEY = input("Paste your Gemini API key: ")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

# Load Pollinations API key
POLLINATIONS_API_KEY = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('POLLINATIONS_API_KEY='):
                POLLINATIONS_API_KEY = line.strip().split('=')[1]
                print("✓ Loaded Pollinations API key")
                break
except FileNotFoundError:
    pass

if not POLLINATIONS_API_KEY:
    print("⚠️ No Pollinations API key found. Image generation will not work.")
    print("Get your free key from: https://pollinations.ai")

# Pre-computed prompts for quick buttons
QUICK_PROMPTS = [
    "Write a blog post about the legendary VW 1.9 TDI engine reliability",
    "Write a blog post comparing VW 1.9 TDI vs 2.0 TDI engines",
    "Write a blog post about common problems and fixes for the VW 2.0 TDI",
    "Write a blog post about tuning and performance upgrades for TDI engines",
    "Write a blog post about the history of VW TDI diesel engines"
]

# Pre-written answers for fallback (when API fails)
FALLBACK_ANSWERS = {
    0: """**The Legendary VW 1.9 TDI - Why It's Unkillable**

The VW 1.9 TDI engine, particularly the ALH and PD versions, is legendary for its reliability. Many owners report exceeding 300,000 miles with basic maintenance. The mechanical injection pump on earlier models is simple and robust. The ALH engine (1998-2003) is considered the most reliable, while the PD (2004-2006) offers more power but with camshaft wear concerns. These engines routinely outlast the cars they're in and have a cult following worldwide.""",

    1: """**1.9 TDI vs 2.0 TDI - Which One is Better?**

The 1.9 TDI is simpler, more reliable, and easier to work on. It lacks a DPF and has fewer emissions components that fail. The 2.0 TDI (common rail, 2008+) offers more power, smoother operation, and better fuel economy. However, the 2.0 TDI has known issues: failed DPF, clogged intake manifolds, failed EGR coolers, and dual-mass flywheel failures. For a daily driver, the 2.0 TDI is fine. For longevity and DIY maintenance, the 1.9 TDI wins.""",

    2: """**Common 2.0 TDI Problems and Fixes**

The 2.0 TDI has several common issues: DPF clogging (solution: regular highway driving or delete), failed EGR valve (solution: clean or delete), failed dual-mass flywheel (solution: replace with solid flywheel), camshaft wear (use correct oil), and failed heater core (flush system). The good news is most problems have known fixes. The CP4 fuel pump is also a weak point - consider upgrading to a CP3 pump for reliability.""",

    3: """**Tuning Your TDI - Power Upgrades That Work**

A simple tune (remap) on a 1.9 TDI ALH can take it from 90hp to 130hp with no hardware changes. Add bigger nozzles for 150hp. A VNT17 turbo plus tune can reach 170-180hp. For the 2.0 TDI, a stage 1 tune adds 30-40hp. Stage 2 with downpipe adds another 20hp. Keep EGTs in check and always monitor boost. A clutch upgrade is recommended above 300lb-ft torque. These engines respond incredibly well to tuning.""",

    4: """**The History of VW TDI Engines**

VW introduced TDI (Turbo Direct Injection) in 1989. The 1.9 TDI came in several versions: VE (1996-2003) with mechanical injection pump, PD (2004-2006) with unit injectors, and then the 2.0 TDI common rail (2008+). The 1.9 ALH is the most beloved. Dieselgate (2015) hurt VW's diesel reputation, but the TDI community remains strong. These engines are known for torque, fuel efficiency (40-50mpg), and longevity when properly maintained."""
}


def generate_text(prompt):
    """Generate text using Gemini API"""

    data = {
        "contents": [{"parts": [
            {"text": f"Write a 80-100 word blog post about: {prompt}. Use an engaging title and short paragraphs."}]}],
        "generationConfig": {
            "maxOutputTokens": 200,
            "temperature": 0.7
        }
    }

    json_data = json.dumps(data).encode('utf-8')
    request = urllib.request.Request(GEMINI_URL, data=json_data, method='POST')
    request.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"API error: {e}")
        return None


def generate_image(prompt):
    """Generate image using Pollinations API with key from .env"""

    if not POLLINATIONS_API_KEY:
        # Fallback to static images if no API key
        import random
        static_images = [
            "/static/images/image_0.jpg",
            "/static/images/image_1.jpg",
            "/static/images/image_2.jpg",
            "/static/images/image_3.jpg",
            "/static/images/image_4.jpg"
        ]
        return random.choice(static_images)

    # Encode the prompt for URL (spaces become %20, etc.)
    encoded_prompt = urllib.parse.quote(prompt)

    # Build the URL with the API key from .env file
    # Format: https://gen.pollinations.ai/image/{PROMPT}?key=YOUR_KEY&model=flux
    image_url = f"https://gen.pollinations.ai/image/{encoded_prompt}?key={POLLINATIONS_API_KEY}&model=flux&width=512&height=512"

    return image_url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/generate/text', methods=['POST'])
def generate_text_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = generate_text(prompt)

    if response is None:
        return jsonify({
            'fallback': True,
            'quickPrompts': QUICK_PROMPTS,
            'fallbackAnswers': FALLBACK_ANSWERS
        })

    return jsonify({'response': response, 'fallback': False})


@app.route('/generate/image', methods=['POST'])
def generate_image_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Generate the image URL using the key from .env
    image_url = generate_image(prompt)

    # Return the URL - the browser will fetch the image directly
    return jsonify({'imageUrl': image_url})


@app.route('/generate/audio', methods=['POST'])
def generate_audio_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        os.makedirs('static/audio', exist_ok=True)
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join('static', 'audio', filename)

        tts = gTTS(prompt, lang='en')
        tts.save(filepath)

        audio_url = f"/static/audio/{filename}"
        return jsonify({'audioUrl': audio_url})

    except Exception as e:
        print(f"Audio generation error: {e}")
        return jsonify({
            'fallback': True,
            'message': 'Audio generation failed. Please use the pre-generated prompts above.'
        })


if __name__ == '__main__':
    print("=" * 50)
    print("📝 Multi-Content Generator Starting...")
    print("=" * 50)
    print("\n📍 http://127.0.0.1:5000")
    print("📍 Text Generation: Gemini API (with fallback)")
    print("📍 Image Generation: Pollinations (with API key from .env)")
    print("📍 Audio Generation: gTTS (Text-to-Speech)")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5000)