from pydub import AudioSegment
import torch

def is_stereo(path):
    try:
        audio = AudioSegment.from_file(path)
        channels = audio.channels
        return channels != 1
        
    except Exception as e:  
        print(f"Error checking if audio is stereo: {e}")
        return False
    
def clear_model(model):
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()       