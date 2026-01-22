import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# फाईल्स साठवण्यासाठी तात्पुरते फोल्डर सेट करणे
if os.name == 'nt':  # तुमच्या पीसीसाठी (Windows)
    DOWNLOAD_PATH = 'downloads/%(title)s.%(ext)s'
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
else:  # Render सर्व्हरसाठी (Linux)
    DOWNLOAD_PATH = '/tmp/%(title)s.%(ext)s'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return "कृपया वैध यूट्यूब लिंक टाका!", 400
    
    # कुकीज फाईलचा वापर करून बॉट एरर टाळणे
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': DOWNLOAD_PATH,
        'cookiefile': 'cookies.txt',  # ही ओळ सर्वात महत्त्वाची आहे
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # व्हिडिओ डाऊनलोड करणे
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # फाईल युजरला पाठवणे
            return send_file(file_path, as_attachment=True)
            
    except Exception as e:
        return f"एरर आली आहे: {str(e)}", 500

if __name__ == "__main__":
    # पोर्ट सेटिंग
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
