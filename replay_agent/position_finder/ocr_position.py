from utils.logger.logger_setup_data_extraction import logger
import os
import json
from prompt.position_finder import CORRECT_COORDINATE
from replay_agent.planner.replayer_action import ReplayerAction

from replay_agent.screenshot_processor.element_analyzer_easyocr import get_elements

from core.llm_chat import LLMChat
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate

class OcrPosition:
    def __init__(self):
        self.chat = LLMChat()

    def correct_click_coordinates(self, element_name, init_x, init_y, image_path, output_path):
        elements_in_range = get_elements(image_path, output_path, init_x, init_y, 500)
        if len(elements_in_range) == 0:
            logger.info("No elements found in the specified range.")
            return
        ## Check if the text is present in any of the elements
        if element_name is not None:
            match_list = []
            for element in elements_in_range:
                if element_name == element.get("text"):
                    logger.info(f"Found element with text '{element_name}' in range.")
                    match_list.append(element)
            if len(match_list) == 1:
                Number = match_list[0].get("id")
                coordinate = match_list[0].get("coordinates")
                x = coordinate.get("x")
                y = coordinate.get("y")
                print(f"Correct click coordinates to: ({x}, {y})")
                return x, y
        select_element_number = CORRECT_COORDINATE.format(element_name=element_name)
        replayerAction = ReplayerAction(self.chat)
        select_element_number_json = replayerAction.analyst_image(output_path,[] ,select_element_number)
        Number = select_element_number_json["Number"]
        coordinate = elements_in_range[int(Number)].get("coordinates")
        x = coordinate.get("x")
        y = coordinate.get("y")
        print(f"Correct click coordinates to: ({x}, {y})")
        return x, y
        
