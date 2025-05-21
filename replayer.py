from utils.logger.logger_setup_data_extraction import logger
from replay_agent.planner.automated_actions import AutomatedActions
from datetime import datetime
import os
import shutil


def run():
    logger.info(f"started...")    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...") 
    current_time_str = datetime.now().strftime('%m%d%H%M%S')
    image_folder_path = os.path.join("log", "screenshot", current_time_str)
    os.makedirs(image_folder_path)
    shutil.copy("output\\knowledge_flow.json", image_folder_path)

    automated_actions = AutomatedActions(image_folder_path)
    action = automated_actions.generate_steps()



    logger.info(f"end...") 


if __name__ == "__main__": 
    run()




