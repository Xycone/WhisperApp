import whisperx

from enums.deviceTypes import DeviceTypes
from enums.modelSizes import ModelSizes

WHISPERX_MODELS = {
    "base": "/app/models/faster-whisper-base",
    "small": "/app/models/faster-whisper-small",
    "medium": "/app/models/faster-whisper-medium",
    "large": "/app/models/faster-whisper-large-v2"
}

class WhisperXManager:
    # Initialiser
    def __init__(self, size: ModelSizes, device: DeviceTypes, batch_size, compute_type):
        try:
            self.__size = size
            self.__device = device
            self.__batch_size = batch_size
            self.__compute_type = compute_type
            self.__audio = None
            self.__model = whisperx.load_model(WHISPERX_MODELS.get(self.__size), self.__device, compute_type=self.__compute_type)

        except Exception as e:
            raise RuntimeError(f"Error initializing WhisperXManager: {e}")
    
    # Getters & Setters
    def get_audio(self):
        return self.__audio
    
    def get_size(self):
        return self.__size
        
    # Methods
    def transcribe(self, path):
        if self.__model is None:    
            raise RuntimeError("Model has not been loaded. Call load_model() first.")

        try:
            self.__audio = whisperx.load_audio(path)
            transcript = self.__model.transcribe(self.__audio, batch_size=self.__batch_size)

            # Align output
            model_a, metadata = whisperx.load_align_model(language_code=transcript["language"], device=self.__device)
            transcript["segments"] = whisperx.align(transcript["segments"], model_a, metadata, self.__audio, self.__device, return_char_alignments=False)["segments"]

            return transcript
            
        except FileNotFoundError as e:
            raise RuntimeError(f"Audio file not found: {e}")
        
        except Exception as e:
            raise RuntimeError(f"Error transcribing audio: {e}")