### app.py (with custom prompt support)

import os
import openai
import json
import base64
import tempfile
import subprocess
import traceback
import atexit
import functools
from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import summarize_to_bullets
from transformers import pipeline
import whisper
from dotenv import load_dotenv

# Auto-flushing prints
print = functools.partial(print, flush=True)

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load Whisper model once
print("🚀 Loading Whisper model at startup...")
WHISPER_MODEL = whisper.load_model("base")
print("✅ Whisper model loaded.")

# Load translation pipeline once
print("🚀 Loading HuggingFace translation model...")
TRANSLATOR = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
print("✅ Translation model loaded.")

# Store cookie temp file path globally
COOKIE_TEMP_PATH = None

def get_cookie_file_from_env():
    global COOKIE_TEMP_PATH
    cookies_b64 = os.environ.get('YOUTUBE_COOKIES_BASE64')
    if not cookies_b64:
        raise Exception("YOUTUBE_COOKIES_BASE64 environment variable not set")

    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'wb') as f:
        f.write(base64.b64decode(cookies_b64))
    COOKIE_TEMP_PATH = path
    print(f"✅ Cookies written to temp file: {path}")
    return path

def cleanup_temp_cookie():
    if COOKIE_TEMP_PATH and os.path.exists(COOKIE_TEMP_PATH):
        os.remove(COOKIE_TEMP_PATH)
        print(f"🧹 Temp cookie file {COOKIE_TEMP_PATH} deleted.")

atexit.register(cleanup_temp_cookie)

def download_audio(video_url, cookies_path):
    output_file = tempfile.mktemp(suffix='.webm')
    cmd = [
        'yt-dlp', '--cookies', cookies_path,
        '-f', 'bestaudio', '-o', output_file, video_url
    ]
    print(f"🎧 Running yt-dlp with: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"✅ Audio downloaded to: {output_file}")
    return output_file

def convert_audio_to_wav(input_path):
    output_path = tempfile.mktemp(suffix=".wav")
    cmd = ['ffmpeg', '-i', input_path, '-ar', '16000', '-ac', '1', output_path]
    print(f"🔄 Converting audio to WAV with ffmpeg: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"✅ Conversion complete: {output_path}")
    return output_path

def transcribe_with_whisper(audio_path):
    print("🎙️ Transcribing with Whisper...")
    result = WHISPER_MODEL.transcribe(audio_path)
    transcript = result["text"]
    detected_lang = result["language"]
    print(f"✅ Transcription complete. Detected language: {detected_lang}")
    print(transcript[:500])
    return transcript.strip(), detected_lang

def translate_to_english(text, chunk_size=400):
    print("🌐 Translating to English using OpenAI GPT...")
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    chunks = []
    current_chunk = ""
    for sentence in text.split(". "):
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())

    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"🔸 Translating chunk {idx + 1}/{len(chunks)}...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a translator that converts any language into natural English."},
                    {"role": "user", "content": f"Translate this to English:\n\n{chunk}"}
                ],
                max_tokens=5000,
                temperature=0.2,
            )
            translated = response.choices[0].message.content.strip()
            translated_chunks.append(translated)
        except Exception as e:
            print(f"❌ Error translating chunk {idx + 1}: {e}")
            translated_chunks.append("[Translation failed for this part]")

    result = " ".join(translated_chunks)
    print("✅ Full translation complete. Preview:")
    print(result[:500])
    return result

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_url = data.get('url')
    summary_mode = data.get('summary_mode', 'bullet')
    custom_prompt = data.get('custom_prompt', None)

    if not video_url:
        return jsonify({'error': 'Missing YouTube URL'}), 400

    try:
        print("🔄 Step 1: Getting cookies from env...")
        cookies_path = get_cookie_file_from_env()

        print("🔄 Step 2: Downloading audio...")
        audio_path = download_audio(video_url, cookies_path)

        print("🔄 Step 3: Converting to WAV...")
        wav_path = convert_audio_to_wav(audio_path)

        print("🔄 Step 4: Transcribing...")
        transcript, detected_lang = transcribe_with_whisper(wav_path)

        if detected_lang != 'en':
            print(f"🔄 Step 5: Detected language is '{detected_lang}'. Translating...")
            translated = translate_to_english(transcript)
        else:
            print("✅ Skipping as the transcribed content was already in english.")
            translated = transcript

        print("🔄 Step 6: Summarizing with mode:", summary_mode)
        bullets = summarize_to_bullets(translated, mode=summary_mode, custom_prompt=custom_prompt)

        return jsonify({
            'transcript': transcript,
            'translated': translated,
            'summary': bullets
        })

    except Exception as e:
        print("❌ Error during pipeline:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 15000)), debug=True)