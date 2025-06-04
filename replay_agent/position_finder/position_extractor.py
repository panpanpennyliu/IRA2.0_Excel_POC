from core.llm_chat import LLMChat
from replay_agent.planner.replayer_action import ReplayerAction
from replay_agent.screenshot_processor.image_editor import ImageEditor
from prompt.action_generator import VERIFY_POSITION
from prompt.action_generator import GET_LABELS
from prompt.action_generator import IDENTIFY_TEXT_BOX_LABELS
from prompt.action_generator import GET_TABLE_INITIAL_VALUE
from prompt.position_finder import INITIAL_COORDINATE
from replay_agent.position_finder.ocr_position import OcrPosition
import re
from utils.logger.logger_setup_data_extraction import logger

import os


class PositionExtractor:
    def __init__(self):      
        self.chat = LLMChat() 

    def get_position_by_name(self, image_folder_path, image_path, element_name, element_type):
        if element_type =="input_box":
            x,y = self.get_position_input_box(image_folder_path, image_path, element_name)

        elif element_type =="cell":
            x,y = self.get_position_cell(image_folder_path, image_path, element_name)

        elif "text" in element_type:
            x,y = self.get_position_text_button(image_folder_path, image_path, element_name)
        
        elif element_type =="drop_down_box_and_select_value":
            x,y = self.get_position_drop_down_box(image_folder_path, image_path, element_name)
        return x,y
    
    def get_position_input_box(self, image_folder_path, image_path, element_name):
        
        imageEditor = ImageEditor(image_path)

        save_path_mark_text_box = os.path.join (image_folder_path, "position_"+ element_name + "_mark_input_box.png")

        input_boxes = imageEditor.mark_text_box(save_path_mark_text_box)

        index = 0

        while index < 3:

            identify_text_box_labels = IDENTIFY_TEXT_BOX_LABELS.format(element_name = element_name)

            replayerAction = ReplayerAction(self.chat)

            text_box_labels_reply_json = replayerAction.analyst_image(save_path_mark_text_box,[], identify_text_box_labels)

            number = int(text_box_labels_reply_json["number"])

            x, y, w, h = input_boxes[number]
            e_x = x + w//2
            e_y = y + h//2

            position_verify = self.verify_position(e_x, e_y, element_name, image_folder_path, image_path, str(number)+"_"+str(index))

            if position_verify:
                break
            else:
                index += 1

        return e_x, e_y
    
    def get_position_drop_down_box(self, image_folder_path, image_path, element_name):
        
        imageEditor = ImageEditor(image_path)

        save_path_mark_text_box = os.path.join (image_folder_path, "position_"+ element_name + "_mark_text_box.png")

        input_boxes = imageEditor.mark_text_box(save_path_mark_text_box)

        index = 0

        while index < 3:

            identify_text_box_labels = IDENTIFY_TEXT_BOX_LABELS.format(element_name = element_name)

            replayerAction = ReplayerAction(self.chat)

            text_box_labels_reply_json = replayerAction.analyst_image(save_path_mark_text_box,[], identify_text_box_labels)

            number = int(text_box_labels_reply_json["number"])

            x, y, w, h = input_boxes[number]
            e_x = x + w - 15
            e_y = y + h//2

            position_verify = self.verify_position(e_x, e_y, element_name, image_folder_path, image_path, str(number)+"_"+str(index))

            if position_verify:
                break
            else:
                index += 1

        return e_x, e_y
    
    def get_position_cell(self, image_folder_path, image_path, element_name):

        imageEditor = ImageEditor(image_path)

        index = 0

        while index < 3:

            save_path_mark_text_box = os.path.join (image_folder_path, "position_"+ element_name + "_table_lines.png")

            horizontal_table, vertical_table = imageEditor.detect_table_lines(save_path_mark_text_box)
            
            x0 = (vertical_table[0][0] + vertical_table[1][0]) // 2 
            y0 = (horizontal_table[0][1] + horizontal_table[1][1]) // 2 

            initial_value_add_X_path = os.path.join(image_folder_path, "position_"+ element_name + "_initial_value_" + str(index) + ".png")
            
            initial_value_add_X_image = imageEditor.add_X(x0, y0, 5, initial_value_add_X_path)

            get_table_initial_value = GET_TABLE_INITIAL_VALUE

            replayerAction = ReplayerAction(self.chat)

            table_initial_value_json = replayerAction.analyst_image(initial_value_add_X_image,[], get_table_initial_value)

            row_0 = table_initial_value_json["row"]
            column_0 = table_initial_value_json["column"]

            match = re.search(r'([A-Za-z]+)(\d+)', element_name)
            column_element = match.group(1)  # 提取字母部分，例如 "I"
            row_element = match.group(2)

            row_i = int(row_element) - int(row_0)
            column_i = ord(column_element) - ord(column_0)

            e_x = (vertical_table[column_i][0] + vertical_table[column_i + 1][0]) // 2 + 7
            e_y = (horizontal_table[row_i][1] + horizontal_table[row_i + 1][1]) // 2 + 7

            position_verify = self.verify_position(e_x, e_y, element_name, image_folder_path, image_path, str(row_i)+"_"+str(column_i)+"_"+str(index))

            if position_verify:
                break
            else:
                index += 1

        

        return e_x, e_y
    
    def get_position_text_button(self, image_folder_path, image_path, element_name):

        # 1.initial coordinate
        index = 0
        # wight = 
        replayerAction = ReplayerAction(self.chat)
        imageEditor = ImageEditor(image_path)
        height, width = imageEditor.get_image_size()

        while index < 3:

            initial_coordinate = INITIAL_COORDINATE.format(element_name = element_name, width = width, height = height)

            replayerAction = ReplayerAction(self.chat)
            initial_coordinate_key_list = ["x", "y"]
            initial_coordinate_json = replayerAction.analyst_image_gpt(image_path, initial_coordinate_key_list, initial_coordinate)

            init_x = initial_coordinate_json["x"]
            init_y = initial_coordinate_json["y"]

            if int(init_x) > width or int(init_y) > height:
                continue

            # 2.ocr
            save_path_ocr = os.path.join(image_folder_path, "position_"+ element_name + "_ocr_"+ str(init_x) + "_"+ str(init_y) + ".png")
            ocr_position = OcrPosition()
            e_x, e_y = ocr_position.correct_click_coordinates(element_name, init_x, init_y, image_path, save_path_ocr)

            position_verify = self.verify_position(e_x, e_y, element_name, image_folder_path, image_path, "_"+str(index))

            if position_verify:
                break
            else:
                index += 1

        return e_x, e_y
    
    def verify_position(self, x, y, element_name, image_folder_path, image_path, number):

        verify_position_path = os.path.join(image_folder_path, "position_"+ element_name + "_verify_position_"+ str(number) +".png")
        
        imageEditor = ImageEditor(image_path)

        verify_add_X_image = imageEditor.add_X(x, y, 5, verify_position_path)

        verify_position = VERIFY_POSITION.format(element_name = element_name)

        replayerAction = ReplayerAction(self.chat)

        verify_position_reply_json = replayerAction.analyst_image(verify_add_X_image, [],verify_position)

        position_verify_result = verify_position_reply_json["position"]

        if position_verify_result == "yes":
            logger.info("verified coordinate:(" + str(x) + "," + str(y) + ")")
            return True
        logger.info("error coordinate:(" + str(x) + "," + str(y) + ")")
        return False
    








