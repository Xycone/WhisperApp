import whisper

from enums.modelSizes import ModelSizes
from enums.deviceTypes import DeviceTypes

class WhisperManager:
    # Initialiser
    def __init__(self, size: ModelSizes, device: DeviceTypes):
        try:
            self.__size = size
            self.__device = device
            self.__model = whisper.load_model(self.__size, self.__device)

        except Exception as e:
            raise RuntimeError(f"Error initializing WhisperManager: {e}")
    
    # Getters & Setters
    def get_size(self):
        return self.__size

    # Methods
    def transcribe(self, path):
        if self.__model is None:    
            raise RuntimeError("Model has not been loaded. Call load_model() first.")
        
        try:
            transcript = self.__model.transcribe(path)
            return transcript
        
        except FileNotFoundError as e:
            raise RuntimeError(f"Audio file not found: {e}")
        
        except Exception as e:
            raise RuntimeError(f"Error transcribing audio: {e}")