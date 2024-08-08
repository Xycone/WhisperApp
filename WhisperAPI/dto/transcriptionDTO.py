from pydantic import BaseModel
from enums.modelSizes import ModelSizes
from enums.diarisationMethods import DiarisationMethods
from enums.transcriptionMethods import TranscriptionMethods

class TranscriptionDTO(BaseModel):
    model_size: ModelSizes
    transcription_method: TranscriptionMethods
    diarisation: bool
    diarisation_method: DiarisationMethods
    num_speakers: int
    audit: bool