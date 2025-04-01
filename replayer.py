from utils.logger_setup_data_extraction import logger
from replay_agent.planner.snapshot_analyzer import SnapshotAnalyzer
from replay_agent.position_finder.position_extractor import PositionExtractor


def run():
    logger.info(f"started...")    
    
    # Step 1: Screen Snapshot and analyst in knowledge base (Error Handing)
    logger.info(f"\nstarted ScreenSnapshotAnalyzer...") 
    snapshot_analyzer = SnapshotAnalyzer()
    action = snapshot_analyzer.generate_action()

    # position_extractor = PositionExtractor()
    # position_extractor.get_position_by_name("input\\screenshot\\screenshot.png","cell row 2, column A")

    # Step 2: Action parser and take action
    # Step 3: Validation Success (Error Handing)
    # Step 4: Still in current screen? 

    logger.info(f"end...") 


if __name__ == "__main__": 
    run()




