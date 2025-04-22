
import json, re

from core.llm_chat import LLMChat
from core.step_manager import Step

from prompt.action_generator import PURPOSE
from utils.logger.logger_setup_data_extraction import logger
from utils.json.json_processor import json_process

class ReplayerAction:

    def __init__(self, llm_chat):
        self.steps = []
        self.chat = llm_chat

    
    def get_respond_prompt(self, *prompts):

        content = '\n'.join(map(str, prompts))
        # logger.info("messages_str:"+ content)
        # model_name = "gpt-4o-mini gemini-2.0-flash gemini-2.0-pro-exp-02-05 claude-3-5-sonnet gpt-4.5-preview  deepseek-chat gpt-4-vision-preview"
        
        model_name = "gemini-1.5-pro"

        logger.info("******model name:"+ model_name)
        response = self.chat.prompt_respond(content, model_name)
        response_json = json_process(response)
        logger.info(f"Replayer Action response:\n {response}")

        return response_json
    
    
    def analyst_image(self, image_path, *prompts):

        content = '\n'.join(map(str, prompts))
        # gemini-2.0-pro-exp-02-05  gemini-1.5-pro gpt-4o
        model_name = "gemini-2.0-pro-exp-02-05"
        logger.info("******model name:"+ model_name)
        retries = 0
        max_retries = 3
        success = False

        while retries < max_retries and not success:
            try:
                response = self.chat.image_respond_gemini(image_path, content, model_name)
                # response = self.chat.image_respond_gemini_google(image_path, content, model_name)
                # response = self.chat.image_respond(image_path, content, model_name)

                response_json = json_process(response)
                logger.info(f"Replayer Action response:\n {response}")
                success = True
            except (KeyError, TypeError):
                retries += 1
                if retries >= max_retries:
                    raise  
                continue      
        return response_json
    

    # def analyst_image_gpt(self, image_path, *prompts):
        
    #     content = '\n'.join(map(str, prompts))
    #     model_name = "gpt-4o"
    #     logger.info("******model name:"+ model_name)
        
    #     response_json = json_process(response)
    #     logger.info(f"Replayer Action response:\n {response}")
    #     return response_json
    
    

   


    
