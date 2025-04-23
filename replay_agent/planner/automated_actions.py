from core.llm_chat import LLMChat
import pyautogui
from replay_agent.planner.replayer_action import ReplayerAction
from prompt.action_generator import PURPOSE
from prompt.action_generator import ANALYZE_REQUEST
from prompt.action_generator import ANALYZE_REQUEST_ACTION
from prompt.action_generator import ACTION_VERIFY
from prompt.action_generator import DETERMINE_ACTION
from prompt.action_generator import ANALYZE_REQUEST_STEPS
from prompt.action_generator import DETERMINE_STEP
from replay_agent.position_finder.position_extractor import PositionExtractor
from replay_agent.screenshot_processor.screenshot_capture import ScreenshotCapture
from replay_agent.exception_handler.exception_manager import ExceptionManager

import os
import json


from utils.logger.logger_setup_data_extraction import logger

class AutomatedActions:
    def __init__(self,image_folder_path):    
        self.image_folder_path = image_folder_path 
        self.chat = LLMChat() 
    
    def get_knowledge_base(self):
        try:
            with open('output/knowledge_flow.json', 'r', encoding= 'UTF-8') as file:
                data = file.read()
            # base = data.replace(':',"=").replace('{','').replace('}','')
            # print(len(base.split('\n')))
            return data

        except Exception as e:
            print(f"Error when reading knowledge json: {e}")
        return None
    
    def generate_steps(self):

        knowledge_base = f"knowledge base:"+ self.get_knowledge_base()
        purpose = f"PURPOSE:"+PURPOSE
        analysis_request = f"ANALYZE_REQUEST:"+ANALYZE_REQUEST_STEPS
        replayerAction = ReplayerAction(self.chat)

        # 3
        steps_replay_json = replayerAction.get_respond_prompt(knowledge_base, purpose, analysis_request)
        flow_steps = steps_replay_json["steps"] 

        # steps_knowledge_path = os.path.join(self.image_folder_path, "action_knowledge_list.json")
        # with open(steps_knowledge_path, 'w', encoding='utf-8') as f:
        #     json.dump(steps_replay_json, f, ensure_ascii=False, indent=4)
        
        # flow_steps_status = False
        flow_steps["status"] = False
        # steps = []

        steps_json = {
            "flow_steps":flow_steps
        }

        # generate actions

        screenshot_capture = ScreenshotCapture(self.image_folder_path)

        action_index = 0
        step_index = 0
        actions_list = []
        
        

        while not steps_json["flow_steps"]["status"]:
            screenshot = screenshot_capture.get_screen_snapshot("screenshot_" + str(action_index) + ".png")
            determine_step = DETERMINE_STEP

            # 3
            action_from_step = replayerAction.analyst_image(screenshot, purpose, determine_step, steps_replay_json)

            if action_from_step["step_index"] != "unknown":
                step_index = int(action_from_step["step_index"])
                if step_index > action_index :
                    logger.info("Start action")
                    if action_from_step["action_type"] == "LEFT_CLICK":
                        position_extractor = PositionExtractor()
                        x_e, y_e = position_extractor.get_position_by_name(self.image_folder_path, screenshot, action_from_step["click_element"], action_from_step["click_element_type"])
                        action_from_step["position"] = str(x_e) + "," + str(y_e)
                        pyautogui.click(x_e, y_e)
                        execute_flag = True


                    elif action_from_step["action_type"] == "KEY_WRITE":
                        pyautogui.write(action_from_step["key_code"])
                        execute_flag = True

                    elif action_from_step["action_type"] == "KEY_HOTKEY":
                        keys = action_from_step["key_code"].split('+')
                        pyautogui.hotkey(*keys)
                        execute_flag = True              

                    elif action_from_step["action_type"] == "unknow":                  
                        logger.info("Error Handling-----1")
                        return
                    
                    if execute_flag:
                        screenshot_verify = screenshot_capture.get_screen_snapshot("screenshot_" + str(action_index) + "_v.png")
                        action_verify = ACTION_VERIFY.format(description = action_from_step["step_description"])
                        action_verify_replay_json = replayerAction.analyst_image(screenshot_verify, action_verify)
                        verify_result = action_verify_replay_json['verify_result']
                        if verify_result == "no" :
                            logger.info("Error Handling-----2")
                            return
                        elif len(flow_steps[0]) > step_index:
                            action_index += 1
                            action_from_step["action_index"] = action_index
                            actions_list.append(action_from_step)
                        else:
                            action_from_step["action_index"] = action_index
                            actions_list.append(action_from_step)
                            steps_json["flow_steps"]["status"] = True
                            break
                    

                # if step_index <= action_index :
                #     logger.info("Error Handling---3")
                #     return


            else:
                logger.info("Error Handling---Unknow step")
                # 当前界面不能执行steps_index + 1
                exception_manager = ExceptionManager()
                exception_steps = exception_manager.plan_for_exception(flow_steps[str(step_index + 1)],"",screenshot)
                exception_steps_json = json.loads(exception_steps)
                exception_steps_json["status"] = False
                steps_json["exception_steps_" + str(step_index + 1)] = exception_steps_json
                steps_knowledge_path = os.path.join(self.image_folder_path, "action_knowledge_list.json")
                with open(steps_knowledge_path, 'w', encoding='utf-8') as f:
                    json.dump(steps_json, f, ensure_ascii=False, indent=4)
                return

        action_execute_json = {
            "actions": actions_list
        }

        actions_execute_path = os.path.join(self.image_folder_path, "action_execute_list.json")
        with open(actions_execute_path, 'w', encoding='utf-8') as f:
            json.dump(action_execute_json, f, ensure_ascii=False, indent=4)


        return
    

    # def generate_actions(self):

    






