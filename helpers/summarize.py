import os
from dotenv import load_dotenv
from prompts.llama_prompts import language_skill, infer_age, infer_location
import datetime


def summarize_data(candidate_data, custom_prompt, infer_data):
    #Change openai_api_key
    candidate_data = str(candidate_data)
    current_date = datetime.date.today()

    if infer_data == "age":
        response = infer_age(candidate_data, custom_prompt, current_date)
    elif infer_data == "languageSkills":
        response = language_skill(candidate_data, custom_prompt)
    elif infer_data == "location":
        response = infer_location(candidate_data, custom_prompt, current_date)

    return response