from core.llm_chat import LLMChat

model_type = 'ocr11'

class LogicIdentifier:
    def __init__(self):        
        self.llm_chat = LLMChat()
        
    def merge_steps(self, concept_data):
        print("77777777")
        response = self.llm_chat.one_time_respond("who are you?")
        return response