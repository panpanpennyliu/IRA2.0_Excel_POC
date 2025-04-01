import json
import re
from utils.logger_setup_data_extraction import logger

def json_process(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            data = json.loads(json_str)
            # print(data)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return
    else:
        logger.error("No valid JSON content was found")
        return