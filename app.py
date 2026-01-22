import os
import uuid
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url", "").strip()

    if not url:
        return "कृपया वैध YouTube लिंक टाका!", 400

    if "youtube.com" not in url and "youtu.be" not in url:
        return "फक्त YouTube link allowed आहे!", 400

    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

    ydl_opts = {
        "format": "18/best[ext=mp4]/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,

        # ✅ BOT PROTECTION FIX
        "cookiesfrombrowser": ("chrome",),  # Local PC साठी

        # ✅ Cloud fallback
        "cookiefile": "cookies.txt",

        # ✅ Extra safety
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return "Download failed. पुन्हा प्रयत्न करा.", 500

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
        )

        # ✅ Auto cleanup
        @response.call_on_close
        def cleanup():
            try:
                os.remove(file_path)
            except Exception:
                pass

        return response

    except yt_dlp.utils.DownloadError:
        return (
            "YouTube bot / login error. "
            "Cookies update करा आणि पुन्हा try करा.",
            500,
        )

    except Exception as e:
        return f"Server error: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
