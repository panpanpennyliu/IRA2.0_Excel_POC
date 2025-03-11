from utils.logger_setup_data_extraction import logger
from prompt.generate_knowledge_json import *
from core.llm_chat import LLMChat

class KnowledgeGenerator:
    def __init__(self):        
        self.chat = LLMChat()
    
    def generate_knowledge_json(self, data):
        context_manager_frames = data
        context_response = self.chat.context_respond_default(context_manager_frames.context_to_str(), GENERATE_BUSINESS_FLOW_REQUEST)
        context = context_response['answer'].replace("```json", '').replace("```", '')
        logger.info(f"response answer for compile concept json:\n {context}")
        logger.info("=========FFFFFF===============")

        context_manager_frames.add_context(context)
        context_manager_frames.print_context()

        context_response = self.chat.context_respond_default(context_manager_frames.context_to_str(), COMPILE_KNOWLEDGE_JSON_REQUEST)
        context = context_response['answer'].replace("```json", '').replace("```", '')
        logger.info(f"response answer for compile knowledge json:\n {context}")
        logger.info("=========GGGGGG===============")

        
        return context