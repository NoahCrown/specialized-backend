import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain.callbacks.manager import get_openai_callback

class ImprovedOutput(BaseModel):
    JobDescription: str = Field(..., description="Improved job description based on comprehensive analysis")
    AnalysisSummary: str = Field(..., description="Detailed summary of comparative and gap analysis with key insights")
    Improvements: List[str] = Field(..., description="List of specific improvements made to the job description")

def improve_prompt(ai_payload, job_description, parser=ImprovedOutput):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

    load_data = """
    <<SYS>>
    You are an expert AI assistant specializing in analyzing and improving job descriptions. Your task is to enhance AI-generated job descriptions by incorporating insights from human-refined versions and conducting comprehensive analysis.
    <<SYS>>

    [INST]
    Analyze the provided AI-generated job description and its human-refined counterpart. Your tasks:

    1. Conduct a thorough analysis comparing both versions and identifying gaps.
    2. Create an improved job description that combines the strengths of both versions.
    3. Provide a detailed summary of your analysis and improvements.

    Guidelines for improved job description:
    • Retain core information from the AI-generated output.
    • Adopt appropriate elements of tone, structure, and style from the human-refined version.
    • Ensure the improved version is comprehensive, professional, and aligned with industry standards.
    • Do not add information absent from both provided versions.
    • Maintain any original omissions (e.g., job location) from the AI version.
    • Use clear headings and subheadings to organize information.
    • Employ bullet points for responsibilities, qualifications, and benefits.
    • Ensure proper formatting is maintained in the output, including for lists and sections.

    For the analysis summary:
    • Provide a comprehensive comparison of structure, content, tone, and effectiveness.
    • Use bullet points to highlight key differences and improvements.
    • Explain technical concepts in layman's terms when necessary.
    • Identify specific areas where the human-refined version improved upon the AI-generated one.
    • Discuss any potential drawbacks or missed opportunities in either version.
    • Analyze the overall impact of the changes on the job description's effectiveness.
    • Use subheadings to organize different aspects of the analysis (e.g., "Content Analysis," "Structural Improvements," "Tone and Style").

    For the improvements list:
    • Provide a numbered list of specific, actionable improvements made to the job description.
    • Explain the rationale behind each improvement and its expected impact.

    Return a JSON object with the following structure:
    1. "JobDescription": The improved job description, maintaining proper formatting for lists and sections.
    2. "AnalysisSummary": Detailed summary of comparative and gap analysis, using bullet points and subheadings for clarity.
    3. "Improvements": Numbered list of specific improvements made, with brief explanations.

    Ensure all JSON keys and string values use double quotes. For multiline strings or lists, use appropriate JSON formatting to maintain readability.

    AI-Generated Output:
    {ai_payload}

    Human-Refined Version:
    {job_description}

    Format instructions:
    {format_instructions}

    Answer:
    [/INST]
    """

    query = load_data
    object_parser = JsonOutputParser(pydantic_object=parser)
    prompt = PromptTemplate(
        template=query,
        input_variables=["ai_payload", "job_description"],
        partial_variables={"format_instructions": object_parser.get_format_instructions()}
    )
    params = {"job_description": job_description, "ai_payload": ai_payload}
    llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
    llm_chain = prompt | llm | object_parser
    with get_openai_callback() as cb:
        response = llm_chain.invoke(params)
    return response
