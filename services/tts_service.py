# tts_service.py

import requests
from gtts import gTTS
import os
import uuid

class MurfTTSService:
	def __init__(self, api_key: str):
		self.api_key = api_key
		self.base_url = "https://api.murf.ai/v1/speech/generate"

	def synthesize(self, text: str, voice: str = "default") -> str:
		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}
		payload = {
			"text": text,
			"voice": voice
		}
		try:
			response = requests.post(self.base_url, json=payload, headers=headers)
			response.raise_for_status()
			data = response.json()
			# Assume the API returns a URL to the audio file
			return data.get("audio_url", "")
		except Exception as e:
			print(f"MurfTTSService error: {e}")
			return ""


class GTTSService:
	def __init__(self, upload_dir: str = "uploads"):
		self.upload_dir = upload_dir

	def synthesize(self, text: str, lang: str = "en") -> str:
		try:
			tts = gTTS(text=text, lang=lang)
			filename = f"gtts_{uuid.uuid4().hex}.mp3"
			filepath = os.path.join(self.upload_dir, filename)
			tts.save(filepath)
			return filepath
		except Exception as e:
			print(f"GTTSService error: {e}")
			return ""
