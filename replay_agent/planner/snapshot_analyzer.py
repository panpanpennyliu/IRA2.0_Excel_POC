from core.llm_chat import LLMChat
import pyautogui
from replay_agent.planner.replayer_action import ReplayerAction
from prompt.action_generator import PURPOSE
from prompt.action_generator import ANALYZE_REQUEST
from utils.json_processor import json_process

import os
import json


from utils.logger_setup_data_extraction import logger

class SnapshotAnalyzer:
    def __init__(self):      
        self.chat = LLMChat() 

    def get_screen_snapshot(self):
        try:
            logger.info(f"Start Screenshot.... ")
            frame_folder_path = os.path.join('input', 'screenshot')
            screenshot = pyautogui.screenshot()
            file_path = os.path.join(frame_folder_path,"screenshot.png")
            screenshot.save(file_path)
            logger.info(f"Screenshot saved as {file_path}")
            return file_path
        except Exception as e:
            logger.info(f"Error when taking a screenshot of the current screen: {e}")
        return None
    

    
    def get_knowledge_base(self):
        try:
            with open('output/concept_dta_sample_5_e.json', 'r', encoding= 'UTF-8') as file:
                data = file.read()
            # base = data.replace(':',"=").replace('{','').replace('}','')
            # print(len(base.split('\n')))
            return data

        except Exception as e:
            print(f"Error when reading knowledge json: {e}")
        return None
    
    def generate_action(self):
        
        # get action from knowledge
        # screen_concept = self.get_screen_snapshot()
        knowledge_base = f"knowledge base:"+ self.get_knowledge_base()
        propose = f"PURPOSE:"+PURPOSE
        analysis_request = f"ANALYZE_REQUEST:"+ANALYZE_REQUEST
        replayerAction = ReplayerAction(self.chat)
        action_replay = replayerAction.get_action(analysis_request, propose, knowledge_base)
        action_replay_json = json_process(action_replay)
        with open('output/action_text.json', 'w', encoding='utf-8') as f:
            json.dump(action_replay_json, f, ensure_ascii=False, indent=4)

        

        # determine start action
        # get mouseclick position


        return action_replay






