import os
import requests
import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET

# Configuration
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George (British Gentleman)
MODEL_ID = "eleven_turbo_v2_5"
USERNAME = "skyleramastro-cmd"
REPO = "morning-briefing"
BASE_URL = f"https://{USERNAME}.github.io/{REPO}"

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY environment variable.")

# Get Today's Date in Eastern Time
tz = pytz.timezone("America/New_York")
now = datetime.datetime.now(tz)
date_display = now.strftime("%A, %B %d, %Y")
iso_date = now.strftime("%Y-%m-%d")

# 1. Compile Briefing Text
briefing_text = f"""Good morning, sir. This is Alfred with your morning briefing for {date_display}. 

Your cabinet is operational and standing by. Tony has your training and nutrition targets calibrated, Pam has your calendar and student schedule organized to protect your midday focus, and Chewbacca is monitoring your fleet and workshop mechanicals.

The weather in St. Petersburg is favorable for outdoor work and active recreation. Have a disciplined and productive day, sir."""

print(f"Generating audio for {date_display}...")

# 2. Call ElevenLabs TTS API
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "text": briefing_text,
    "model_id": MODEL_ID,
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(tts_url, json=payload, headers=headers)
if response.status_code != 200:
    raise RuntimeError(f"ElevenLabs API Error {response.status_code}: {response.text}")

audio_filename = "briefing_today.mp3"
with open(audio_filename, "wb") as f:
    f.write(response.content)

audio_size = os.path.getsize(audio_filename)
print(f"Audio generated successfully ({audio_size} bytes).")

# 3. Generate 1080p Visual Dashboard Cover Art
print("Rendering 1080p dashboard cover art...")
img = Image.new("RGB", (1920, 1080), color=(15, 20, 26))
draw = ImageDraw.Draw(img)

# Layout lines & typography
draw.rectangle([(60, 60), (1860, 1020)], outline=(40, 52, 68), width=3)
draw.text((120, 120), "ALFRED EXECUTIVE BRIEFING", fill=(212, 175, 55))
draw.text((120, 180), date_display.upper(), fill=(240, 240, 240))
draw.line([(120, 260), (1800, 260)], fill=(60, 75, 95), width=2)

draw.text((120, 320), "CABINET STATUS:", fill=(100, 200, 255))
draw.text((160, 390), "• TONY (Training & Nutrition): Active — Full Body Progression Active", fill=(210, 215, 220))
draw.text((160, 460), "• PAM (Operations): Student Time Zones Mapped (21-hr Target Model)", fill=(210, 215, 220))
draw.text((160, 530), "• CHEWBACCA (Engineering): Fleet Maintenance & Systems Monitored", fill=(210, 215, 220))
draw.text((160, 600), "• HENRY (Project Management): St. Pete Grotto & NC Warehouse Tracked", fill=(210, 215, 220))
draw.text((160, 670), "• STERLING (Finance): Automated Investments & Portfolio Balanced", fill=(210, 215, 220))
draw.text((160, 740), "• REGINA (Social Media): Evening Wind-Down Briefing Scheduled", fill=(210, 215, 220))

cover_filename = "cover_today.jpg"
img.save(cover_filename, "JPEG", quality=90)
print("Cover art saved.")

# 4. Generate RSS 2.0 Podcast XML Feed
print("Updating podcast.xml feed...")
rss = ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Skyler's Daily Morning Briefing"
ET.SubElement(channel, "link").text = BASE_URL
ET.SubElement(channel, "description").text = "Private executive briefing delivered by Alfred and the Cabinet."
ET.SubElement(channel, "language").text = "en-us"

image = ET.SubElement(channel, "image")
ET.SubElement(image, "url").text = f"{BASE_URL}/{cover_filename}"
ET.SubElement(image, "title").text = "Skyler's Daily Morning Briefing"
ET.SubElement(image, "link").text = BASE_URL

item = ET.SubElement(channel, "item")
ET.SubElement(item, "title").text = f"Briefing — {date_display}"
ET.SubElement(item, "description").text = briefing_text
ET.SubElement(item, "enclosure", url=f"{BASE_URL}/{audio_filename}?v={iso_date}", length=str(audio_size), type="audio/mpeg")
ET.SubElement(item, "guid").text = f"alfred-briefing-{iso_date}"
ET.SubElement(item, "pubDate").text = now.strftime("%a, %d %b %Y %H:%M:%S %z")

tree = ET.ElementTree(rss)
tree.write("podcast.xml", encoding="utf-8", xml_declaration=True)
print("podcast.xml updated successfully.")
