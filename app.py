from flask import Flask, render_template, request, send_from_directory, jsonify
from gtts import gTTS
import yt_dlp
import os
import time
import requests
from moviepy.editor import ImageClip, AudioFileClip

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

# --- टूल 1: Text to Speech ---
@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    filename = f"speech_{int(time.time())}.mp3"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    try:
        tts = gTTS(text=text, lang='hi')
        tts.save(filepath)
        return jsonify({"file_url": f"/get-file/{filename}", "type": "audio"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- टूल 2: Universal Downloader ---
@app.route('/download-video', methods=['POST'])
def download_video():
    data = request.json
    url, media_type = data.get('url'), data.get('type')
    filename_base = f"dl_{int(time.time())}"
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/{filename_base}.%(ext)s',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    if media_type == 'mp3':
        ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
            if media_type == 'mp3': filename = filename.rsplit('.', 1)[0] + ".mp3"
            return jsonify({"file_url": f"/get-file/{filename}", "type": "video" if media_type == 'video' else "audio"})
    except Exception as e:
        return jsonify({"error": "Download Error: Check Link or yt-dlp update"}), 500

# --- टूल 3: AI Video Creator (Prompt to Video) ---
@app.route('/create-ai-video', methods=['POST'])
def ai_video():
    data = request.json
    prompt = data.get('prompt')
    filename_base = f"ai_{int(time.time())}"
    
    try:
        # 1. Audio
        audio_path = os.path.join(DOWNLOAD_FOLDER, f"{filename_base}.mp3")
        gTTS(text=prompt, lang='hi').save(audio_path)
        
        # 2. AI Image (Pollinations API)
        img_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
        img_path = os.path.join(DOWNLOAD_FOLDER, f"{filename_base}.jpg")
        with open(img_path, 'wb') as f: f.write(requests.get(img_url).content)
        
        # 3. Combine to Video
        video_path = os.path.join(DOWNLOAD_FOLDER, f"{filename_base}.mp4")
        a_clip = AudioFileClip(audio_path)
        v_clip = ImageClip(img_path).set_duration(a_clip.duration)
        v_clip.set_audio(a_clip).write_videofile(video_path, fps=24, codec="libx264")
        
        return jsonify({"file_url": f"/get-file/{filename_base}.mp4", "type": "video"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
