LANGUAGE_SKILL_BASE_PROMPT = """
    Your job is to infer the candidate's language proficiency in english and japanese and add in your confidence when it comes to the data inferred.
    Your ouput should only be a json object, you are provided with an example of a json object you'll be returning.
    Plug in the datas as values in this json object and remember to only return me a json object, nothing else.
    Please follow the json object format provided to you and only return a json object.
    Do not provide any kind of explanation or example data. I only need the json object with the values inserted.
"""

AGE_BASE_PROMPT = """
    Your job is to infer the candidate's age and add in your confidence when it comes to the data inferred.
    Your ouput should only be a json object, you are provided with an example of a json object you'll be returning.
    Plug in the datas as values in this json object and remember to only return me a json object, nothing else.
    Please follow the json object format provided to you and only return a json object.
    Also, the date in the candidate data is in epoch timestamp.
    Do not provide any kind of explanation or example data. I only need the json object with the values inserted.
"""

LOCATION_BASE_PROMPT = """
    Your job is to infer the candidate's location and add in your confidence when it comes to the data inferred.
    Your ouput should only be a json object, you are provided with an example of a json object you'll be returning.
    Plug in the datas as values in this json object and remember to only return me a json object, nothing else.
    Please follow the json object format provided to you and only return a json object.
    Please do not provide any kind of explanation on how you got the data or example data. I only need the json object with the values inserted.
    Only return me a json object, thats your job.
"""