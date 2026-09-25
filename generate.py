import os
import requests
import datetime
import pytz
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET

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

# 2. 1400x1400 Square Cover Art (Required for YouTube Music)
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

# 3. RSS 2.0 XML with iTunes tags
print("Writing compliant podcast.xml...")
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ET.register_namespace("itunes", ITUNES_NS)

rss = ET.Element("rss", version="2.0", attrib={"{http://www.w3.org/2000/xmlns/}itunes": ITUNES_NS})
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Skyler's Daily Morning Briefing"
ET.SubElement(channel, "link").text = BASE_URL
ET.SubElement(channel, "description").text = "Private executive briefing delivered by Alfred and the Cabinet."
ET.SubElement(channel, "language").text = "en-us"
ET.SubElement(channel, f"{{{ITUNES_NS}}}author").text = "Alfred"
ET.SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = "false"
ET.SubElement(channel, f"{{{ITUNES_NS}}}image", attrib={"href": f"{BASE_URL}/{cover_filename}"})

category = ET.SubElement(channel, f"{{{ITUNES_NS}}}category", attrib={"text": "News"})

image = ET.SubElement(channel, "image")
ET.SubElement(image, "url").text = f"{BASE_URL}/{cover_filename}"
ET.SubElement(image, "title").text = "Skyler's Daily Morning Briefing"
ET.SubElement(image, "link").text = BASE_URL

item = ET.SubElement(channel, "item")
ET.SubElement(item, "title").text = f"Briefing — {date_display}"
ET.SubElement(item, "description").text = briefing_text
ET.SubElement(item, "enclosure", attrib={
    "url": f"{BASE_URL}/{audio_filename}",
    "length": str(audio_size),
    "type": "audio/mpeg"
})
ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = f"briefing-{iso_date}"
ET.SubElement(item, "pubDate").text = now.strftime("%a, %d %b %Y %H:%M:%S %z")
ET.SubElement(item, f"{{{ITUNES_NS}}}duration").text = "60"
ET.SubElement(item, f"{{{ITUNES_NS}}}explicit").text = "false"
ET.SubElement(item, f"{{{ITUNES_NS}}}image", attrib={"href": f"{BASE_URL}/{cover_filename}"})

tree = ET.ElementTree(rss)
tree.write("podcast.xml", encoding="utf-8", xml_declaration=True)
print("podcast.xml written successfully.")
