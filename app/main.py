from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
import requests
import os
from app.config import settings

app = FastAPI()

@app.get("/")
async def test():
    return settings.replicate_api_token

@app.post("/speak")
async def speak(text: str = Form(...), reference: UploadFile = None):
    """
    Reçoit du texte + fichier audio de référence
    → Envoie au modèle XTTS sur Replicate
    → Retourne l'audio généré
    """

    # Sauvegarde temporaire du fichier de référence si fourni
    ref_path = None
    if reference:
        ref_path = f"/tmp/{reference.filename}"
        with open(ref_path, "wb") as f:
            f.write(await reference.read())

    # Préparer payload pour Replicate
    headers = {"Authorization": f"Token {settings.replicate_api_token}"}
    payload = {
        "version": "f631e1c4e1b2cd79c8e19ee1322c76f777bdc3ff9ed1e2b706ac39ff3e69059c",  # modèle XTTS-v2
        "input": {
            "text": text,
            "speaker": "fr",  # langue
            "speakerfile": open(ref_path, "rb") if ref_path else None
        }
    }

    response = requests.post(REPLICATE_API_URL, headers=headers, files=None, json=payload)
    if response.status_code != 201:
        return {"error": response.json()}

    prediction = response.json()
    audio_url = prediction["urls"]["get"]

    # Télécharger le résultat audio depuis Replicate
    result = requests.get(audio_url, headers=headers)
    audio = result.json()

    # Le résultat final est un lien HTTP -> récupérer l'audio
    output_url = audio["output"][0]
    audio_resp = requests.get(output_url, stream=True)

    return StreamingResponse(audio_resp.raw, media_type="audio/wav")
