
import json, re

from core.llm_chat import LLMChat
from core.step_manager import Step

from prompt.plan import PLAN_FORMAT
from utils.logger_setup_data_extraction import logger

class Planner:

    def __init__(self, llm_chat):
        self.steps = []
        self.chat = llm_chat

    def plan(self, request, **kwargs):

        plan_content = ""
        background = ""
        if 'background' in kwargs:
            background = kwargs['background']
        plan_content += f"<background>\n{background}\n</background>\n"
        knowledge = ""
        if 'knowledge' in kwargs:
            knowledge = kwargs['knowledge']
        plan_content += f"<knowledge>\n{knowledge}\n</knowledge>\n"
        plan_content += PLAN_FORMAT
        
        response = self.chat.prompt_respond_default(request, plan_content).replace("```json", '').replace("```", '')
        logger.info(f"Planner response:\n {response}")
        
        steps_data = json.loads(response)["steps"]
        for step_data in steps_data:
            step = Step(step_data["step_name"], step_data["step_description"], step_data["model_name"], step_data["process_type"])
            self.steps.append(step)
        return self.steps
    
    def extract_steps(plan_string):
        # Define an empty list to store the steps
        steps = []
        # Extracting step descriptions
        steps = re.findall(r"\d+\.\s(.*?)(?=\n\d+\.\s|\Z)", plan_string, re.DOTALL)
        return steps
