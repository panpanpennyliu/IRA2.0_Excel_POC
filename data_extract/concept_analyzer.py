import os,sys
import base64
from prompt.generate_concept_json import GENERATE_CONCEPT_JSON_REQUEST
from prompt.generate_concept_json import GENERATE_CONCEPT_JSON_BACKGROUND
from prompt.generate_concept_json import GENERATE_CONCEPT_JSON_KNOWLEDGE
from prompt.generate_concept_json import COMPILE_FRAME_JSON_REQUEST
from prompt.generate_concept_json import COMPILE_CONCEPT_JSON_REQUEST
from prompt.generate_concept_json import GENERATE_STATE_TRANSITION_REQUEST

from core.llm_chat import LLMChat
from core.planner import Planner
from core.context_manager import ContextManager
from core.context_manager_map import ContextManagerMap

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.logger_setup_data_extraction import logger
from prompt.system_context import SYSTEM_CONTEXT, SYSTEM_CONTEXT_WITH_TOOLS
from langchain.chat_models import init_chat_model
from utils.logger_setup_data_extraction import logger


class ConceptAnalyzer:
    def __init__(self):      
        self.chat = LLMChat() 
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def generate_concept_data(self):
        context_manager_frames = ContextManager()          

        # process all the frames for one business process
        frame_folder_path = os.path.join('input', 'pickFrame')
        #frame_folder_path = r'D:\temp\Penny\AI\PycharmProjects\git\IRA2.0_Excel_POC\input\pickFrame'
        logger.info(f"frame folder: {frame_folder_path}") 

        for subdir, _, files in os.walk(frame_folder_path):
            logger.info(f"sub-folder: {subdir}")

            context_manager_2_frames = ContextManagerMap()
            pre_frame_context = ""

            for file in files:
                #current_file_directory = os.path.dirname(os.path.abspath(__file__))
                #frames_folder_path = os.path.join(current_file_directory, '..', 'input', 'pickFrame')
                #frames_folder_path = os.path.normpath(frames_folder_path)
                frame_image = os.path.join(subdir, file)
                logger.info(f"image path: {frame_image}")


                # make plan steps for each frame
                
                #sys.exit(0)
                request = GENERATE_CONCEPT_JSON_REQUEST
                background = GENERATE_CONCEPT_JSON_BACKGROUND
                knowledge = GENERATE_CONCEPT_JSON_KNOWLEDGE.format(frame_image=frame_image)

                logger.info(f"Planner input:\n request:\n {request},\n background:\n {background},\n knowledge:\n {knowledge}")

                planner = Planner(self.chat)
                steps = planner.plan(request, background=background, knowledge=knowledge)

                # process each step planned        
                context_manager_frame = ContextManager()                             
                for index, step in enumerate(steps, start=1):
                    #if index < 3:
                        #continue
                    logger.info(f"Step {index}")
                    if step.process_type == "text":
                        response = self.chat.prompt_respond(step.description, step.model_name)
                    elif step.process_type == "image":
                        response = self.chat.image_respond(frame_image, step.description, step.model_name)
                    
                    context = f"{response}"
                    context_manager_frame.add_context(context)               
                
                # extract state transition information based on frames comparision             
                context_manager_2_frames.add_context("pre_frame", pre_frame_context)
                context_manager_2_frames.add_context("cur_frame", context_manager_frame.context_to_str())
                pre_frame_context = context_manager_frame.context_to_str()

                context_manager_2_frames.print_context()
                logger.info("===========AAAAAA=============")

                context_response = self.chat.context_respond_default(context_manager_2_frames.context_to_str(), GENERATE_STATE_TRANSITION_REQUEST)                
                context = context_response['answer'].replace("```json", '').replace("```", '')
                logger.info(f"response answer for extract state transition:\n {context}")
                logger.info("=========BBBBBB===============")
                context_manager_frame.add_context(context)                 
              
                # compile json for current frame                
                context_response = self.chat.context_respond_default(context_manager_frame.context_to_str(), COMPILE_FRAME_JSON_REQUEST)                
                context = context_response['answer'].replace("```json", '').replace("```", '')
                logger.info(f"response answer for compile frame json:\n {context}")
                logger.info("=========CCCCCC===============")
                

                context_manager_frames.add_context(context) 

        #sys.exit(0)
        # compile json for all frames        
        context_response = self.chat.context_respond_default(context_manager_frames.context_to_str(), COMPILE_CONCEPT_JSON_REQUEST)
        context = context_response['answer'].replace("```json", '').replace("```", '')
        logger.info(f"response answer for compile concept json:\n {context}")
        logger.info("=========DDDDDD===============")

        return context
    
        # TODO: validate the response
        
