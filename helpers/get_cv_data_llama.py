import os
from concurrent.futures import ThreadPoolExecutor
from langchain_community.llms.deepinfra import DeepInfra
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
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
    certifications: List[str] = Field(description="Certifications held by the candidate")
    comments: Optional[str] = Field(description="General comments or notes about the candidate")
    dateOfBirth: Optional[int] = Field(description="Candidate's date of birth, represented as an millisecond epoch format")
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
    comments: str = Field(description="Full description or remarks about the work experience")
    companyName: str = Field(description="Name of the company associated with the work experience")
    endDate: int = Field(description="End date of the work experience, represented as an millisecond epoch format")
    isLastJob: bool = Field(description="Indicates whether this position was the candidate's most recent job")
    startDate: int = Field(description="Start date of the work experience, represented as an millisecond epoch format")
    title: str = Field(description="Job title or position held during this work experience")

class CandidateWorkHistory(BaseModel):
    workHistory: List[WorkExperience] = Field(description="A list detailing the work experiences or work history of the individual")

def get_workhistory_from_text(lang, text):
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
        [/INST]
        """
    prompt = PromptTemplate(template=query, input_variables=["text"])
    llm = ChatOpenAI(model = "gpt-4-0125-preview", temperature= 0)
    chain = LLMChain(prompt = prompt, llm = llm)
    response = chain.run({"text": text})
    return response

def run_llama_candidate(lang,query,text,parser):
    prompt = PromptTemplate(template=query, input_variables=["text"], partial_variables={"format_instructions": parser.get_format_instructions()})
    llm = ChatOpenAI(model = "gpt-4-0125-preview", temperature= 0)
    chain = prompt | llm | parser
    # llm_chain = prompt | llm | parser
    response_candidate = chain.invoke({"text": text})
    # response = parse_json_with_autofix(response)
    print(response_candidate)
    return response_candidate

def extract_cv(pdf_file):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
    # pdf_reader = PdfReader(pdf_file)
    # text = ""

    # for page in pdf_reader.pages:
    #     text += page.extract_text()
    doc = fitz.open(pdf_file)
    filtered_text = ""  # Initialize an empty string to store filtered text
    filter_sentence = "Evaluation Warning: The document was created with Spire.Doc for Python."
    # Iterate through each page of the PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load the current page
        text = page.get_text()  # Extract text from the current page
        
        # Split the text into sentences and filter out the specific sentence
        sentences = text.split('\n')  # Assuming each sentence is on a new line
        filtered_sentences = [sentence for sentence in sentences if filter_sentence not in sentence]
        
        # Join the filtered sentences back into a block of text
        filtered_page_text = '\n'.join(filtered_sentences)
        filtered_text += filtered_page_text + "\n"  # Append the filtered text of the current page with a newline
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
        [/INST]
    """

    query = init_query_translation + candidate_query
    candidate_parser = JsonOutputParser(pydantic_object=Candidate)

    # summarized_text = get_workhistory_from_text(lang,text)

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
        [/INST]

    """

    workhistory_query = init_query_translation + workhistory_query
    workhistory_parser = JsonOutputParser(pydantic_object=CandidateWorkHistory)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_task1 = executor.submit(run_llama_candidate, lang, query, text, candidate_parser)
        future_task2 = executor.submit(run_llama_candidate, lang, workhistory_query, text, workhistory_parser)
        
        result_task1 = future_task1.result()
        result_task2 = future_task2.result()
        
        response = [result_task1, result_task2]
        print(response)
        return response