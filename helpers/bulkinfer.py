from flask import jsonify
import requests
import os
from helpers.summarize import summarize_data
from helpers.bullhorn_access import BullhornAuthHelper, on_401_error
import itertools
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('SPECIALIZED_CLIENT_ID')
USERNAME = os.getenv('SPECIALIZED_USERNAME')
PASSWORD = os.getenv('SPECIALIZED_PASSWORD')
CLIENT_SECRET = os.getenv('SPECIALIZED_CLIENT_SECRET')
SPECIALIZED_URL = os.getenv('SPECIALIZED_REST_URL')

# Initialize BullhornAuthHelper
bullhorn_auth_helper = BullhornAuthHelper(CLIENT_ID, CLIENT_SECRET)
bullhorn_auth_helper.authenticate(USERNAME, PASSWORD)

@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def run_custom_prompt(params):

    candidate_id, custom_prompt, infer_data, SPECIALIZED_URL= params
    access_token = bullhorn_auth_helper.get_rest_token()
    try:
        search_candidate_by_id_url = f'search/Candidate?BhRestToken={access_token}&query=id:{candidate_id}&fields=id,firstName,lastName,email,phone,dateOfBirth,address,certifications,ethnicity,primarySkills,educationDegree,comments,secondarySkills,skillSet,specialties'
        search_candidate_workhistory_by_id_url=f'query/CandidateWorkHistory?BhRestToken={access_token}&fields=id,candidate,startDate,endDate,companyName,title,isLastJob,comments,jobOrder&where=candidate.id={candidate_id}'
        candidate_data = requests.get(SPECIALIZED_URL+search_candidate_by_id_url)
        if candidate_data.status_code == 401:
            try:
                error = candidate_data.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)
        else:
            pass
        candidate_data = candidate_data.json()
        candidate_data = candidate_data['data'][0]
        if (infer_data == "age" and candidate_data["dateOfBirth"] is None) or (infer_data == "location") or (infer_data == "languageSkills"):
            candidate_workhistory = requests.get(SPECIALIZED_URL+search_candidate_workhistory_by_id_url)
            if candidate_workhistory.status_code == 401:
                try:
                    error = candidate_workhistory.json()
                    raise Exception(error["message"])
                except:
                    raise Exception(error)
            else:
                pass
            candidate_workhistory = candidate_workhistory.json()
            candidate_workhistory = candidate_workhistory['data']
            candidate_data = [candidate_data, candidate_workhistory]
            response = summarize_data(candidate_data, custom_prompt, infer_data)

        elif infer_data == "age" and candidate_data["dateOfBirth"] is not None:
            response = summarize_data(candidate_data, custom_prompt, infer_data)
        status = "success"
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            response = {"error": str(e)}
            status = "failed"
    
    return candidate_id, status, response

def process_candidate_batch(params_batch):
    # This function is intended to be run in a separate process
    # It receives a batch of parameters for each candidate
    results = []
    for params in params_batch:
        result = run_custom_prompt(params)
        results.append(result)
    return results

def chunked_iterable(iterable, size):
    it = iter(iterable)
    chunk = list(itertools.islice(it, size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, size))
    