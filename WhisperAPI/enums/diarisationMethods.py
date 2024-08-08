from enum import Enum

class DiarisationMethods(str, Enum):
    clustering = "clustering"
    whisperX_pipeline = "whisperX_pipeline"