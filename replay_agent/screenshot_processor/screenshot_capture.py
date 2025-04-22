from utils.logger.logger_setup_data_extraction import logger

import pyautogui
import os


class ScreenshotCapture:
    def __init__(self,image_folder_path):    
        self.image_folder_path = image_folder_path 

    def get_screen_snapshot(self, screenshot_name):
        try:
            logger.info(f"Start Screenshot.... ")
            screenshot = pyautogui.screenshot()
            file_path = os.path.join(self.image_folder_path, screenshot_name)
            screenshot.save(file_path)
            logger.info(f"Screenshot saved as {file_path}")
            return file_path
        except Exception as e:
            logger.info(f"Error when taking a screenshot of the current screen: {e}")
        return None
    