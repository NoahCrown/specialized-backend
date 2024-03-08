import os
import json
from langchain_community.llms.deepinfra import DeepInfra
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Union
from dotenv import load_dotenv

class EnglishProficiency(BaseModel):
    Language: Literal["English"] = Field(default="English", description="The language is English.")
    enProficiency: Literal['None', 'Basic', 'Conversational', 'Business', 'Fluent', 'Native'] = Field(..., description="This field categorizes the candidate's English proficiency: 'None' indicates no knowledge; 'Basic' covers simple phrases and expressions; 'Conversational' involves everyday communication; 'Business' pertains that the candidate can use English in professional setting; 'Fluent' means the candidate is fluent in English language, has high proficiency and can use it better than Business level; and 'Native' represents a proficiency indistinguishable from that of a native speaker or they are born and raised in an English-speaking country.")
    confidence: int = Field(..., ge=1, le=5, description="AI's confidence in inferring the data, 1 being (Extremely low confidence), 2 being (Low confidence), 3 being (Confident), 4 being (High confidence), 5 being (Very Confident).")
    explanation: str = Field(..., description="Explanation about the inference on the language skill")

class JapaneseProficiency(BaseModel):
    Language: Literal["Japanese"] = Field(default="Japanese", description="The language is Japanese.")
    jpProficiency: Literal['None', 'Basic', 'Conversational', 'Business', 'Fluent', 'Native'] = Field(..., description="This field categorizes the candidate's Japanese proficiency: 'None' indicates no knowledge; 'Basic' covers simple phrases and expressions; 'Conversational' involves everyday communication; 'Business' pertains that the candidate can use Japanese in professional setting; 'Fluent' means the candidate is fluent in Japanese language, has high proficiency and can use it better than Business level; and 'Native' represents a proficiency indistinguishable from that of a native speaker or they are born and raised in Japan.")
    confidence: int = Field(..., ge=1, le=5, description="AI's confidence in inferring the data, 1 being (Extremely low confidence), 2 being (Low confidence), 3 being (Confident), 4 being (High confidence), 5 being (Very Confident).")
    explanation: str = Field(..., description="Explanation about the inference on the language skill")

class LanguageProficiency(BaseModel):
    languageSkills: List[Union[EnglishProficiency, JapaneseProficiency]] = Field(..., description="Inferred proficiency of the candidate in English and Japanese")

class AgeInference(BaseModel):
    Age: int = Field(..., description="Inferred age of the candidate")
    confidence: int = Field(..., ge=1, le=5, description="AI's confidence in inferring the data, 1 being (Extremely low confidence), 2 being (Low confidence), 3 being (Confident), 4 being (High confidence), 5 being (Very Confident)")
    explanation: str = Field(..., description="Explanation about the inference on the age of the candidate")

class LocationInference(BaseModel):
    Location: str = Field(..., description="Inferred current city and country of the candidate")
    confidence: int = Field(..., ge=1, le=5, description="AI's confidence in inferring the data, 1 being (Extremely low confidence), 2 being (Low confidence), 3 being (Confident), 4 being (High confidence), 5 being (Very Confident).")
    explanation: str = Field(..., description="Explanation about the inference on the current location of the candidate")

