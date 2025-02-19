class KnowledgeGenerator:    
    def __init__(self, llm_chat):
        self.llm_chat = llm_chat

    def generate_knowledge_json(self, pattern_data):
        return {}

from core.llm_chat import LLMChat

model_type = 'ocr11'

class KnowledgeGenerator:
    def __init__(self, config):        
        self.llm_chat = LLMChat(config, model_type)
    
    def generate_knowledge_json(self, pattern_data):
        print("99999999")
        response = self.llm_chat.one_time_respond("who are you?")
        
        return response