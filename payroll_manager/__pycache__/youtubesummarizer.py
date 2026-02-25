import yt_dlp
import re

def extract_video_id(url):
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

url = input("Enter YouTube URL: ")

ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitlesformat': 'vtt',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    subtitles = info.get("subtitles") or info.get("automatic_captions")

    if not subtitles:
        print("❌ No subtitles available for this video.")
    else:
        lang = list(subtitles.keys())[0]
        subs = subtitles[lang][0]['url']

        import requests
        vtt = requests.get(subs).text

        print("\n📜 Transcript:\n")
        print(vtt)



