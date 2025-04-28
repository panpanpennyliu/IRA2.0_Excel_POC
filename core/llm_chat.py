import os,sys
import dotenv
import base64
import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.logger.logger_setup_data_extraction import logger
from prompt.system_context import SYSTEM_CONTEXT, SYSTEM_CONTEXT_WITH_TOOLS
from utils.logger.logger_setup_data_extraction import logger
from openai import OpenAI
from PIL import Image
from google import genai

dotenv.load_dotenv(os.path.join('config', '.env'))

class LLMChat: 
    def __init__(self):
        model_name = os.getenv("DEFAULTM_MODEL")
        self.chat = ChatOpenAI(model=model_name, temperature=0.1, verbose=True) 
    
    def prompt_respond_default(self, request, system_prompt):               
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )    

        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        response = chain.invoke(
            {
                "messages": [
                    HumanMessage(content=request),
                ],
            }
        )
        return response    
    
    def prompt_respond(self, request, model_name): 
        self.chat = ChatOpenAI(model=model_name, temperature=0.1, verbose=True)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    #"You are a helpful assistant. Answer all questions to the best of your ability.",
                    "You are a helpful assistant. Put each response in the json format as the output",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ) 

        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        response = chain.invoke(
            {
                "messages": [
                    HumanMessage(content=request),
                ],
            }
        ).replace("```json", '').replace("```", '')

        logger.info(f"prompt_respond:\n {response}") 
        return response  
    
    def context_respond_default(self, context_str, messages_str):
        logger.info("#################################")
        logger.info(f"context_str:\n {context_str}")
        logger.info(f"messages_str:\n {messages_str}")
        logger.info("#################################")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_CONTEXT,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        context_chain = create_stuff_documents_chain(self.chat, prompt)
        docs = [Document(context_str)]        
        context_entity = lambda data: self._convert(data, docs)
        messages = [messages_str]
        retrieval_chain = RunnablePassthrough.assign(
            context=context_entity,
        ).assign(
            answer=context_chain,
        )
        response = retrieval_chain.invoke(
            {
                "messages": messages,
            }
        )
        #print("context_respond_default response: \n")
        #print(response)
        #print("===============")
        return response
        
    def context_respond(self, context_str, messages_str, model_name):
        logger.info("#################################")
        logger.info(f"context_str:\n {context_str}")
        logger.info(f"messages_str:\n {messages_str}")
        logger.info("#################################")

        self.chat = ChatOpenAI(model=model_name, temperature=0.1, verbose=True)
        
        print("====================================\n\n")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_CONTEXT,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        context_chain = create_stuff_documents_chain(self.chat, prompt)
        docs = [Document(context_str)]
        context_entity = lambda data: self._convert(data, docs)
        messages = [messages_str]
        retrieval_chain = RunnablePassthrough.assign(
            context=context_entity,
        ).assign(
            answer=context_chain,
        )
        response = retrieval_chain.invoke(
            {
                "messages": messages,
            }
        )
        #print("context_respond response: \n")
        #print(response)
        #print("===============")
        return response    

    def _convert(self, data: Dict[str, Any], docs: str):
        return docs
    
    def _validate_arguments(self, input_args, arg_definition):
        if len(arg_definition) != 0:
            for key, value in arg_definition.items():
                if key not in input_args:
                    return False
        else:
            if input_args:
                return False
        return True
    
    def encode_image(self,image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    def image_respond(self, image_path, request, model_name):
        #self.logger.info('[process image]')

        #base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        #full_image_path = os.path.join(base_dir, image_path)

        #self.logger.info('image_path: %s', full_image_path)
        #self.logger.info('prompt: %s', prompt)

        self.chat = ChatOpenAI(model=model_name, temperature=0.1, verbose=True)  

        result = ""
        try:
            base64_image = self.encode_image(image_path)
        except Exception as e:
                result = "Running Error"
                self.logger.error('Exception: \n %s \n', e) 
        
        if result != "Running Error":
            for attempt in range(5): #retry up to 5 times
                try:
                    prompt = ChatPromptTemplate.from_messages(
                        [
                            (
                                "system",
                                "You are a helpful assistant. Put each response in the json format as the output",
                            ),
                            MessagesPlaceholder(variable_name="messages"),
                        ]
                    )
                    output_parser = StrOutputParser()
                    chain = prompt | self.chat | output_parser

                    message = HumanMessage(  
                        content=[  
                            {"type": "text", "text": request},  
                            {  
                                "type": "image_url",  
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},  
                            },  
                        ],  
                    )  

                    response = chain.invoke(
                        {
                            "messages": [message],
                        }
                    ).replace("```json", '').replace("```", '')
                    
                    logger.info(f"image_response:\n {response}") 
                    result = response               

                    break

                except Exception as e:
                    result = "Running Error"
                    sleep_time = 2 ** attempt
                    logger.error(f"Exception: {e}")
                    logger.info(f"Retrying in {sleep_time} seconds" )
                    time.sleep(sleep_time)
        return result   
    
    def image_respond_gemini(self, image_path, request, model_name):
        prompt = "You are a helpful assistant. Put each response in the json format as the output"
        request = prompt + request
        result = ""
        try:
            base64_image = self.encode_image(image_path)
        except Exception as e:
                result = "Running Error"
                self.logger.error('Exception: \n %s \n', e) 
        
        if result != "Running Error":
            for attempt in range(5): #retry up to 5 times
                try:
                    self.openai_model = OpenAI(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url=os.getenv("OPENAI_API_BASE")
                    )

                    response = self.openai_model.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": request},
                                {"type": "image_url", "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"}
                                }
                            ]}
                        ],
                        temperature=0.0,
                    )
                    
                    result = response.choices[0].message.content    
                    logger.info(f"image_response:\n {result}")             
                    break

                except Exception as e:
                    result = "Running Error"
                    sleep_time = 2 ** attempt
                    logger.error(f"Exception: {e}")
                    logger.info(f"Retrying in {sleep_time} seconds" )
                    time.sleep(sleep_time)
        return result 
    
    def image_respond_gemini_google(self, image_path, request, model_name):
        result = ""
        
        if result != "Running Error":
            for attempt in range(5): #retry up to 5 times
                try:
                    image = Image.open(image_path)
                    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your API key
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[image, request]
                    )  

                    logger.info(f"image_response:\n {response}")  

                    result = response.candidates[0].content.parts[0].text          
                    break

                except Exception as e:
                    result = "Running Error"
                    sleep_time = 2 ** attempt
                    logger.error(f"Exception: {e}")
                    logger.info(f"Retrying in {sleep_time} seconds" )
                    time.sleep(sleep_time)
        return result 