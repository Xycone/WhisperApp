import gc

from enums.deviceTypes import DeviceTypes
from langchain_community.llms import LlamaCpp

class LlamaCppManager:
    def __init__(self, model_path, device: DeviceTypes):
        llm_params = {
            "model_path": model_path,
            "temperature": 0,
            "max_tokens": 2000,
            "n_ctx": 8192
        }

        if device == "cuda":
            llm_params["n_gpu_layers"] = 33
            llm_params["n_batch"] = 512
            
        self.__llm = LlamaCpp(**llm_params)
    
    def audit_transcript(self, transcript):
        prompt = f"""
        <s>
        [INST]
        You are an auditor, your task is to audit the content in the conversation.
        Keep in mind that the speaker assignment is not always accurate and some segments might be misassigned.
        Go through the transcript verbatim without creating your own information and try to understand the intent of the speakers and their conversation:
        [/INST]
        {transcript}

        [INST]
        Audit the conversation according to the following criteria without changing anything.
        Keep in mind each item in the criteria checklist is independent of one another and does not have to appear in the transcript in any order:
        [/INST]
        1. Introduced themselves by name while stating that they are calling from IPPFA or IPP without disclosing any other insurer or company.
   
        2. Briefly shared about the types of services.

        3. Mention about a possibility of a meeting or Zoom session.
   
        4. Mentioned the name of the person or the source from whom they got the customer's contact details.

        [INST]
        For each item in the criteria checklist above, your response must follow the format:
        Provide the result as either a Pass or Fail and only quote the text from the transcript that best supports your evaluation as evidence, keep the quote short.
        [/INST]
        </s>
        """

        # Generate the audit result
        result = self.__llm(prompt)

        return result
    
    def unload_model(self):
        try:
            # Delete the model instance and trigger garbage collection
            del self.__llm
            gc.collect()

        except Exception as e:
            print(f"Error unloading model: {e}")     