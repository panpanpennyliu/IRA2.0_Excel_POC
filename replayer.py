from utils.logger_setup_data_extraction import logger
from replay_agent.planner.snapshot_analyzer import SnapshotAnalyzer
from replay_agent.position_finder.position_extractor import PositionExtractor
from datetime import datetime
import os



def run():
    logger.info(f"started...")    
    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...") 
    current_time_str = datetime.now().strftime('%m%d%H%M%S')
    image_folder_path = os.path.join("input", "screenshot", current_time_str)
    os.makedirs(image_folder_path)
    # snapshot_analyzer = SnapshotAnalyzer(image_folder_path)
    # action = snapshot_analyzer.generate_action()

    position_extractor = PositionExtractor()
    position_extractor.get_position_by_name(image_folder_path, "input\\screenshot\\screenshot.png","Formula Bar","input_box")

    # Step 2: Action parser and take action
    # Step 3: Validation Success (Error Handing)
    # Step 4: Still in current screen? 

    logger.info(f"end...") 


if __name__ == "__main__": 
    run()




