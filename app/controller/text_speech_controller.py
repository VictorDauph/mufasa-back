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