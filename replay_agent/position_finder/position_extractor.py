from core.llm_chat import LLMChat
from replay_agent.planner.replayer_action import ReplayerAction
from replay_agent.position_finder.image_editor import ImageEditor
from prompt.action_generator import VERIFY_POSITION
from prompt.action_generator import GET_LABELS
from prompt.action_generator import IDENTIFY_TEXT_BOX_LABELS
import re
from utils.logger_setup_data_extraction import logger
from utils.json_processor import json_process
from replay_agent.planner.snapshot_analyzer import SnapshotAnalyzer

import pyautogui
import os
import time


class PositionExtractor:
    def __init__(self):      
        self.chat = LLMChat() 

    def get_position_by_name(self, image_folder_path, image_path, element_name, element_type):
        if element_type =="input_box":
            x,y = self.get_position_input_box(image_folder_path, image_path, element_name)

        elif element_type =="cell":
            x,y = self.get_position_cell(image_folder_path, image_path, element_name)

        elif element_type =="text_button":
            x,y = self.get_position_text_button(image_folder_path, image_path, element_name)

        return x,y
    
    def get_position_input_box(self, image_folder_path, image_path, element_name):
        
        imageEditor = ImageEditor(image_path)

        save_path_mark_text_box = os.path.join (image_folder_path, element_name + "_mark_text_box.png")

        input_boxes = imageEditor.mark_text_box(save_path_mark_text_box)

        index = 0

        while index < 3:

            identify_text_box_labels = IDENTIFY_TEXT_BOX_LABELS.format(element_name = element_name)

            replayerAction = ReplayerAction(self.chat)

            text_box_labels_reply = replayerAction.get_position_gemini(save_path_mark_text_box, identify_text_box_labels)

            text_box_labels_reply_json = json_process(text_box_labels_reply)

            number = int(text_box_labels_reply_json[element_name]["number"])

            x, y, w, h = input_boxes[number]
            e_x = x + w//2
            e_y = y + h//2

            position_verify = self.verify_position(e_x, e_y, element_name, image_folder_path, image_path, str(number)+"_"+str(index))

            if position_verify:
                break
            else:
                index += 1

        return e_x, e_y
    
    def get_position_cell(self, image_folder_path, image_path, element_name):
        
        imageEditor = ImageEditor(image_path)

        save_path_mark_text_box = os.path.join (image_folder_path, element_name + "_mark_text_box.png")

        input_boxes = imageEditor.mark_text_box(save_path_mark_text_box)
        

        return 1,1
    
    def get_position_text_button(self, image_folder_path, image_path, element_name):
        return 1,1
    
    def verify_position(self, x, y, element_name, image_folder_path, image_path, number):

        verify_position_path = os.path.join(image_folder_path, element_name + "_verify_position_"+ str(number) +".png")
        
        imageEditor = ImageEditor(image_path)

        # snapshot_analyzer = SnapshotAnalyzer(image_folder_path)

        verify_add_X_image = imageEditor.add_X(x, y, 5, verify_position_path)

        # screen_concept = snapshot_analyzer.get_screen_snapshot(verify_posision_path)

        verify_position = VERIFY_POSITION.format(element_name = element_name)

        replayerAction = ReplayerAction(self.chat)

        verify_position_reply = replayerAction.get_position_gemini(verify_add_X_image, verify_position)

        verify_position_reply_json = json_process(verify_position_reply)

        position_verify_result = verify_position_reply_json["position"]

        if position_verify_result == "inside":
            logger.info("verified coordinate:(" + str(x) + "," + str(y) + ")")
            return True
        logger.info("error coordinate:(" + str(x) + "," + str(y) + ")")
        return False
    
    def get_position_by_name_0(self, image_folder_path, image_path, element_name):

        pattern = r"cell\s+([A-Za-z]+)(\d+)"
        match = re.search(pattern, element_name)

        verfy_time = 0

        if match:
            letter = match.group(1)  
            number = match.group(2)
            if letter > 'A' and number > '1':
                while verfy_time < 2:

                    first_row_x = self.get_position_by_label(image_folder_path, image_path, "cell " + letter +"1", verfy_time)[0]
                    first_col_y = self.get_position_by_label(image_folder_path, image_path, "cell A" + number, verfy_time)[1]

                    logger.info(element_name + "accurate coordinate:(" + str(first_row_x) + "," + str(first_col_y) + ")")

                    position_verify_result = self.action_and_verify_position(first_row_x, first_col_y, element_name, "cell_verfy_" + str(verfy_time), str(first_row_x) + "_" + str(first_col_y), image_folder_path, image_path)

                    if position_verify_result:
                        return first_row_x , first_col_y
                    else:
                        verfy_time = verfy_time + 1

                return first_row_x, first_col_y
            
            
        return self.get_position_by_label(image_folder_path, image_path, element_name, verfy_time)
    

    def get_position_by_label(self, image_folder_path, image_path, element_name, verfy_time):

        imageEditor = ImageEditor(image_path)

        label_find_time = 0

        while label_find_time < 5 :

            label_offset = label_find_time + verfy_time * 5

            save_path_number_labels = os.path.join (image_folder_path, element_name + "_mark_number_labels_"+ str(label_offset) +".png")

            label_cols, label_rows = imageEditor.draw_grid_and_labels(save_path_number_labels, label_offset)

            replayerAction = ReplayerAction(self.chat)

            get_labels = GET_LABELS.format(element_name = element_name)
            
            labels_reply = replayerAction.get_position_gemini(save_path_number_labels, get_labels)

            # verify

            labels_reply_json = json_process(labels_reply)

            grid_cell = int(labels_reply_json[element_name]["grid_cell"])

            center_x, center_y = imageEditor.labels_to_position(label_cols, label_rows, grid_cell, label_offset)

            position_verify = self.action_and_verify_position(center_x, center_y, element_name, label_offset, grid_cell, image_folder_path, image_path)

            if position_verify:
                return center_x ,center_y
            else:
                label_find_time = label_find_time + 1
        

        return center_x ,center_y
    
    def action_and_verify_position(self, x, y, element_name, label_offset, grid_cell, image_folder_path, image_path):

        verify_posision_path = os.path.join(image_folder_path, element_name + "_click_position_"+ str(label_offset) + "_" + str(grid_cell) + ".png")
        
        imageEditor = ImageEditor(image_path)

        # snapshot_analyzer = SnapshotAnalyzer(image_folder_path)

        verify_add_X_image = imageEditor.add_X(x, y, 5, verify_posision_path)

        # screen_concept = snapshot_analyzer.get_screen_snapshot(verify_posision_path)

        verify_position = VERIFY_POSITION.format(element_name = element_name)

        replayerAction = ReplayerAction(self.chat)

        verify_position_reply = replayerAction.get_position_gemini(verify_add_X_image, verify_position)

        verify_position_reply_json = json_process(verify_position_reply)

        position_verify_result = verify_position_reply_json["position"]

        if position_verify_result == "inside":
            logger.info("verified coordinate:(" + str(x) + "," + str(y) + ")")
            return True
        logger.info("error coordinate:(" + str(x) + "," + str(y) + ")")
        return False
    











