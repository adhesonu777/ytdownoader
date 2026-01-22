import os
import time
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# फाईल साठवण्यासाठी तात्पुरता पाथ
DOWNLOAD_FOLDER = '/tmp' if os.name != 'nt' else 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return "कृपया वैध यूट्यूब लिंक टाका!", 400
    
    # सर्वात सुरक्षित डाऊनलोड सेटिंग्ज
    ydl_opts = {
        'format': 'best',  # 'bestvideo+bestaudio' ऐवजी फक्त 'best' वापरा, यामुळे रिकामी फाईल येणार नाही
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s_%(timestamp)s.%(ext)s'),
        'cookiefile': 'cookies.txt',  # तुमची कुकीज फाईल
        'nocheckcertificate': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # फाईल खरंच तयार झाली आहे का आणि ती रिकामी नाही ना, याची खात्री करणे
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return send_file(file_path, as_attachment=True)
            else:
                return "सर््हरवर फाईल तयार होऊ शकली नाही, कृपया पुन्हा प्रयत्न करा.", 500
                
    except Exception as e:
        return f"एरर आली आहे: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
