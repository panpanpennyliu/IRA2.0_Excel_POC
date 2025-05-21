from utils.logger.logger_setup_data_extraction import logger
from replay_agent.planner.automated_actions import AutomatedActions
from replay_agent.position_finder.position_extractor import PositionExtractor
from datetime import datetime
import os
from replay_agent.action_executor.switch_action import switch_window
from replay_agent.screenshot_processor.screenshot_capture import ScreenshotCapture
import shutil
import logging


def run():
    logger.info(f"started...")    
    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...") 
    current_time_str = datetime.now().strftime('%m%d%H%M%S')
    image_folder_path = os.path.join("log", "screenshot", current_time_str)
    os.makedirs(image_folder_path)
    shutil.copy("output\\knowledge_flow.json", image_folder_path)
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()  # 关闭原有文件流
            # 指定新的日志文件路径
            handler.baseFilename =  os.path.join(image_folder_path, "replay.log") 
            handler.stream = open(handler.baseFilename, handler.mode)


    automated_actions = AutomatedActions(image_folder_path)
    action = automated_actions.generate_steps()

    # screenshot_capture = ScreenshotCapture(image_folder_path)
    # screenshot = screenshot_capture.get_screen_snapshot("screenshot_.png")

    # position_extractor = PositionExtractor()
    # position_extractor.get_position_by_name(image_folder_path, "log\\screenshot\\screenshot.png","Sheet1","text_button")

    # Step 2: Action parser and take action
    # Step 3: Validation Success (Error Handing)
    # Step 4: Still in current screen? 
    # switch_window("Excel")

    # screenshot = "log\\screenshot\\0430142544\\screenshot_3_v.png"
    # position_extractor = PositionExtractor()
    # x_e, y_e = position_extractor.get_position_input_box("log\\screenshot\\0430142544", screenshot,"Amount")


    logger.info(f"end...") 


if __name__ == "__main__": 
    run()




