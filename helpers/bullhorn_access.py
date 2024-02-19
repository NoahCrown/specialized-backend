import requests
from urllib.parse import urlparse, parse_qs
from functools import wraps

class BullhornAuthHelper:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.rest_token = None

    def authenticate(self, username, password):
        authorization_url = f'https://auth.bullhornstaffing.com/oauth/authorize?client_id={self.client_id}&username={username}&password={password}&response_type=code&action=Login'
        
        auth_response = requests.get(authorization_url, allow_redirects=True)
        redirect_url = auth_response.url
        code = self.extract_code_from_url(redirect_url)
        
        access_url = f'https://auth.bullhornstaffing.com/oauth/token?grant_type=authorization_code&code={code}&client_secret={self.client_secret}&client_id={self.client_id}'

        access_response = requests.post(access_url)
        access_response = access_response.json()
        self.access_token = access_response["access_token"]

        login_url = f'https://rest.bullhornstaffing.com/rest-services/login?version=*&access_token={self.access_token}'

        login_response = requests.post(login_url)
        login_response = login_response.json()
        self.rest_token = login_response["BhRestToken"]

    @staticmethod
    def extract_code_from_url(url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Check if 'code' parameter exists in the query
        if 'code' in query_params:
            code = query_params['code'][0]
            return code
        else:
            return None

    def get_access_token(self):
        return self.access_token

    def get_rest_token(self):
        return self.rest_token
    
def on_401_error(callback_function):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if "Bad 'BhRestToken' or timed-out." in str(e):
                    # Handle 401 error, maybe refresh token or take other actions
                    print("401 error occurred! Attempting to refresh Bullhorn access token.")
                    # Call the Bullhorn authentication callback function to refresh the token
                    access_token = callback_function()
                    # Retry the original function call with the new access token
                    return func(*args, **kwargs)
                else:
                    # Re-raise the exception if it's not a 401 error
                    raise e

        return wrapper

    return decorator