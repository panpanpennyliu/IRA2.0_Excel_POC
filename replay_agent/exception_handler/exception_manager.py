from utils.logger.logger_setup_data_extraction import logger
from replay_agent.action_executor.action_perform import ActionExecutor
import os
import json
from prompt.app_instruction import INSTRUCTIONS
from prompt.exception_handle import ASK_FOR_HELP
from replay_agent.position_finder.ocr_position import OcrPosition
from prompt.exception_handle import PLAN_FOR_EXCEPTION

import tkinter as tk
from tkinter import messagebox
import shutil

from core.llm_chat import LLMChat
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate

import pyautogui
from replay_agent.screenshot_processor.screenshot_capture import ScreenshotCapture
import threading


class ExceptionManager:
    def __init__(self):
        self.chat = LLMChat()
        self.executor = ActionExecutor()
        self.isApply = True

    def perform_action(self, action):
        # Logic to perform action based on exception type
        logger.info(f"Performing action: {action}")
        self.executor.execute_action(action)
        
    def plan_for_exception(self,exception_description, step_description, next_step_description, image_path):
        if step_description is None or step_description == "":
            logger.error("Step description is None")
            return
        if image_path is None or image_path == "":
            logger.error("Image path is None")
            return
        
        logger.info(f"Plan Actions to Handle Exception: {step_description}")
        response_schemas = [
            ResponseSchema(name="ExceptionDescription", description="Description of the exception"),
            ResponseSchema(name="ActionDescription", description="Description of the action"),
            ResponseSchema(name="ActionSteps", description="Actions to handle the exception", type="string array")
        ]  
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        response_format = output_parser.get_format_instructions()
        partial_prompt = PromptTemplate(
            template=PLAN_FOR_EXCEPTION,
            partial_variables={"response_format": response_format}
        )
        prompt = partial_prompt.format(exception_description=exception_description, step_description=step_description, instructions="")
        logger.info(f"Prompt: {prompt}")
        try:
            # ai_model = GenAIModel()
            # response = ai_model.process_image(output_path, prompt)
            response = self.chat.image_respond(image_path, prompt, os.getenv("MODEL_PLAN_FOR_EXCEPTION"))
        except Exception as e:
            logger.error(f"Error: {e}")
            return
        if response is None or response == "Running Error":
            return
        # logger.info(f"Response: {response}")
        json_response = json.loads(response)
        suggestion = json_response.get("ActionDescription")
        action_steps = json_response.get("ActionSteps")
        # send email to the team to ask for help
        logger.info(f"Sending email for help: {suggestion}")
        steps_dict = {str(index + 1): step for index, step in enumerate(action_steps)}

        steps_json = json.dumps(steps_dict, indent=4)
        
        folder_path = os.path.dirname(image_path)
        screenshot_capture = ScreenshotCapture(folder_path)
        ask_for_help_path= os.path.basename(image_path).replace("screenshot_", "ask_for_help_")
        screenshot_thread = threading.Thread(target=screenshot_capture.get_screen_snapshot, args=(ask_for_help_path,))
        screenshot_thread.start()

        self.ask_for_help(exception_description, steps_json)

        screenshot_thread.join()        

        if self.isApply:
            return steps_json
        else:
            logger.info("User choose to handle exception manually")
            ask_for_help_path= os.path.basename(image_path).replace("screenshot_", "ask_for_help_manual_")
            screenshot_thread = threading.Thread(target=screenshot_capture.get_screen_snapshot, args=(ask_for_help_path,))
            screenshot_thread.start()
            self.manual_window(step_description)
            screenshot_thread.join() 
            return None

    def ask_for_help(self, exception, action_steps):
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        popup = tk.Toplevel()
        popup.attributes("-topmost", True)
        popup.title("Exception Handling")

        # 设置内边距
        popup_frame = tk.Frame(popup, padx=60, pady=60)
        popup_frame.pack(fill=tk.BOTH, expand=True)
        label_text = f"AI recommends the following actions for exception handling.\nException description:\n {exception}\nActions:\n {action_steps}\n\nPlease choose whether to apply the recommended actions or manually handle the exception."
        prompt_label = tk.Label(popup_frame, text=label_text, justify="left")
        prompt_label.pack(pady=30)

        button_frame = tk.Frame(popup_frame)
        button_frame.pack(pady=30)

        continue_button = tk.Button(button_frame, text="Apply actions",
                                    command=lambda: self.apply_case(popup, root))
        continue_button.pack(side=tk.LEFT, padx=10)

        stop_button = tk.Button(button_frame, text="Handle exception manually",
                                command=lambda: self.manual_case(popup, root))
        stop_button.pack(side=tk.LEFT, padx=10)

        popup.protocol("WM_DELETE_WINDOW", lambda: self.manual_case(popup, root))
        root.mainloop()


    def apply_case(self, popup, root):
        self.isApply = True
        popup.destroy()
        root.destroy()

    def manual_case(self, popup, root):
        self.isApply = False
        popup.destroy()
        root.destroy()

    def stop_case(self, popup, root):
        popup.destroy()
        root.destroy()

    def manual_window(self, step_description):
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        popup = tk.Toplevel()
        popup.attributes("-topmost", True)
        popup.title("Ask for help")
        label = tk.Label(popup, text=f" Please help execute below action manually:\n {step_description}", justify="left")
        label.pack()
        ok_button = tk.Button(popup, text="Ready for next action", command=lambda: self.stop_case(popup, root))
        ok_button.pack(pady=10)
        popup.protocol("WM_DELETE_WINDOW", lambda: self.stop_case(popup, root))
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        popup.update_idletasks()
        window_width = popup.winfo_width()
        window_height = popup.winfo_height()

        x = screen_width - window_width - 20
        y = screen_height - window_height - 150
        popup.geometry(f"+{x}+{y}")
        root.mainloop()


    def copy_and_rename_file(self, source_file, destination_folder, new_name):
        try:
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            destination_file = os.path.join(destination_folder, new_name)
            shutil.copy2(source_file, destination_file)
        except FileNotFoundError:
            print(f"Error: source file {source_file} not found")
        except Exception as e:
            print(f"Unknown exception while copying file: {e}")