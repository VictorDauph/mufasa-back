from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, Settings
from app.controller import text_speech_controller
from app.dto.SpeakInDto import SpeakInDto

app = FastAPI()

# Autoriser ton front à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://127.0.0.1:5500"] si tu veux être précis
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/speak")
async def speak(req: SpeakInDto):
    return {"audio_url":text_speech_controller.text_to_speech(req.text,req.ref_url)}

@app.post("/ref_upload")
async def ref_upload(file:UploadFile):
    return await text_speech_controller.upload_reference(file)