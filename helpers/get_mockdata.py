import json

def extract_and_store(response):
    try:
        # Parse the API response as JSON
        api_data = response
        
        # Create an empty dictionary to store the extracted data
        extracted_data = {}
        
        address = api_data.get("address")
        # Store the API response in the dictionary
        extracted_data["id"] = api_data.get("id")
        extracted_data["first_name"] = api_data.get("first_name")
        extracted_data["last_name"] = api_data.get("last_name")
        extracted_data["address"] = {
            "address1": address.get("address1"),
            "address2": address.get("address2"),
            "city": address.get("city"),
            "state": address.get("state")
        }
        extracted_data["phone"] = api_data.get("phone")
        extracted_data["dateOfBirth"] = api_data.get("dateOfBirth")
        extracted_data["certification"] = api_data.get("certification")
        extracted_data["ethnicity"] = api_data.get("ethnicity")
        extracted_data["primarySkills"] = api_data.get("primarySkills")
        extracted_data["educationDegree"] = api_data.get("educationDegree")
        extracted_data["comments"] = api_data.get("comments")
        extracted_data["specialties"] = api_data.get("specialties")
        
        return extracted_data
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return None
    
def extract_and_store_work_history(response):
    try:
        # Parse the API response as JSON
        api_data = response

        candidate = api_data.get("candidate")
        extracted_data = {
            "id": api_data.get("id"),
            "candidate":{
                "id": candidate.get("id"),
                "first_name": candidate.get("first_name"),
                "last_name": candidate.get("last_name")
                },
            "startDate": api_data.get("startDate"),
            "endDate": api_data.get("endDate"),
            "companyName": api_data.get("companyName"),
            "title": api_data.get("title"),
            "islastJob": api_data.get("islastJob")
        }
        
        return extracted_data
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return None
