import os
import base64
from multiprocessing import Pool
from dotenv import load_dotenv
from cachelib import SimpleCache
from flask import Flask, request, abort, jsonify, session
from flask_session import Session
from helpers.bulkinfer import run_custom_prompt,chunked_iterable
from helpers.get_data import extract_data
from helpers.summarize import summarize_data
from helpers.search import search_for_id, search_for_candidate, search_for_name
from helpers.get_mockdata import extract_and_store, extract_and_store_work_history
from helpers.get_cv_data_llama import extract_cv
from helpers.sanitize_b64 import sanitize_base64, get_file_type_from_base64
from helpers.convert2pdf_spire import convert_to_pdf, allowed_file
from helpers.bullhorn_access import BullhornAuthHelper, on_401_error
from prompts.data_prompt import AGE_BASE_PROMPT, LANGUAGE_SKILL_BASE_PROMPT, LOCATION_BASE_PROMPT
from prompts.prompt_database import read_item, SavePrompts, LoadPrompts, DeletePrompts
from flask_cors import CORS
import requests
import tempfile
import json

app = Flask(__name__)
CORS(app)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

cache = SimpleCache()

load_dotenv()
CLIENT_ID = os.getenv('SPECIALIZED_CLIENT_ID')
USERNAME = os.getenv('SPECIALIZED_USERNAME')
PASSWORD = os.getenv('SPECIALIZED_PASSWORD')
CLIENT_SECRET = os.getenv('SPECIALIZED_CLIENT_SECRET')
SPECIALIZED_URL = os.getenv('SPECIALIZED_REST_URL')

# Initialize BullhornAuthHelper
bullhorn_auth_helper = BullhornAuthHelper(CLIENT_ID, CLIENT_SECRET)
bullhorn_auth_helper.authenticate(USERNAME, PASSWORD)

