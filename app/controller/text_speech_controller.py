import json

from fastapi import HTTPException
import replicate
import httpx
from fastapi import UploadFile
from app.config import settings


def text_to_speech(text: str,ref_url: str):
    input = {
        "speaker": ref_url or "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav",
        "text":text,
        "language":"fr"
    }

    output = replicate.run(
        "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        input=input
    )
    print(output.url)
    return output.url

async def upload_reference(file: UploadFile) -> str:
    """
    Upload un fichier audio (wav/mp3) vers Replicate
    et retourne l'URL publique temporaire
    """
    try:
        async with httpx.AsyncClient() as client:

                # lire le contenu du fichier uploadé
                file_bytes = await file.read()
                print("Upload:", file.filename, len(file_bytes))

                # envoyer vers l'endpoint Replicate /files
                resp = await client.post(
                    "https://api.replicate.com/v1/files",
                    headers={"Authorization": f"Token {settings.replicate_api_token}"},
                    files={"content": (file.filename, file_bytes, file.content_type)}
                )

                resp.raise_for_status()
                data = resp.json()
                return data["urls"]["get"]
    except httpx.HTTPStatusError as e:
        # Erreur HTTP (ex: 400, 401, 500)
        return {"error from replicate API": f"HTTP {e.response.status_code}", "details": e.response.text}

    except httpx.RequestError as e:
        # Erreur réseau (ex: pas de connexion)
        return {"error from replicate API": "Request failed", "details": str(e)}

    except Exception as e:
        # Catch-all pour toute autre exception
        return {"error from replicate API": "Unexpected error", "details": str(e)}


import replicate


async def speak_to_text(audio_file_path: str) -> str:
    """
    Transcrit un fichier audio en texte via Whisper sur Replicate.

    :param audio_file_path: lien vers fichier audio (wav, mp3, etc.)
    :return: texte transcrit
    """
    try:
        # Chargement du modèle Whisper (base sur Replicate)
        model = 'openai/whisper:8099696689d249cf8b122d833c36ac3f75505c666a395ca40ef26f68e7d3d16e'

        # Exécution de la prédiction
        output = replicate.run(
            model,
            input={
                "audio": audio_file_path,  # fichier hébergé sur le web
                "language": "fr"  # facultatif : tu peux forcer la langue
            }
        )

        # L’output est une string avec la transcription
        return output["transcription"]

    except httpx.HTTPStatusError as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur HTTP pendant la transcription: {str(e)}"
        )

    except Exception as e:  # attrape TypeError, ValueError, etc.
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne pendant la transcription: {str(e)}"
        )

async def ask_llama(prompt: str,transcription:str):
    try:
        context_arr = json.loads(prompt)
        context_arr.append({"role":"user","content":transcription})
        prompt = json.dumps(context_arr)

        # Appel au modèle Replicate
        output = replicate.run(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": prompt,
                "max_tokens": 300,       # facultatif
                "temperature": 0.3       # un peu de créativité mais réponses stables
            }
        )

        # output peut être un générateur -> on concatène
        if isinstance(output, (list, tuple)):
            answer = "".join(output)
        else:
            answer = str(output)

        context_arr.append({"role":"system","content":answer})

        return {"context":context_arr, "answer":answer}



    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur Replicate: {e}")
