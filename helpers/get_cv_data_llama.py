import os
from concurrent.futures import ThreadPoolExecutor
from langchain_community.llms.deepinfra import DeepInfra
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, EmailStr
from typing import List, Optional
from dotenv import load_dotenv
import fitz
import json
from PyPDF2 import PdfReader
from langdetect import detect

class SkillData(BaseModel):
    data: List[str] = Field(description="List of skills")
    total: int = Field(description="Total number of skills")

class Candidate(BaseModel):
    certifications: str = Field(description="Certifications held by the candidate")
    comments: Optional[str] = Field(description="General comments or notes about the candidate")
    dateOfBirth: Optional[str] = Field(description="Candidate's date of birth")
    educationDegree: str = Field(description="Highest educational degree obtained by the candidate")
    email: str = Field(description="Candidate's email address")
    ethnicity: Optional[str] = Field(description="Candidate's self-reported ethnicity (optional)")
    firstName: str = Field(description="Candidate's first name")
    lastName: str = Field(description="Candidate's last name")
    phone: str = Field(description="Candidate's contact phone number")
    primarySkills: SkillData = Field(description="Primary skills or competencies of the candidate")
    secondarySkills: SkillData = Field(description="Secondary skills or competencies of the candidate")
    skillSet: SkillData = Field(description="Comprehensive list of the candidate's skills")
    specialties: SkillData = Field(description="Areas of specialty or expertise for the candidate")

class WorkExperience(BaseModel):
    comments: str = Field(description="Summarized description or remarks about the work experience")
    companyName: str = Field(description="Name of the company associated with the work experience")
    endDate: int = Field(description="End date of the work experience, represented as an epoch timestamp")
    isLastJob: bool = Field(description="Indicates whether this position was the candidate's most recent job")
    startDate: str = Field(description="Start date of the work experience, can be a specific date or period")
    title: str = Field(description="Job title or position held during this work experience")

class CandidateWorkHistory(BaseModel):
    workHistory: List[WorkExperience] = Field(description="A list detailing the work experiences or work history of the individual")

def get_workhistory_from_text(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.split_text(text)
    response = ""
    for text in texts:
        response = str(response)
        query = """
        <<SYS>>
        You are a bot who is professional at extracting candidate data from a candidate's resume.
        <<SYS>>
        [INST]
        This is a CV containing candidate's information: {text}
        Give me the whole work history of the candidate. Please DO NOT summarize and give the exact details of each work experience.
        If there are no value for the needed data, just put None.
        This is the data the that I need:
        - Description or remarks about the work experience
        - Name of the company associated with the work experience
        - End date of the work experience
        - Start date of the work experience
        - Indicates whether this position was the candidate's most recent job
        - Job title or position held during this work experience
        
        Answer:
        {response}
        [/INST]
        """
        prompt = PromptTemplate(template=query, input_variables=["text","response"])
        llm = DeepInfra(model_id = "meta-llama/Llama-2-70b-chat-hf", verbose=True)
        llm.model_kwargs = {
            "temperature": 0,
            "max_tokens":10000000
        }
        chain = prompt | llm
        response = chain.invoke({"text": text, "response": response})
    return response

def run_llama_candidate(query,text,parser):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.split_text(text)
    response_candidate= ""
    for text in texts:
        response_candidate = str(response_candidate)
        prompt = PromptTemplate(template=query, input_variables=["text", "response"], partial_variables={"format_instructions": parser.get_format_instructions()})
        llm = DeepInfra(model_id = "meta-llama/Llama-2-70b-chat-hf", verbose=True)
        llm.model_kwargs = {
            "temperature": 0,
            "max_tokens":10000000
        }
        llm_chain = prompt | llm | parser
        response_candidate = llm_chain.invoke({"text": text, "response": response_candidate})
        # response = parse_json_with_autofix(response)
        print(response_candidate)
    return response_candidate

def extract_cv(pdf_file):
    load_dotenv()
    os.environ["DEEPINFRA_API_TOKEN"] = os.getenv('DEEPINFRA_API_TOKEN')
    # pdf_reader = PdfReader(pdf_file)
    # text = ""

    # for page in pdf_reader.pages:
    #     text += page.extract_text()
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    lang = detect(text)

    init_query_translation = '' if lang == 'en' else f'Suppose you are a {lang} to English translator and the document is in {lang} texts, can you translate it so that you can extract the data and read it without giving me an output of translated texts and then'

    candidate_query = """
        <<SYS>>
        You are a bot who is professional at extracting candidate data from a candidate's resume.
        <<SYS>>
        [INST]
        This is a CV containing candidate's information: {text}

        Question:
        Please provide the candidate's profile as a JSON object. If a value is not mentioned, put null.
        
        Format instructions:
        {format_instructions}
        Answer:
        {response}
        [/INST]
    """

    query = init_query_translation + candidate_query
    candidate_parser = JsonOutputParser(pydantic_object=Candidate)

    summarized_text = get_workhistory_from_text(text)

    workhistory_query = """
        <<SYS>>
        You are a bot who is professional at extracting candidate's data from a candidate's resume.
        <<SYS>>
        [INST]
        This is a summary of a candidate's work history and experience: {text}

        Question:
        Please provide the whole work history and experience of the candidate as a JSON object. If a value is not mentioned, put null.

        Format instructions:
        {format_instructions}
        Answer:
        {response}
        [/INST]

    """

    workhistory_query = init_query_translation + workhistory_query
    workhistory_parser = JsonOutputParser(pydantic_object=CandidateWorkHistory)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_task1 = executor.submit(run_llama_candidate, query, text, candidate_parser)
        future_task2 = executor.submit(run_llama_candidate, workhistory_query, summarized_text, workhistory_parser)
        
        result_task1 = future_task1.result()
        result_task2 = future_task2.result()
        
        response = [result_task1, result_task2]
        print(response)
        return response