import os
import requests
import datetime
import pytz
from PIL import Image, ImageDraw

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George
MODEL_ID = "eleven_turbo_v2_5"
USERNAME = "skyleramastro-cmd"
REPO = "morning-briefing"
BASE_URL = f"https://{USERNAME}.github.io/{REPO}"

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY environment variable.")

tz = pytz.timezone("America/New_York")
now = datetime.datetime.now(tz)
date_display = now.strftime("%A, %B %d, %Y")
iso_date = now.strftime("%Y-%m-%d")
pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")

briefing_text = f"""Good morning, sir. This is Alfred with your morning briefing for {date_display}. 

Your cabinet is operational and standing by. Tony has your training and nutrition targets calibrated, Pam has your calendar and student schedule organized to protect your midday focus, and Chewbacca is monitoring your fleet and workshop mechanicals.

The weather in St. Petersburg is favorable for outdoor work and active recreation. Have a disciplined and productive day, sir."""

print(f"Generating audio for {date_display}...")

# 1. ElevenLabs Speech Synthesis
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "text": briefing_text,
    "model_id": MODEL_ID,
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
}

response = requests.post(tts_url, json=payload, headers=headers)
if response.status_code != 200:
    raise RuntimeError(f"ElevenLabs API Error {response.status_code}: {response.text}")

audio_filename = "briefing_today.mp3"
with open(audio_filename, "wb") as f:
    f.write(response.content)

audio_size = os.path.getsize(audio_filename)

# 2. 1400x1400 Square Cover Art
print("Rendering 1400x1400 square cover art...")
img = Image.new("RGB", (1400, 1400), color=(15, 20, 26))
draw = ImageDraw.Draw(img)

draw.rectangle([(50, 50), (1350, 1350)], outline=(40, 52, 68), width=4)
draw.text((100, 120), "ALFRED EXECUTIVE BRIEFING", fill=(212, 175, 55))
draw.text((100, 180), date_display.upper(), fill=(240, 240, 240))
draw.line([(100, 260), (1300, 260)], fill=(60, 75, 95), width=2)

draw.text((100, 320), "CABINET STATUS:", fill=(100, 200, 255))
draw.text((130, 400), "• TONY (Training): Full Body Progression Active", fill=(210, 215, 220))
draw.text((130, 480), "• PAM (Operations): 21-hr Student Model Deconflicted", fill=(210, 215, 220))
draw.text((130, 560), "• CHEWBACCA (Fleet): Outboards & RV Systems Monitored", fill=(210, 215, 220))
draw.text((130, 640), "• HENRY (Projects): St. Pete Grotto & NC Build Tracked", fill=(210, 215, 220))
draw.text((130, 720), "• STERLING (Finance): Automated Portfolio Balanced", fill=(210, 215, 220))
draw.text((130, 800), "• REGINA (Media): Evening Wind-Down Briefing Scheduled", fill=(210, 215, 220))

cover_filename = "cover_today.jpg"
img.save(cover_filename, "JPEG", quality=90)

# 3. Clean, Compliant RSS 2.0 XML
print("Writing compliant podcast.xml...")
clean_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Skyler's Daily Morning Briefing</title>
    <link>{BASE_URL}</link>
    <description>Private executive briefing delivered by Alfred and the Cabinet.</description>
    <language>en-us</language>
    <itunes:author>Alfred</itunes:author>
    <itunes:summary>Private executive briefing delivered by Alfred and the Cabinet.</itunes:summary>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:category text="News"/>
    <itunes:image href="{BASE_URL}/{cover_filename}"/>
    <image>
      <url>{BASE_URL}/{cover_filename}</url>
      <title>Skyler's Daily Morning Briefing</title>
      <link>{BASE_URL}</link>
    </image>
    <item>
      <title>Briefing — {date_display}</title>
      <description>{briefing_text}</description>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{BASE_URL}/{audio_filename}" length="{audio_size}" type="audio/mpeg"/>
      <guid isPermaLink="false">briefing-{iso_date}</guid>
      <itunes:duration>60</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:image href="{BASE_URL}/{cover_filename}"/>
    </item>
  </channel>
</rss>"""

with open("podcast.xml", "w", encoding="utf-8") as f:
    f.write(clean_xml)

print("podcast.xml written cleanly.")
