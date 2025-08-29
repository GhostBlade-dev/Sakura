# schemas.py
from pydantic import BaseModel

class TTSRequest(BaseModel):
	text: str
	voice: str = "default"

class TTSResponse(BaseModel):
	audio_url: str

class UploadAudioResponse(BaseModel):
	filename: str
	url: str

class ErrorResponse(BaseModel):
	detail: str
