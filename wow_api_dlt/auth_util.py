from dlt.sources.helpers.rest_client.auth import OAuth2ClientCredentials
import dlt
from dlt.sources.helpers.rest_client import RESTClient
import time
from .rate_limiter import blizzard_api_rate_limiter
BASE_URL = "https://eu.api.blizzard.com"



def get_api_client():
    """
    Returns a RESTClient instance configured for the Blizzard API.
    """
    client_id = dlt.secrets["wow_api"]["client_id"]
    client_secret = dlt.secrets["wow_api"]["client_secret"]
    return RESTClient(
        base_url = BASE_URL,
        auth = OAuth2ClientCredentials(
            client_id = client_id,
            client_secret = client_secret,
            access_token_url = "https://oauth.battle.net/token",
        ),
    )

def get_api_response(endpoint: str, params: dict = {}):
    """
    Makes a request to the Blizzard API and returns the response.
    """
    blizzard_api_rate_limiter.wait_for_token()  # Wait for a token before making the request

    client = get_api_client()
    response = client.get(path=endpoint, params=params)
    response.raise_for_status() # Ensure we raise an error for bad responses
    return response

if __name__ == "__main__":
    pass