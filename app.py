from flask import Flask, render_template, request, jsonify
import urllib.request
import json
import os
import time

app = Flask(__name__)

# Load Gemini API key from .env file
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

# Gemini URL for text generation
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"


def generate_text(prompt, content_type):
    """Generate text content using Gemini"""

    system_prompt = f"""You are a professional content creator. Generate {content_type} content based on the user's request.

Requirements:
- Use clear structure (headings, paragraphs, bullet points where appropriate)
- Be engaging and professional
- Match the tone to the content type
- Return ONLY the content, no explanations

Content types:
- blog: 300-500 words with headings
- email: Professional, concise, proper greeting and closing
- code: Working code with comments
- social: Short, engaging with relevant hashtags
"""

    full_prompt = f"{system_prompt}\n\nUser request: {prompt}"

    data = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 2000,
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
        return f"Error generating text: {str(e)}"


def generate_image(prompt):
    """Generate image using Pollinations (free, no API key)"""

    # Encode the prompt for URL
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    # Pollinations returns the image directly at this URL
    # We'll just return the URL for the frontend to display
    return image_url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate/text', methods=['POST'])
def generate_text_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    content_type = data.get('contentType', 'blog')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = generate_text(prompt, content_type)
    return jsonify({'response': response})


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
    print("📍 Text Generation: Gemini API")
    print("📍 Image Generation: Pollinations (free)")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5000)