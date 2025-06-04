from core.llm_chat import LLMChat
import pyautogui
from replay_agent.planner.replayer_action import ReplayerAction
from prompt.action_generator import PURPOSE
from prompt.action_generator import ANALYZE_REQUEST
from prompt.action_generator import ANALYZE_REQUEST_ACTION
from prompt.action_generator import ACTION_VERIFY
from prompt.action_generator import STEP_TO_ACTION
from prompt.action_generator import ANALYZE_REQUEST_STEPS
from prompt.action_generator import DETERMINE_STEP
from replay_agent.position_finder.position_extractor import PositionExtractor
from replay_agent.screenshot_processor.screenshot_capture import ScreenshotCapture
from replay_agent.exception_handler.exception_manager import ExceptionManager
from replay_agent.action_executor import switch_action
from replay_agent.action_executor import dropdown_select_action
from replay_agent.action_executor import click_action
from replay_agent.action_executor import hotkey_action



import os, re
import json


from utils.logger.logger_setup_data_extraction import logger

class AutomatedActions:
    def __init__(self,image_folder_path):    
        self.image_folder_path = image_folder_path 
        self.chat = LLMChat() 
    
    def get_knowledge_base(self):
        try:
            with open('output/knowledge.json', 'r', encoding='UTF-8') as file:
                data = file.read()
            json_data = json.loads(data)

            business_flow_path = os.path.join(self.image_folder_path, 'business_flow.json')
            with open(business_flow_path, 'w', encoding='UTF-8') as output_file:
                json.dump(json_data["knowledgeJson"]["business_flow"], output_file, ensure_ascii=False, indent=4)
            return str(json_data["knowledgeJson"]["business_flow"])

        except Exception as e:
            print(f"Error when reading knowledge json: {e}")
        return None
    
    def generate_steps_choose(self):

        knowledge_base = f"knowledge base:"+ self.get_knowledge_base()
        purpose = f"PURPOSE:"+PURPOSE
        analysis_request = f"ANALYZE_REQUEST:"+ANALYZE_REQUEST_STEPS
        replayerAction = ReplayerAction(self.chat)

        steps_replay_json_list = ["steps"] 
        steps_replay_json = replayerAction.get_respond_prompt(steps_replay_json_list, knowledge_base, purpose, analysis_request)
        flow_steps = steps_replay_json["steps"] 

        # steps_knowledge_path = os.path.join(self.image_folder_path, "action_knowledge_list.json")
        # with open(steps_knowledge_path, 'w', encoding='utf-8') as f:
        #     json.dump(steps_replay_json, f, ensure_ascii=False, indent=4)
        
        # flow_steps_status = False
        flow_steps["status"] = False
        flow_steps["description"] = purpose
        flow_steps["executing_step"] = 1
        # steps = []

        steps_json = {
            "flow_steps":flow_steps
        }

        # generate actions

        screenshot_capture = ScreenshotCapture(self.image_folder_path)

        action_index = 0
        flow_step_index = 0
        actions_list = []

        while not steps_json["flow_steps"]["status"]:
            if steps_json["flow_steps"]["status"].startswith("Unable_execute"):
                break

            last_steps_key = None

            # Iterate through the keys in the JSON data
            for key, value in steps_json.items():
                # Check if the key ends with '_steps' and contains 'status' with value false
                if isinstance(value, dict) and value.get('status') is False:
                    last_steps_key = key
            # if last_steps_key contain "flow": flow_steps_flag = True
            flow_steps_flag = (last_steps_key == "flow_steps")
            
            # executing_steps = steps_json[last_steps_key]
            while not steps_json[last_steps_key]["status"]:

                # 3
                screenshot = screenshot_capture.get_screen_snapshot("screenshot_" + str(action_index) + ".png")
                determine_step = DETERMINE_STEP.format(step = steps_json[last_steps_key][str(steps_json[last_steps_key]["executing_step"])])
                action_from_step_list = ["executed","can_execute","description"]
                action_from_step = replayerAction.analyst_image(screenshot, action_from_step_list, determine_step)

                if action_from_step["step_index"] != "unknown":
                    step_index = int(action_from_step["step_index"])
                    if flow_steps_flag: 
                        flow_step_index = step_index
                    else: 
                        action_from_step["step_index"] = str(flow_step_index) + "." + str(action_from_step["step_index"])
                    # if step_index > action_index :
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

                    elif action_from_step["action_type"] == "KEY_PRESS":
                        key = action_from_step["key_code"]
                        pyautogui.press(key)
                        execute_flag = True          

                    elif action_from_step["action_type"] == "unknow":                  
                        logger.info("Error Handling-----1")
                        return
                    
                    if execute_flag:
                        screenshot_verify = screenshot_capture.get_screen_snapshot("screenshot_" + str(action_index) + "_v.png")
                        action_verify = ACTION_VERIFY.format(description = action_from_step["step_description"])
                        action_verify_replay_json = replayerAction.analyst_image(screenshot_verify, action_verify)
                        verify_result = action_verify_replay_json['verify_result']
                        # verify_result = "yes"
                        if verify_result == "no" :
                            logger.info("Error Handling-----verified failed")
                            return
                        elif len(steps_json[last_steps_key])-2 > step_index:
                            action_index += 1
                            action_from_step["action_index"] = action_index
                            actions_list.append(action_from_step)
                        else:
                            action_index += 1
                            action_from_step["action_index"] = action_index
                            actions_list.append(action_from_step)
                            steps_json[last_steps_key]["status"] = True
                            break
                        

                    # if step_index <= action_index :
                    #     logger.info("Error Handling---3")
                    #     return


                else:
                    logger.info("Error Handling---Unknow step")
                    # 当前界面不能执行 steps_index + 1
                    if flow_steps_flag:
                        exception_manager = ExceptionManager()
                        exception_steps = exception_manager.plan_for_exception(flow_steps[str(flow_step_index + 1)],"",screenshot)
                        exception_steps_json = json.loads(exception_steps)
                        exception_steps_json["status"] = False
                        exception_steps_json["description"] = flow_steps[str(flow_step_index + 1)]
                        exception_steps_json["executing_step"] = 1
                        steps_json["exception_steps_" + str(flow_step_index + 1)] = exception_steps_json
                        break
                    else:
                        return
        
        steps_knowledge_path = os.path.join(self.image_folder_path, "action_knowledge_list.json")
        with open(steps_knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(steps_json, f, ensure_ascii=False, indent=4)

        action_execute_json = {
            "actions": actions_list
        }

        actions_execute_path = os.path.join(self.image_folder_path, "action_execute_list.json")
        with open(actions_execute_path, 'w', encoding='utf-8') as f:
            json.dump(action_execute_json, f, ensure_ascii=False, indent=4)


        return
    

    def generate_steps(self):

        knowledge_base = f"knowledge base:"+ self.get_knowledge_base()
        purpose = f"PURPOSE:"+PURPOSE
        analysis_request = f"ANALYZE_REQUEST:"+ANALYZE_REQUEST_STEPS
        replayerAction = ReplayerAction(self.chat)

        # 3
        steps_replay_json_list = ["steps"] 
        steps_replay_json = replayerAction.get_respond_prompt(steps_replay_json_list, knowledge_base, purpose, analysis_request)
        flow_steps = steps_replay_json["steps"] 

        flow_steps["status"] = False
        flow_steps["description"] = purpose
        flow_steps["executing_step"] = 1

        steps_json = {
            "flow_steps":flow_steps,
            "values":{},
            "windows":{},
        }

        # generate actions

        screenshot_capture = ScreenshotCapture(self.image_folder_path)

        actions_execute_list = []
        # actions_steps_list = []
        step_index = 0
        action_index = 1

        while not steps_json["flow_steps"]["status"]:

            last_steps_key = None

            # Iterate through the keys in the JSON data
            for key, value in steps_json.items():
                # Check if the key ends with '_steps' and contains 'status' with value false
                if isinstance(value, dict) and value.get('status') is False:
                    last_steps_key = key
            # if last_steps_key contain "flow": flow_steps_flag = True
            flow_steps_flag = (last_steps_key == "flow_steps")
            
            executing_step = steps_json[last_steps_key]

            step_count = sum(1 for key in executing_step if key.isdigit())

            if executing_step["executing_step"] > step_count:
                executing_step["status"] = True
                executing_step["executing_step"] = 0
                if not flow_steps_flag:
                    handle_steps = executing_step["handle_steps"]
                    handle_steps_index = executing_step["handle_steps_index"]
                    steps_json[handle_steps]["executing_step"] = handle_steps_index + 1
                    continue
                executing_step["executing_step"] += 1
                break

            while not executing_step["status"]:
                step_index += 1
                step_description = executing_step[str(executing_step["executing_step"])]
                if len(steps_json["values"]) > 0:
                    step_description += "The following values are available for reference, Only when the following key appears can its value be used:" + str(steps_json["values"])
                logger.info(f"## Start executing {last_steps_key}: {executing_step['executing_step']}: {step_description}")
                screenshot = screenshot_capture.get_screen_snapshot("screenshot_" + str(step_index) + "_" + last_steps_key + "_" + str(executing_step["executing_step"]) + ".png")
                determine_step = DETERMINE_STEP.format(step = step_description)
                determine_step_list = ["can_execute"]
                determine_step_json = replayerAction.analyst_image(screenshot, determine_step_list, determine_step)
                determine_step_json["executed"] = "False"
                # determine_step_json["can_execute"] = "True"
                if determine_step_json["executed"] == "True":
                    if executing_step["executing_step"] >= step_count:
                        executing_step["executing_step"] += 1
                        continue
                    else:
                        executing_step["status"] = True
                        executing_step["executing_step"] = 0
                        break
                elif determine_step_json["can_execute"] == "True" or determine_step_json["can_execute"] == "true":
                    step_to_actions = STEP_TO_ACTION.format(step = step_description, values = steps_json["values"], executed_steps = "")
                    actions_from_step_list = ["actions"]
                    actions_from_step = replayerAction.analyst_image(screenshot, actions_from_step_list, step_to_actions)
                    actions_from_step["actions"]
                    actions_from_step["step_index"] = last_steps_key + "." + str(executing_step["executing_step"])
                    actions_from_step["step_description"] = executing_step[str(executing_step["executing_step"])]
                    executing_step["actions"+"_"+ str(executing_step["executing_step"])] = actions_from_step["actions"]
                    action_index = self.execute_actions(actions_from_step, actions_execute_list, screenshot, action_index, steps_json)

                    # verify
                    screenshot_verify = screenshot_capture.get_screen_snapshot("screenshot_" + str(step_index) + "_v.png")
                    verify_result = self.verify_step(screenshot_verify, executing_step[str(executing_step["executing_step"])], actions_from_step)
                    if verify_result:
                        if executing_step["executing_step"] >= step_count:
                            executing_step["status"] = True
                            executing_step["executing_step"] = 0
                            if not flow_steps_flag:
                                handle_steps = executing_step["handle_steps"]
                                handle_steps_index = executing_step["handle_steps_index"]
                                steps_json[handle_steps]["executing_step"] = handle_steps_index + 1
                            break
                        executing_step["executing_step"] += 1
                        logger.info(f"## Successfully completed {last_steps_key}: {executing_step['executing_step']}: {step_description}")                        
                        continue
                    else:
                        determine_step_json["reason"]
                        actions_execute_list[-1]["status"] = "failed"
                        logger.info("Error Handling---verified failed")
                        self.error_handle(screenshot_verify, steps_json, last_steps_key, determine_step_json["reason"])
                        break

                else:
                    logger.info("Error Handling---Unknow step")
                    self.error_handle(screenshot, steps_json, last_steps_key, determine_step_json["reason"])
                    break
        
        steps_knowledge_path = os.path.join(self.image_folder_path, "action_knowledge_list.json")
        with open(steps_knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(steps_json, f, ensure_ascii=False, indent=4)

        action_execute_json = {
            "actions_execute_list": actions_execute_list
        }

        actions_execute_path = os.path.join(self.image_folder_path, "action_execute_list.json")
        with open(actions_execute_path, 'w', encoding='utf-8') as f:
            json.dump(action_execute_json, f, ensure_ascii=False, indent=4)

        return


    def execute_actions(self, actions_from_step, actions_list, screenshot, action_index, steps_json):
        actions = actions_from_step["actions"]
        for index, action in enumerate(actions):
            action_type = action["action_type"]
            logger.info("action_type: " + action_type)
            if action_type == "LEFT_CLICK":
                click_element = action["key_element"]
                click_element_type = action["key_element_type"]
                position_extractor = PositionExtractor()
                x_e, y_e = position_extractor.get_position_by_name(self.image_folder_path, screenshot, click_element, click_element_type)
                action["click_position"] = str(x_e) + "," + str(y_e)
                if click_element_type == "drop_down_box_and_select_value":
                    dropdown_select_action.select_dropdown_option(x_e, y_e, action["value"])
                else:
                    click_action.click(x_e, y_e)

            elif action_type == "KEY_WRITE":
                key_code = action["key_element"]
                pyautogui.write(key_code)

            elif action_type == "KEY_HOTKEY":
                key_code = action["key_element"]
                keys = [key.lower() for key in key_code.split('+')]
                hotkey_action.hotkey(*keys)

            elif action_type == "KEY_PRESS":
                key_code = action["key_element"]
                pyautogui.press(key_code)

            elif action_type == "KEY_UP":
                key_code = action["key_element"]
                pyautogui.up(key_code)

            elif action_type == "KEY_DOWN":
                key_code = action["key_element"]
                pyautogui.down(key_code)
            
            elif action_type == "SWITCH":
                app_name = action["key_element"]
                if app_name in steps_json["windows"]:
                    app_name = steps_json["windows"][app_name]
                full_app_name = switch_action.switch_window(app_name)
                if full_app_name != app_name:
                    steps_json["windows"][app_name] = full_app_name

            elif action_type == "GET_VALUE":
                value_name = action["key_element"]
                value = action["value"]
                steps_json["values"][value_name] = value


            actions_list.append(action.copy())
            actions_list[-1]["action_list_index"] = action_index
            actions_list[-1]["action_index"] = actions_from_step["step_index"] + "#" + str(action["action_index"])
            action_index += 1

            if len(actions)>1 and index < len(actions) - 1:
                folder_path = os.path.dirname(screenshot)
                screenshot_capture = ScreenshotCapture(folder_path)
                screenshot_for_action= os.path.basename(screenshot).replace(".png", "#" + str(index+1) + ".png")
                screenshot = screenshot_capture.get_screen_snapshot(screenshot_for_action)

        return action_index
        

    def verify_step(self, image_path, *step_description):
        # Verify the step using the image and step description
        action_verify = ACTION_VERIFY.format(description = step_description)
        replayerAction = ReplayerAction(self.chat)
        action_verify_replay_json = replayerAction.analyst_image_gpt(image_path, [], action_verify)
        verify_result = action_verify_replay_json['executed']

        if verify_result == "false":
            return False
        return True
    
    def error_handle(self, image_path, steps_json, last_steps_key, reason = None):

    
        handle_num = last_steps_key.count("handle")
        exception_manager = ExceptionManager()

        if handle_num > 1:
            last_steps_key = "flow_steps"
            executing_step = steps_json[last_steps_key]
            executing_step_index = executing_step["executing_step"]
            pattern = r'^flow_steps_\d+\(\d+\)_handle_steps$'
            exception_key = "flow_steps_" + str(executing_step_index) + "_handle_steps"
            exception_count = 0
            for key in steps_json:
                if re.match(pattern, key):
                    exception_count += 1
                if key.startswith(exception_key):
                    steps_json[key]["status"] = "Unable_execute_" + str(steps_json[key]["executing_step"])
            if exception_count > 0:
                logger.info(f"Cannot execute step{str(steps_json[last_steps_key]["executing_step"])}")
                steps_json[last_steps_key]["status"] = "Unable_execute_" + str(steps_json[last_steps_key]["executing_step"])
                return
            error_handle_steps_name = last_steps_key + "_" + str(executing_step_index) + "("+ str(exception_count)+")" +"_handle_steps"
            
        else:
            executing_step = steps_json[last_steps_key]
            executing_step_index = executing_step["executing_step"]
            error_handle_steps_name = last_steps_key + "_" + str(executing_step_index) +"_handle_steps"
        step_description = executing_step[str(executing_step_index)]

        exception_steps = exception_manager.plan_for_exception(reason ,step_description,"",image_path)
        if exception_steps == None:
            executing_step["executing_step"] += 1
            return
        exception_steps_json = json.loads(exception_steps)
        exception_steps_json["status"] = False
        exception_steps_json["description"] = step_description
        exception_steps_json["executing_step"] = 1
        exception_steps_json["handle_steps"] = last_steps_key
        exception_steps_json["handle_steps_index"] = executing_step_index
        steps_json[error_handle_steps_name] = exception_steps_json

        return steps_json

    






