import torch
import gc

from manager.clusteringManager import ClusteringManager
from manager.diarisationPipelineManager import DiarisationPipelineManager
from manager.whisperManager import WhisperManager
from manager.whisperXManager import WhisperXManager

from enums.deviceTypes import DeviceTypes
from enums.modelSizes import ModelSizes

class ModelLoader():
    def __init__(self, size: ModelSizes, device: DeviceTypes, batch_size, compute_type):
        self.__loaded_models = {}
        self.load_whisperx(size, device, batch_size, compute_type)

    def load_whisperx(self, size: ModelSizes, device: DeviceTypes, batch_size, compute_type):
        model_key = "WhisperX"

        if model_key not in self.__loaded_models or self.__loaded_models[model_key].get_size() != size:
            self.del_models(model_key)
            self.__loaded_models[model_key] = WhisperXManager(size, device, batch_size, compute_type)

        return self.__loaded_models.get(model_key)  

    def load_whisper(self, size: ModelSizes, device: DeviceTypes):
        model_key = "Whisper"

        if model_key not in self.__loaded_models or self.__loaded_models[model_key].get_size() != size:
            self.del_models(model_key)
            self.__loaded_models[model_key] = WhisperManager(size, device)

        return self.__loaded_models.get(model_key) 
        
    def load_clustering(self, device: DeviceTypes):
        model_key = "Clustering"

        if model_key not in self.__loaded_models:
            self.__loaded_models[model_key] = ClusteringManager(device)

        return self.__loaded_models.get(model_key)
        
    def load_dirisationPipeline(self, device: DeviceTypes, auth_token):
        model_key = "Diarisation Pipeline"
        
        if model_key not in self.__loaded_models:
            self.__loaded_models[model_key] = DiarisationPipelineManager(device, auth_token)

        return self.__loaded_models.get(model_key)
    
    def get_model(self, model_key):
        return self.__loaded_models.get(model_key)
    
    def get_all_models(self):
        return self.__loaded_models

    def del_models(self, *model_keys):
        for key in model_keys:
            if key in self.__loaded_models:
                del self.__loaded_models[key]
        self.__free_memory()

    def del_all_models(self):
        self.__loaded_models.clear()
        self.__free_memory()

        return self

    def __free_memory(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return self