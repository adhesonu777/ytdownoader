import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return "कृपया वैध यूट्यूब लिंक टाका!", 400
    
    # Render वर डाऊनलोडसाठी /tmp/ फोल्डर वापरणे अनिवार्य आहे
    download_path = '/tmp/%(title)s.%(ext)s'
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': download_path,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"एरर आली आहे: {str(e)}", 500

if __name__ == "__main__":
    # Render साठी आवश्यक पोर्ट सेटिंग
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)