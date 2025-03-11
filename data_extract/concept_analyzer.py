import os,sys
import base64
from prompt.generate_concept_data import *

from core.llm_chat import LLMChat
from core.planner import Planner
from core.context_manager import ContextManager
from core.context_manager_map import ContextManagerMap

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
        logger.info(f"video folder: {frame_folder_path}") 

        for i, (subdir, _, files) in enumerate(os.walk(frame_folder_path)):
            #break
            if i == 0:
                continue
            logger.info(f"sub-folder: {subdir}")
            video_folder = os.path.basename(subdir)
            logger.info(f"video-id: {video_folder}")

            context_manager_video = ContextManager()
            context_manager_state_trans = ContextManagerMap()
            context_manager_2_frames = ContextManagerMap()
            pre_frame_context = ""

            for frame_index, file in enumerate(files):
                logger.info(f"frame file name: {file}")
                frame_file_path = os.path.join(subdir, file)
                logger.info(f"frame file path: {frame_file_path}")

                file_name = os.path.splitext(file)[0]
                file_name = file_name.replace('____', '|')
                last_underscore_index = file_name.rfind('_')
                if last_underscore_index != -1:
                    frame_file_name = file_name[:last_underscore_index] + '|' + file_name[last_underscore_index + 1:]
                else:
                    frame_file_name = file_name
                print(frame_file_name)               


                # make plan steps for each frame
                request = GENERATE_CONCEPT_JSON_REQUEST
                background = GENERATE_CONCEPT_JSON_BACKGROUND
                knowledge = GENERATE_CONCEPT_JSON_KNOWLEDGE.format(frame_file_name=frame_file_name, video_folder=video_folder)

                logger.info(f"Planner input:\n request:\n {request},\n background:\n {background},\n knowledge:\n {knowledge}")

                planner = Planner(self.chat)
                steps = planner.plan(request, background=background, knowledge=knowledge)

                # process each step planned        
                context_manager_frame = ContextManager()                             
                for index, step in enumerate(steps, start=1):
                    #if index > 1:
                        #continue
                    logger.info(f"Step {index}")
                    if step.process_type == "text":
                        response = self.chat.prompt_respond(step.description, step.model_name)
                    elif step.process_type == "image":
                        response = self.chat.image_respond(frame_file_path, step.description, step.model_name)
                    
                    context = f"{response}"
                    context_manager_frame.add_context(context) 

                    # generate step description based on extracted picture info
                    if index == 1:
                        context_response = self.chat.context_respond_default(context_manager_frame.context_to_str(), GENERATE_ACTION_DESCRIPTION_REQUEST)                
                        context = context_response['answer'].replace("```json", '').replace("```", '')
                        logger.info(f"response answer for step description:\n {context}")
                        logger.info("=========AAAAAA===============")
                        context_manager_frame.add_context(context)              


                # extract state transition information based on frames comparision             
                context_manager_2_frames.add_context("pre_frame", pre_frame_context)
                context_manager_2_frames.add_context("cur_frame", context_manager_frame.context_to_str())
                pre_frame_context = context_manager_frame.context_to_str()

                context_manager_2_frames.print_context()
                logger.info("===========BBBBBB=============")

                context_response = self.chat.context_respond_default(context_manager_2_frames.context_to_str(), GENERATE_STATE_TRANSITION_REQUEST)                
                context = context_response['answer'].replace("```json", '').replace("```", '')
                logger.info(f"response answer for extract state transition:\n {context}")
                logger.info("=========CCCCCC===============")
                context_manager_frame.add_context(context) 

                # save state transition for each step
                context_manager_state_trans.add_context(f"step_{frame_index}", context)                           

                
                # compile all json attributes for current frame                
                context_response = self.chat.context_respond_default(context_manager_frame.context_to_str(), COMPILE_FRAME_JSON_REQUEST)                
                context = context_response['answer'].replace("```json", '').replace("```", '')
                logger.info(f"response answer for compile frame json:\n {context}")
                logger.info("=========DDDDDD===============")               

                context_manager_frames.add_context(context) 
                
            '''
            
            #sys.exit(0)
            # generate video id
            response = self.chat.prompt_respond_default(COMPILE_VIDEO_ID_REQUEST.format(video_folder=video_folder))
            logger.info(f"response for video id:\n {response}")
            logger.info("=========EEEEEE===============")
            context_manager_video.add_context(response) 

            # generate business flow based on state_trans context
            context_response = self.chat.context_respond_default(context_manager_state_trans.context_to_str(), GENERATE_BUSINESS_FLOW_REQUEST)
            context = context_response['answer'].replace("```json", '').replace("```", '')
            logger.info(f"response answer for summerize business flow:\n {context}")
            logger.info("=========EEEEEE===============")
            context_manager_video.add_context(context) 

            # compile all frames for one video to one json              
            context_response = self.chat.context_respond_default(context_manager_frame.context_to_str(), COMPILE_FRAME_JSON_REQUEST)                
            context = context_response['answer'].replace("```json", '').replace("```", '')
            logger.info(f"response answer for compile frame json:\n {context}")
            logger.info("=========DDDDDD===============")
            context_manager_frames.add_context(context) 

            # merge video id, frames info, business flow

            '''


        #sys.exit(0)
        context_manager_frames.print_context()
        logger.info("=========EEEEEE===============")

        ''' '''

        # compile json for all frames        
        context_response = self.chat.context_respond_default(context_manager_frames.context_to_str(), COMPILE_CONCEPT_JSON_REQUEST)
        context = context_response['answer'].replace("```json", '').replace("```", '')
        logger.info(f"response answer for compile concept json:\n {context}")
        logger.info("=========FFFFFF===============")

       

        return context_manager_frames
