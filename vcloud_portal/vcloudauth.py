import time
import requests
import json
from vcloud_portal.vcloudconfig import *

class VCloudDirectorTokenManager:
    def __init__(self, base_url, apitoken):
        # self.auth_url = base_url + '/cloudapi/1.0.0/sessions/provider'
        self.auth_url = base_url + '/oauth/provider/token'
        self.apitoken = apitoken
        self.token = None
        self.token_expiry_time = None

    def get_token(self):
        if self.token is None or self.is_token_expired():
            self.renew_token()
        return self.token

    def is_token_expired(self):
        if self.token_expiry_time is None:
            return True
        current_time = time.time()
        return current_time >= self.token_expiry_time - 30

    def renew_token(self):
        #response = requests.post(self.auth_url, auth=(self.username,self.password),headers={'Accept': 'application/json;version=36.3'})
        response = requests.post(
            self.auth_url,
            headers={'ContentType': 'application/x-www-form-urlencoded'},
            data=f"grant_type=refresh_token&refresh_token={self.apitoken}"
        )
        jsonobj = json.loads(response.content.decode())
        if response.status_code == 200:
            self.token = jsonobj['access_token']
            # Assuming the token expiry is provided in seconds
            self.token_expiry_time = time.time() + 1800
        else:
            raise Exception(f"Failed to renew token: {response.status_code} {response.reason}")
