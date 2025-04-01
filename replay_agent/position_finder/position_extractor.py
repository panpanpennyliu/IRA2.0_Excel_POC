from core.llm_chat import LLMChat
from replay_agent.planner.replayer_action import ReplayerAction
from replay_agent.position_finder.image_editor import ImageEditor
from prompt.action_generator import VARIFY_POSITION
from prompt.action_generator import GET_LABELS

import re
from utils.logger_setup_data_extraction import logger
from utils.json_processor import json_process


class PositionExtractor:
    def __init__(self):      
        self.chat = LLMChat() 

    
    def get_position_by_name(self, image_path, element_name):

        pattern = r"cell\s+([A-Za-z]+)(\d+)"
        match = re.search(pattern, element_name)

        if match:
            letter = match.group(1)  
            number = match.group(2)
            if letter > 'A' and number > '1':
                first_row_x = self.get_position_by_label(image_path, "cell " + letter +"1")[0]
                first_col_y = self.get_position_by_label(image_path, "cell A" + number)[1]
                logger.info(element_name + "accurate coordinate:(" + str(first_row_x) + "," + str(first_col_y) + ")")
                return first_row_x, first_col_y
            
        return self.get_position_by_label(image_path, element_name)
    

    def get_position_by_label(self, image_path, element_name):

        imageEditor = ImageEditor(image_path)

        label_offset = 0

        while label_offset < 2 :

            save_path_number_labels = "input\\screenshot\\mark_number_labels.png"

            label_cols, label_rows = imageEditor.draw_grid_and_labels(save_path_number_labels, label_offset)

            replayerAction = ReplayerAction(self.chat)

            get_labels = GET_LABELS.format(element_name = element_name)
            
            labels_reply = replayerAction.get_position_gemini(save_path_number_labels, get_labels)

            # varify

            labels_reply_json = json_process(labels_reply)

            grid_cell = int(labels_reply_json[element_name]["grid_cell"])

            center_x, center_y = imageEditor.labels_to_position(label_cols, label_rows, grid_cell, label_offset)

            radius_varify = 3

            image_varify = "input\\screenshot\\mark_varify.png"

            add_circle_image_varify = imageEditor.add_circle(center_x, center_y, radius_varify, image_varify)

            varify_position = VARIFY_POSITION.format(element_name = element_name)
            varify_position_reply = replayerAction.get_position_gemini(image_varify, varify_position)

            varify_position_reply_json = json_process(varify_position_reply)
            position_varify = varify_position_reply_json[element_name]["RGB_element completely inside " + element_name]


            if position_varify == "yes":
                print("varified coordinate:(" + str(center_x) + "," + str(center_y) + ")")
                return center_x ,center_y
            else:
                label_offset = label_offset + 1
        

        return center_x ,center_y








