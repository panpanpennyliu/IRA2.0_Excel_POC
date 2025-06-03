from utils.logger.logger_setup_data_extraction import logger
from replay_agent.planner.automated_actions import AutomatedActions
from replay_agent.position_finder.position_extractor import PositionExtractor
from datetime import datetime
import os
from replay_agent.action_executor.switch_action import switch_window
from replay_agent.screenshot_processor.screenshot_capture import ScreenshotCapture
import shutil
import logging
import cv2
import numpy as np
import pyautogui
import threading
import time


def run():
    logger.info(f"started...")
    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...")
    current_time_str = datetime.now().strftime('%m%d%H%M%S')
    image_folder_path = os.path.join("log", "screenshot", current_time_str)
    os.makedirs(image_folder_path)
    shutil.copy("output\\knowledge_flow.json", image_folder_path)
    # for handler in logger.handlers:
    #     if isinstance(handler, logging.FileHandler):
    #         handler.close()  
    #         handler.baseFilename = os.path.join(image_folder_path, "replay.log")
    #         handler.stream = open(handler.baseFilename, handler.mode)

    automated_actions = AutomatedActions(image_folder_path)

    screen_size = pyautogui.size()
    fps = 10.0
    video_output_filename = os.path.join(image_folder_path, "screen_record.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_output_filename, fourcc, fps, screen_size)

    recording = True

    record_thread = threading.Thread(target=record_screen, args=(out, fps, lambda: recording))
    record_thread.start()

    try:
        action = automated_actions.generate_steps()
    finally:
        recording = False
        record_thread.join()
        out.release()
    logger.info(f"end...") 

def record_screen(out, fps, is_recording):
    while is_recording():
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        x, y = pyautogui.position()

        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1) 

        out.write(frame)
        time.sleep(1 / fps)


if __name__ == "__main__": 
    run()