def language_skill(candidate_data, custom_prompt, parser = LanguageProficiency):
    load_dotenv()
    os.environ["DEEPINFRA_API_TOKEN"] = os.getenv('DEEPINFRA_API_TOKEN')
    if custom_prompt is None:
        custom_prompt = ""
    else:
        pass

    load_data = """
    <<SYS>>
    You are a bot who is professional at inferring a candidate's language proficiency in english and japanese based on the available data given to you.
    <<SYS>>

    [INST]
    {custom_prompt}
    
    Language Proficiency is ranked like this:
    1 (Lowest): None
    2 (Very Low): Basic
    3 (Low): Conversational
    4 (Intermediate): Business
    5 (High): Fluent
    6 (Very High): Native

    Return it as a JSON object

    Data: 
    {candidate_data}

    Format instructions:
    {format_instructions}

    Previous answer:
    {response}

    Answer:
    [/INST]
    
"""
    query = load_data
    candidate_data= str(candidate_data)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    data_list = text_splitter.split_text(candidate_data)
    response = ""
    for data in data_list:
        response = str(response)
        language_parser = JsonOutputParser(pydantic_object=parser)
        prompt = PromptTemplate(template=query, input_variables=["custom_prompt","candidate_data","response"],partial_variables={"format_instructions": language_parser.get_format_instructions()})
        params = {"candidate_data":data, "custom_prompt": custom_prompt, "response": response}
        llm = DeepInfra(model_id = "meta-llama/Llama-2-70b-chat-hf", verbose=True)
        llm.model_kwargs = {
            "temperature": 0
        }
        llm_chain = prompt | llm | language_parser
        response = llm_chain.invoke(params)
    return response

def infer_age(candidate_data, custom_prompt, current_date, parser = AgeInference):
    load_dotenv()
    os.environ["DEEPINFRA_API_TOKEN"] = os.getenv('DEEPINFRA_API_TOKEN')
    if custom_prompt is None:
        custom_prompt = ""
    else:
        pass

    load_data = """
    <<SYS>>
    You are a bot who is professional at inferring a candidate's age based on the available data given to you.
    <<SYS>>

    [INST]
    {custom_prompt}
    
    Return it as a JSON object.

    Data: 
    {candidate_data}

    Current Date: 
    {current_date}

    Format instructions:
    {format_instructions}

    Previous answer:
    {response}

    Answer:
    [/INST]

    """
    query = load_data
    candidate_data= str(candidate_data)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    data_list = text_splitter.split_text(candidate_data)
    response = ""
    for data in data_list:
        response = str(response)
        age_parser = JsonOutputParser(pydantic_object=parser)
        prompt = PromptTemplate(template=query, input_variables=["custom_prompt","candidate_data","current_date","response"],partial_variables={"format_instructions": age_parser.get_format_instructions()})
        params = {"candidate_data":data, "custom_prompt": custom_prompt, "current_date": current_date,"response": response}
        llm = DeepInfra(model_id = "meta-llama/Llama-2-70b-chat-hf", verbose=True)
        llm.model_kwargs = {
            "temperature": 0
        }
        llm_chain = prompt | llm | age_parser
        response = llm_chain.invoke(params)
    return response
    
def infer_location(candidate_data, custom_prompt, current_date, parser = LocationInference):
    load_dotenv()
    os.environ["DEEPINFRA_API_TOKEN"] = os.getenv('DEEPINFRA_API_TOKEN')
    if custom_prompt is None:
        custom_prompt = ""
    else:
        pass
    
    load_data = """
    <<SYS>>
    You are a bot who is professional at inferring a candidate's location based on the available data given to you.
    <<SYS>>

    [INST]
    {custom_prompt}
    Return it as a JSON object.

    Data: 
    {candidate_data}

    Current Date: 
    {current_date}

    Format instructions:
    {format_instructions}

    Previous answer:
    {response}

    Answer:
    [/INST]

    """
    query = load_data
    candidate_data= str(candidate_data)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    data_list = text_splitter.split_text(candidate_data)
    response = ""
    for data in data_list:
        response = str(response)
        location_parser = JsonOutputParser(pydantic_object=parser)
        prompt = PromptTemplate(template=query, input_variables=["custom_prompt","candidate_data","current_date","response"],partial_variables={"format_instructions": location_parser.get_format_instructions()})
        params = {"candidate_data":data, "custom_prompt": custom_prompt, "current_date": current_date,"response": response}
        llm = DeepInfra(model_id = "meta-llama/Llama-2-70b-chat-hf", verbose=True)
        llm.model_kwargs = {
            "temperature": 0
        }
        llm_chain = prompt | llm | location_parser
        response = llm_chain.invoke(params)
    return response
