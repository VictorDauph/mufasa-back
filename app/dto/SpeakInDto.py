from pydantic import BaseModel


class SpeakInDto(BaseModel):
    text: str
    ref_url: str
