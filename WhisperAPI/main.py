from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware

import torch

from typing import List
from utils import *

from manager.modelLoader import ModelLoader
from manager.llamacppManager import LlamaCppManager

from dto.transcriptionDTO import TranscriptionDTO
from tempfile import NamedTemporaryFile

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE, COMPUTE_TYPE = ("cuda", "float16") if torch.cuda.is_available() else ("cpu", "int8")
model_loader = ModelLoader("large", DEVICE, 16, COMPUTE_TYPE)

@app.post("/transcribe-files")
async def transcribe_files(form_data: TranscriptionDTO = Depends(), files: List[UploadFile] = File(...)):
    # 1. Error check
    if not files:
        raise HTTPException(status_code=400, detail="No Files Uploaded")
    
    if form_data.diarisation and form_data.transcription_method == "whisper" and form_data.diarisation_method == "whisperX_pipeline":
        raise HTTPException(status_code=400, detail="whisperX diarisation pipeline cannot be used with the whisper model. Please use a different transcription and diarisation configuration")
    

    response = {}

    # 2. Load models used for transcription & diarisation onto device
    model_loader.del_models("WhisperX" if form_data.transcription_method == "whisper" else "Whisper")

    transcription_manager = (
        model_loader.load_whisper(form_data.model_size, DEVICE)
        if form_data.transcription_method == "whisper"
        else model_loader.load_whisperx(form_data.model_size, DEVICE, 16, COMPUTE_TYPE)
    )

    if form_data.diarisation:
        model_loader.del_models("Diarisation Pipeline" if form_data.diarisation_method == "clustering" else "Clustering")
        diarisation_manager = (
            model_loader.load_clustering(DEVICE)
            if form_data.diarisation_method == "clustering"
            else model_loader.load_dirisationPipeline(DEVICE, "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")
        )
    else:
        model_loader.del_models("Diarisation Pipeline", "Clustering")

    # 3. Transcribe & diarise all audio files
    for id, file in enumerate(files, start=1):
        with NamedTemporaryFile(delete=True) as temp:
            try:
                # Copies uploaded audio file to the temporary file
                with open(temp.name, 'wb') as temp_file:
                    temp_file.write(file.file.read())

                if form_data.diarisation and is_stereo(temp.name):
                    raise HTTPException(status_code=400, detail="Diarisation cannot be performed on stereo audio.")     

                # Performs audio transcription & diarisation
                transcript = transcription_manager.transcribe(temp.name)

                if form_data.diarisation and form_data.diarisation_method == "clustering":
                    segments = diarisation_manager.diarise(temp.name, transcript["segments"], form_data.num_speakers)
                    
                elif form_data.diarisation and form_data.diarisation_method == "whisperX_pipeline":
                    segments = diarisation_manager.diarise(transcription_manager.get_audio(), transcript, form_data.num_speakers)

                else:
                    segments = transcript["segments"]
                    
                response[id] = {
                    "filename": file.filename,
                    "language": transcript["language"],
                    "segments": [
                        {
                            "start": segment.get("start"),
                            "end": segment.get("end"),
                            "text": segment.get("text"),
                            "speaker": segment.get("speaker")
                        }
                        for segment in segments
                    ]
                }
            
            except Exception as e:
                response[id] = {
                    "filename": file.filename,
                    "error": str(e)
                }
    
    if form_data.audit:
        # 4. Unload models used for transcription & diarisation and load in the LLM used for auditing
        model_loader.del_all_models()
        llama_cpp_manager = model_loader.load_llm(DEVICE)

        # 5. Audit transcript of all audio files
        for index, file_data in response.items():
            try:
                formatted_transcript = "\n".join(
                    f"{segment.get('speaker')}: {segment.get('text')}"
                    for segment in file_data["segments"]
                    )
                
                response[index]['result'] = llama_cpp_manager.audit_transcript(formatted_transcript, form_data.criteria)

            except Exception as e:
                response[index]['result'] = {
                    "error": str(e)
                }

        # 6. Unload LLM used for auditing and load models used for transcription & diarisation
        model_loader.del_models("LLM")

    return response


@app.get("/get-device")
async def get_device():
    return DEVICE