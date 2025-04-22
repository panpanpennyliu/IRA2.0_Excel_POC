from utils.logger.logger_setup_data_extraction import logger
from replay_agent.planner.automated_actions import AutomatedActions
from replay_agent.position_finder.position_extractor import PositionExtractor
from datetime import datetime
import os



def run():
    logger.info(f"started...")    
    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...") 
    current_time_str = datetime.now().strftime('%m%d%H%M%S')
    image_folder_path = os.path.join("log", "screenshot", current_time_str)
    os.makedirs(image_folder_path)
    automated_actions = AutomatedActions(image_folder_path)
    action = automated_actions.generate_steps()

    # position_extractor = PositionExtractor()
    # position_extractor.get_position_by_name(image_folder_path, "log\\screenshot\\screenshot.png","Sheet1","text_button")

    # Step 2: Action parser and take action
    # Step 3: Validation Success (Error Handing)
    # Step 4: Still in current screen? 

    logger.info(f"end...") 


if __name__ == "__main__": 
    run()




