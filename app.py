import os
import uuid
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# Render सर्व्हरसाठी सुरक्षित पाथ
DOWNLOAD_FOLDER = '/tmp'
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
    
    unique_id = str(uuid.uuid4())
    # '18' हा फॉरमॅट ३६०प mp4 साठी असतो, जो सहज डाऊनलोड होतो
    ydl_opts = {
        'format': '18/best[ext=mp4]/best', 
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.%(ext)s'),
        'cookiefile': 'cookies.txt', # तुमची कुकीज फाईल
        'nocheckcertificate': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return send_file(file_path, as_attachment=True)
            else:
                return "सर्व्हरवर फाईल पूर्णपणे तयार झाली नाही. पुन्हा प्रयत्न करा.", 500
                
    except Exception as e:
        return f"एरर आली आहे: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
