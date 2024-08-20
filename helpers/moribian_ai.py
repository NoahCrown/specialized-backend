import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Union
from dotenv import load_dotenv
from langchain.callbacks.manager import get_openai_callback



class ImprovedOutput(BaseModel):
    JobDescription: str = Field(..., description="The better output based on the gap analysis on the AI Generated Output and the Manual Intervention of the output")
    Changes: str = Field(..., description="The changes made from the given prompt such as tone, structure, and etc...")


def improve_prompt(ai_payload, job_description, parser = ImprovedOutput):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

    load_data = """
    <<SYS>>
    You are a bot who is a professional at improving the job description based on the gap analysis of the Ai generated and Human generated Job description. 
    <<SYS>>

    [INST]
    You are provided with jobspec data from a ai output and a human polished output, your goal is to improve the ai output so it follows how the human polished output is structured, toned, and etc.
    Then you are to provide a gap analysis on those two on what differentiate then if it is the tone, structure, etc...

    If there are a missing data such as location of the job, ignore it and don't copy it. Only Include the datas that are located within the ai prompt

    Remember, do not entirely copy the Human Polished Output, only follow the tone, structure, and intonation.
    For the changes explanation, keep it short and simple.


    Return it as a JSON object, all keys and string values needs to be enclosed in double quotes.
    
    AI Output: 
    {ai_payload}

    Human Polished Output: 
    {job_description}

    Format instructions:
    {format_instructions}

    Answer:
    [/INST]
    
"""
    query = load_data
    object_parser = JsonOutputParser(pydantic_object=parser)
    prompt = PromptTemplate(template=query, input_variables=["custom_prompt","candidate_data"],partial_variables={"format_instructions": object_parser.get_format_instructions()})
    params = {"job_description":job_description, "ai_payload": ai_payload}
    llm = ChatOpenAI(model = "gpt-4-0125-preview", temperature= 0)
    llm_chain = prompt | llm | object_parser
    with get_openai_callback() as cb:
        response = llm_chain.invoke(params)
        # logger.info(cb)
    return response
