from enum import Enum

class TranscriptionMethods(str, Enum):
    whisper = "whisper"
    whisperX = "whisperX"