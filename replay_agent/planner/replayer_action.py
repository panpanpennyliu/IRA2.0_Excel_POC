
import json, re

from core.llm_chat import LLMChat
from core.step_manager import Step

from prompt.action_generator import PURPOSE
from utils.logger_setup_data_extraction import logger

class ReplayerAction:

    def __init__(self, llm_chat):
        self.steps = []
        self.chat = llm_chat

    def get_action(self, analysis_request, propose, knowledge_base):
        content = ""
        content += analysis_request
        content += propose
        # content += f"<screen_concept>\n{screen_concept}\n</screen_concept>\n"
        content += knowledge_base
        
        logger.info("messages_str:"+ content)
        # print(content)

        # model_name = "gpt-4o-mini gemini-2.0-flash gemini-2.0-pro-exp-02-05 claude-3-5-sonnet gpt-4.5-preview  deepseek-chat gpt-4-vision-preview"
        model_name = "gpt-4o"
        logger.info("******************model name:"+ model_name)

        response = self.chat.prompt_respond(content, model_name)
        # response = self.chat.image_respond(screen_concept, content, model_name)
        # logger.info(f"Replayer Action response:\n {response}")
    
        return response
    
    def get_position_gemini(self, image_path, get_position):
        content = ""
        content += get_position
        model_name = "gemini-2.0-pro-exp-02-05"
        logger.info("******model name:"+ model_name)
        response = self.chat.image_respond_gemini(image_path, content, model_name)
        logger.info(f"Replayer Action response:\n {response}")
        return response
    
    

   


    
