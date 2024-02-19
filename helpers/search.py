def search_for_id(candidate_id, list_of_response):
    
    found_candidate_data = None
    for response in list_of_response:
        if str(response.get('id')) == str(candidate_id):
            found_candidate_data = response
            break
    if found_candidate_data:
        return found_candidate_data
    else:
        raise ValueError ("Candidate not found")

def search_for_name(candidate_name, list_of_response):
    candidate_name = str(candidate_name).lower()  # Convert candidate name to lowercase

    found_candidate_data = None
    for response in list_of_response:
        first_name = str(response.get('first_name')).lower() if response.get('first_name') else None
        last_name = str(response.get('last_name')).lower() if response.get('last_name') else None

        if first_name == candidate_name or last_name == candidate_name:
            found_candidate_data = response
            break
    if found_candidate_data:
        return found_candidate_data
    else:
        raise ValueError ("Candidate not found")
    
def search_for_candidate(candidate_id, list_of_response):
    found_candidates_data = []
    
    for response in list_of_response:
        if str(response.get('candidate').get('id')) == str(candidate_id):
            found_candidates_data.append(response)
    
    if found_candidates_data:
        return found_candidates_data
    else:
        raise ValueError("Candidate not found")