@app.route('/api/get_candidate', methods=['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def get_candidate():
    try:
        received_id = request.json
        candidate_id = received_id["candidateId"]
        access_token = bullhorn_auth_helper.get_rest_token()
        search_candidate_by_id_url = f'search/Candidate?BhRestToken={access_token}&query=id:{candidate_id}&fields=id,firstName,lastName,email,phone,dateOfBirth,address,certifications,ethnicity,primarySkills,educationDegree,comments,secondarySkills,skillSet,specialties'
        search_candidate_workhistory_by_id_url=f'query/CandidateWorkHistory?BhRestToken={access_token}&fields=id,startDate,endDate,companyName,title,isLastJob,comments,jobOrder&where=candidate.id={candidate_id}'
        
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

        candidate_data = [candidate_data,candidate_workhistory]
        return candidate_data

    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500
    
@app.route('/api/search_name', methods = ['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def search_candidate():
    try:
        received_name = request.json
        candidate_name = received_name["name"]
        access_token = bullhorn_auth_helper.get_rest_token()
        search_candidate_by_name_url = f'search/Candidate?BhRestToken={access_token}&fields=id,firstName,lastName,status&query=name:{candidate_name} AND isDeleted:false&sort=name'
        candidate_data = requests.get(SPECIALIZED_URL+search_candidate_by_name_url)
        if candidate_data.status_code == 401:
            try:
                error = candidate_data.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)
        else:
            pass
        candidate_data = candidate_data.json()
        candidate_data = candidate_data['data']
        return candidate_data
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500

@app.route('/api/get_pdf', methods = ['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def get_candidate_pdf():
    try:
        received_data = request.json
        candidate_id = received_data['candidateId']
        mode = received_data['mode']
        files_data = {"files": []}

        if mode in ["bullhorn", "CV_bullhorn"]:
            access_token = bullhorn_auth_helper.get_rest_token()
            search_candidate_file_by_id_url = f"entity/Candidate/{candidate_id}/fileAttachments?BhRestToken={access_token}&fields=id"
            response = requests.get(SPECIALIZED_URL + search_candidate_file_by_id_url)
            if response.status_code == 401:
                try:
                    error = response.json()
                    raise Exception(error["message"])
                except:
                    raise Exception(error)
            
            file_attachments = response.json().get('data', [])

            for attachment in file_attachments:
                file_id = attachment['id']
                get_candidate_file_url = f"file/Candidate/{candidate_id}/{file_id}?BhRestToken={access_token}"
                candidate_file_response = requests.get(SPECIALIZED_URL + get_candidate_file_url)
                if candidate_file_response.status_code == 401:
                    try:
                        error = candidate_file_response.json()
                        raise Exception(error["message"])
                    except:
                        raise Exception(error)
                
                candidate_file_response = candidate_file_response.json()
                file_name = candidate_file_response['File']['name']
                file_content_base64 = candidate_file_response['File']['fileContent']
                file_content_base64 = sanitize_base64(file_content_base64)
                file_type = get_file_type_from_base64(file_content_base64)  # Assuming it returns "PDF", "DOC", or "DOCX"

                # Decode base64 content to binary
                file_bytes = base64.b64decode(file_content_base64)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type.lower()}') as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(file_bytes)

                try:
                    # Convert to PDF if not already in PDF
                    if file_type != 'PDF':
                        pdf_file_path = convert_to_pdf(temp_file_path)  # Implement this function
                    else:
                        pdf_file_path = temp_file_path

                    # Read the PDF and encode it in base64
                    with open(pdf_file_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    file_content_base64 = base64.b64encode(pdf_data).decode('utf-8')

                    file_content_base64 = sanitize_base64(file_content_base64)
                    files_data["files"].append({"type": "application/pdf", "candidateFile": file_content_base64, "fileName": file_name})
                finally:
                    # Cleanup temporary file
                    os.remove(temp_file_path)
                    if file_type != 'PDF' and pdf_file_path != temp_file_path:
                        os.remove(pdf_file_path)
        else:
            cache_key = 'uploaded_pdf'
            candidate_file_base64 = cache.get(cache_key)
            
            candidate_file_base64 = sanitize_base64(candidate_file_base64)
            file_type = "application/pdf"
            
            files_data["files"].append({"type": file_type, "candidateFile": candidate_file_base64, "fileName":"uploadedPDF"})

        return jsonify(files_data)
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500
    
@app.route('/api/extract_bullhorn', methods = ['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def extract_bullhorn_pdf():
    try:
        received_data= request.json
        candidate_id = received_data['candidateId']
        access_token = bullhorn_auth_helper.get_rest_token()
        search_candidate_file_by_id_url = f"entity/Candidate/{candidate_id}/fileAttachments?BhRestToken={access_token}&fields=id"
        file_id = requests.get(SPECIALIZED_URL+search_candidate_file_by_id_url)
        if file_id.status_code == 401:
            try:
                error = file_id.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)
        else:
            pass
        file_id = file_id.json()
        file_id = file_id['data'][0]['id']

        get_candidate_file_url = f"file/Candidate/{candidate_id}/{file_id}?BhRestToken={access_token}"
        candidate_file = requests.get(SPECIALIZED_URL + get_candidate_file_url)
        if candidate_file.status_code == 401:
            try:
                error = candidate_file.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)
        else:
            pass
        candidate_file = candidate_file.json()
        candidate_file = candidate_file['File']['fileContent']
        candidate_file = sanitize_base64(candidate_file)
        file_type = get_file_type_from_base64(candidate_file)  # Assuming it returns "PDF", "DOC", or "DOCX"
                
        # Decode base64 content to binary
        file_bytes = base64.b64decode(candidate_file)
        
        # Define the temp file path with the correct suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type.lower()}') as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(file_bytes)

        try:
            # Convert to PDF if not already in PDF
            if file_type != 'PDF':
                pdf_file_path = convert_to_pdf(temp_file_path)  # Implement this function
            else:
                pdf_file_path = temp_file_path

            extracted_data = extract_cv(pdf_file_path)  # Implement this function
            cache_key = 'extracted_cv'
            cache.set(cache_key, extracted_data, timeout=60 * 60)
        finally:
            # Cleanup temporary file
            os.remove(temp_file_path)
            if file_type != 'PDF' and pdf_file_path != temp_file_path:
                os.remove(pdf_file_path)
        return extracted_data
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500

@app.route('/api/get_prompt/<int:version_number>', methods = ['POST'])
def send_base_prompt(version_number):
    try:
        received_type = request.json
        prompt_type = received_type["dataToInfer"]
        prompt = read_item(prompt_type,version_number)
        if prompt == "No data found":
            if prompt_type == 'age':
                prompt = AGE_BASE_PROMPT
            elif prompt_type == 'languageSkills':
                prompt = LANGUAGE_SKILL_BASE_PROMPT
            elif prompt_type == 'location':
                prompt = LOCATION_BASE_PROMPT
        response = {"prompt":prompt}
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_prompt', methods = ['POST'])
def get_prompt_count():
    try:
        received_type = request.json
        prompt_type = received_type['dataToInfer']
        load = LoadPrompts(prompt_type)
        response = load.load_prompts()

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/save_prompt', methods = ['POST'])
def save_prompt_on_db():
    try:
        received_type = request.json
        prompt = received_type['response']
        prompt_type = received_type['dataToInfer']
        load = SavePrompts(prompt, prompt_type)
        response = load.create_versions()

        return jsonify({"response":response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/delete_prompt/<int:version_number>', methods = ['POST'])
def delete_prompt_on_db(version_number):
    try:
        received_type = request.json
        prompt_type = received_type['dataToInfer']
        load = DeletePrompts(prompt_type, version_number)
        response = load.delete_item()

        return jsonify({"response":response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompt_input', methods=['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def get_custom_prompt():
    try:
        received_data = request.json
        custom_prompt = received_data["response"]
        candidate_id = received_data["candidateId"]
        infer_data = received_data["dataToInfer"]
        mode = received_data["mode"]
        access_token = bullhorn_auth_helper.get_rest_token()
        search_candidate_by_id_url = f'search/Candidate?BhRestToken={access_token}&query=id:{candidate_id}&fields=id,firstName,lastName,email,phone,dateOfBirth,address,certifications,ethnicity,primarySkills,educationDegree,comments,secondarySkills,skillSet,specialties'
        search_candidate_workhistory_by_id_url=f'query/CandidateWorkHistory?BhRestToken={access_token}&fields=id,candidate,startDate,endDate,companyName,title,isLastJob,comments,jobOrder&where=candidate.id={candidate_id}'
        if mode == "bullhorn":
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
            if (infer_data == "age" and candidate_data["dateOfBirth"] is None) or (infer_data == "location" and mode == "bullhorn") or (infer_data == "languageSkills"):
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
        else:
            cache_key = 'extracted_cv'
            candidate_data = cache.get(cache_key)
            if infer_data == "languageSkills":
                response = summarize_data(candidate_data, custom_prompt, infer_data)
            elif infer_data == "age" and candidate_data[0]["dateOfBirth"] is not None:
                response = summarize_data(candidate_data, custom_prompt, infer_data)
            elif infer_data == "age" and candidate_data[0]["dateOfBirth"] is None:
                response = summarize_data(candidate_data, custom_prompt, infer_data)
            elif infer_data == "location":
                response = summarize_data(candidate_data, custom_prompt, infer_data)
        return response
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500

@app.route('/api/bulk_prompt_input', methods=['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def get_bulk_custom_prompt():
    try:
        received_data = request.json
        custom_prompt = received_data["response"]
        infer_data = received_data["dataToInfer"]
        access_token = bullhorn_auth_helper.get_rest_token()

        if infer_data == "age":
            candidates = f"search/Candidate?BhRestToken={access_token}&query=*:* -(dateOfBirth:[* TO *]) AND isDeleted:false&fields=id,name&sort=-dateAdded&count=10&where=isDeleted=false"
        elif infer_data == "languageSkills":
            candidates = f"search/Candidate?BhRestToken={access_token}&query=*:* -(specialties.id:(2000044 OR 2000008 OR 2000009 OR 2000025 OR 2000010 OR 2000011 OR 2000042) OR (2000043 OR 2000015 OR 2000016 OR 2000026 OR 2000017 OR 2000018 OR 2000041)) AND isDeleted:false&fields=id,name&sort=-dateAdded&count=10&where=isDeleted=false"
        elif infer_data == "location":
            candidates = f"search/Candidate?BhRestToken={access_token}&query=*:* (address.country.id:2378) AND isDeleted:false&fields=id,name&sort=-dateAdded&count=10&where=isDeleted=false"
        
        candidate_data = requests.get(SPECIALIZED_URL + candidates)
        if candidate_data.status_code == 401:
            try:
                error = candidate_data.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)

        candidate_data = candidate_data.json()
        candidate_items = candidate_data['data']

        candidate_id_to_name = {item['id']: item['name'] for item in candidate_items}

        # Prepare to store the results
        params_list = [(cid, custom_prompt, infer_data, SPECIALIZED_URL) for cid in candidate_id_to_name.keys()]

        results_list = []

        # Process in batches of 10
        with Pool(processes=10) as pool:
            for params_batch in chunked_iterable(params_list, 10):
                batch_results = pool.map(run_custom_prompt, params_batch)
                for cid, status, result in batch_results:
                    candidate_name = candidate_id_to_name[cid]
                    results_list.append({
                        'id': cid,  # Include candidate ID if needed
                        'name': candidate_name,
                        'status': status,
                        **result  # Merge result dict which could contain 'data' or 'error'
                    })

        return jsonify(results_list)
    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500

@app.route('/api/filter_data', methods=['POST'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def filter_data():
    try:
        received_data = request.json
        filter_list = received_data.get("missingFields", [])  # Use .get to avoid KeyError if missingFields is not present

        filter_dict = {
            "age": "-dateOfBirth:[* TO *]",
            "languageSkillsEN": "-specialties.id:(2000044 OR 2000008 OR 2000009 OR 2000025 OR 2000010 OR 2000011 OR 2000042)",
            "languageSkillsJP": "-specialties.id:(2000043 OR 2000015 OR 2000016 OR 2000026 OR 2000017 OR 2000018 OR 2000041)",
            "location": "address.country.id:2378"
        }

        # Start building the query part for filters
        query_filters = []
        for field in filter_list:
            if field in filter_dict:
                query_filters.append(filter_dict[field])
        query_filters = " AND ".join(query_filters)  # Combine all filters with AND

        access_token = bullhorn_auth_helper.get_rest_token()
        base_url = f'search/Candidate?BhRestToken={access_token}&fields=id,firstName,lastName,status'
        if query_filters:  # If there are any filters, append them to the base_url
            filter_job_submission_url = f"{base_url}&query={query_filters} AND isDeleted:false&sort=-dateAdded&start=1&count=500"
        else:  # If no filters, just use the base URL
            filter_job_submission_url = f"search/Candidate?BhRestToken={access_token}&query=isDeleted:false&fields=id,firstName,lastName,status&sort=-dateAdded&count=500"

        response = requests.get(SPECIALIZED_URL + filter_job_submission_url)
        if response.status_code == 401:
            try:
                error = response.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)

        response_data = response.json()
        return jsonify(response_data['data'])

    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500
        

@app.route('/api/process_data', methods=['GET'])
@on_401_error(lambda: bullhorn_auth_helper.authenticate(USERNAME, PASSWORD))
def handle_api_data():
    try:
        access_token = bullhorn_auth_helper.get_rest_token()
        get_job_submission_url = f'search/Candidate?BhRestToken={access_token}&query=isDeleted:false&fields=id,firstName,lastName,status&sort=-dateAdded&count=500'

        response = requests.get(SPECIALIZED_URL+get_job_submission_url)
        if response.status_code == 401:
            try:
                error = response.json()
                raise Exception(error["message"])
            except:
                raise Exception(error)
        else:
            pass
        response = response.json()
        response = response['data']
        return response

    except Exception as e:
        if "Bad 'BhRestToken' or timed-out." or "BhRestToken" in str(e):
            raise Exception(str(e))
        else:
            return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])   
def upload_file():
    if 'pdfFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdfFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400

    file_type = file.filename.rsplit('.', 1)[1].lower()
    file_bytes = file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(file_bytes)

    try:
        # Convert to PDF if it's a DOCX or DOC
        if file_type in ['docx', 'doc']:
            pdf_file_path = convert_to_pdf(temp_file_path)
            os.remove(temp_file_path)  # Remove the original temp file after conversion
        else:
            pdf_file_path = temp_file_path

        # Here, pdf_file_path is the path to the PDF file, whether originally uploaded as PDF
        # or converted from DOCX/DOC
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        pdf_data = base64.b64encode(pdf_data).decode("utf-8")

        extracted_data = extract_cv(pdf_file_path)
        session['pdfFile'] = extracted_data

        cache_key = 'extracted_cv'
        cache.set(cache_key, extracted_data, timeout=60*60)
        # Cache key for the PDF file
        cache_key = 'uploaded_pdf'
        cache.set(cache_key, pdf_data, timeout=60*60)
    finally:
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

    return jsonify(extracted_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)