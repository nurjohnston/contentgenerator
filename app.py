from flask import Flask, render_template, request, jsonify, send_from_directory
import urllib.request
import json
import os
import time
import urllib.parse

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

# Pre-computed prompts for quick buttons
QUICK_PROMPTS = [
    "Write a blog post about artificial intelligence and its impact on jobs",
    "Write a blog post about learning Python as a beginner",
    "Write a blog post about space exploration and Mars colonization",
    "Write a blog post about climate change solutions",
    "Write a blog post about mental health awareness"
]

# Pre-written answers for fallback (when API fails)
FALLBACK_ANSWERS = {
    0: """**AI and the Future of Work**

Artificial intelligence is transforming the workplace. While some jobs may be automated, AI is creating new opportunities in tech, data science, and human-AI collaboration. The key is adapting and learning new skills. Studies show that workers who embrace AI tools become more productive and valuable to employers. The future isn't about humans vs machines - it's about humans with machines.""",

    1: """**Why Python is Perfect for Beginners**

Python is the world's most popular programming language for beginners. Its simple, readable syntax feels like writing English. You can build a website, analyze data, or automate tasks within weeks of starting. With free resources like Codecademy and freeCodeCamp, anyone can learn Python regardless of background. The Python community is welcoming and supportive, making it the ideal first language.""",

    2: """**Mars: Humanity's Next Frontier**

Space exploration is entering an exciting era. NASA and SpaceX plan to send humans to Mars within the decade. The red planet offers scientists a chance to study planetary evolution and search for signs of ancient life. Colonizing Mars would ensure humanity's survival and drive technological innovation. While challenges remain - radiation, low gravity, and life support - the dream of becoming a multi-planetary species is closer than ever.""",

    3: """**Climate Change Solutions That Work**

Climate change is the defining challenge of our time. The good news? Solutions exist. Renewable energy like solar and wind is now cheaper than coal in most countries. Electric vehicles are becoming mainstream. Reforestation projects remove carbon from the atmosphere. Individuals can help by reducing meat consumption, using public transit, and voting for climate-conscious leaders. Every action matters.""",

    4: """**Mental Health Awareness Matters**

Mental health is just as important as physical health. Yet too many people suffer in silence due to stigma. Talking openly about anxiety, depression, and stress helps normalize these experiences. Simple practices like meditation, exercise, and connecting with others can dramatically improve wellbeing. If you're struggling, reach out to a friend, family member, or professional. You are not alone, and help is available."""
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
    """Generate image using Pollinations"""

    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true&width=512&height=512"

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

    # Try API first
    response = generate_text(prompt)

    # If API fails, return fallback data
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

    image_url = generate_image(prompt)
    return jsonify({'imageUrl': image_url})


if __name__ == '__main__':
    print("=" * 50)
    print("📝 Multi-Content Generator Starting...")
    print("=" * 50)
    print("\n📍 http://127.0.0.1:5000")
    print("📍 Text Generation: Gemini API (with fallback)")
    print("📍 Image Generation: Pollinations (or local static files)")
    print("📍 Static files served from: /static/")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5000)