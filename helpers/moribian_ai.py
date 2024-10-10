import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain.callbacks.manager import get_openai_callback

class ImprovedOutput(BaseModel):
    JobDescription: str = Field(..., description="Improved job description based on comprehensive analysis of AI-generated and human-refined versions")
    Changes: List[str] = Field(..., description="Numbered list of key changes and improvements made to the original AI output. Each change should be on a new line, properly indented, and include a line break after each item.")
    Analysis: str = Field(..., description="Detailed comparative and gap analysis between AI-generated and human-refined versions")

def improve_prompt(ai_payload, job_description, parser=ImprovedOutput):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

    load_data = """
    <<SYS>>
    You are an expert AI assistant specializing in analyzing and improving job descriptions. Your task is to enhance human-refined job descriptions by incorporating insights from AI-generated versions, making the content more effective and professional.
    <<SYS>>

    [INST]
    Analyze the provided human-refined job description and its AI-generated counterpart. Your tasks:

    1. Conduct a thorough analysis comparing both versions and identifying gaps.
    2. Create an improved job description that combines the strengths of both versions.
    3. Provide a numbered list of changes and improvements made.
    4. Perform a detailed comparative and gap analysis between the two versions.

    Guidelines:
    • Improve the AI output by adopting the tone, structure, and style of the human-refined version where appropriate.
    • Only include information present in the AI-generated version; do not add new data.
    • If certain details (e.g., job location) are missing in the AI version, do not include them.
    • Ensure the improved version is clear, concise, professional, and aligned with industry standards.
    • Use bullet points or numbered lists for clarity where appropriate, ensuring they are properly formatted in the output.
    • Make your analysis understandable to both technical and non-technical audiences.

    For the improved job description:
    • Organize information logically, using headings and subheadings where appropriate.
    • Use bullet points for listing responsibilities, qualifications, and benefits.
    • Ensure proper formatting is maintained in the output.

    For the analysis:
    • Provide a comprehensive comparison of structure, content, tone, and effectiveness.
    • Identify specific areas where the human-refined version improved upon the AI-generated one.
    • Discuss any potential drawbacks or missed opportunities in either version.
    • Analyze the overall impact of the changes on the job description's effectiveness.

    Return your response as a JSON object with the following structure:
    1. "JobDescription": The improved job description, maintaining proper formatting for lists and sections.
    2. "Changes": A numbered list of key changes and improvements made. Each change should be on a new line, properly indented, and include a line break after each item.
    3. "Analysis": A detailed comparative and gap analysis, highlighting main differences and areas of improvement. Use subheadings for clarity.

    Ensure all keys and string values in the JSON are enclosed in double quotes. For multiline strings or lists, use appropriate JSON formatting to maintain readability. Use "\\n" for line breaks within JSON strings to ensure proper formatting in the output.

    AI-generated Output:
    {ai_payload}

    Human-refined Output:
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
        # logger.info(cb)
    return response