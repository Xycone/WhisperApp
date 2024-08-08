import subprocess

import numpy as np
# Monkey-patch numpy to add NAN attribute
np.NAN = np.nan

from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment

import wave
import contextlib

from sklearn.cluster import AgglomerativeClustering

from enums.deviceTypes import DeviceTypes

class ClusteringManager:
    # Initialiser
    def __init__(self, device: DeviceTypes):
        try:
            self.__embedding_model = PretrainedSpeakerEmbedding(
            "speechbrain/spkrec-ecapa-voxceleb",
            device=device
            )

        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

    # Methods
    def diarise(self, path, segments, num_speakers):
        try:
            if path[-3:] != 'wav':
                path = self.__convert_audio(path)

        except Exception as e:
            print(f"Error converting audio: {e}")
            return False       
        
        # Generate speaker embeddings for each segment in segments
        try:
            embeddings = np.zeros(shape=(len(segments), 192))
            for i, segment in enumerate(segments):
                embeddings[i] = self.__segment_embedding(path, self.__calc_audio_duration(path), segment)

            embeddings = np.nan_to_num(embeddings)

            # Assign speaker to each of the segments
            for i in range(len(segments)):
                segments[i]["speaker"] = "SPEAKER_" +  f'{self.__cluster_segments(num_speakers, embeddings)[i]:02d}'

            return segments
        
        except Exception as e:
            print(f"Error diarising audio: {e}")
            return False
    
    # Internal methods (can be accessed outside of class but not recommended)
    def __convert_audio(self, path):
        try:
            new_path = "converted.wav"
            subprocess.run(["ffmpeg", "-i", path, new_path, "-y"], check=True)

            return new_path
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error converting audio with ffmpeg: {e}")

    def __calc_audio_duration(self, path):
        try:
            with contextlib.closing(wave.open(path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)

            return duration
        
        except wave.Error as e:
            raise RuntimeError(f"Error calculating audio duration: {e}")
    
    def __segment_embedding(self, path, duration, segment):
        try:
            audio = Audio()
            start = segment["start"]
            end = min(duration, segment["end"])
            clip = Segment(start, end)
            waveform, sample_rate = audio.crop(path, clip)

            return self.__embedding_model(waveform[None])
        
        except Exception as e:
            raise RuntimeError(f"Error generating segment embedding: {e}")

    def __cluster_segments(self, num_speakers, embeddings):
        try:
            clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
            labels = clustering.labels_

            return labels
        
        except Exception as e:
            raise RuntimeError(f"Error clustering segments: {e}")