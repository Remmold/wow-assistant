from dlt.sources.helpers.rest_client.auth import OAuth2ClientCredentials
import dlt
from dlt.sources.helpers.rest_client import RESTClient
BASE_URL = "https://eu.api.blizzard.com"


def get_auth_token_and_request(endpoint: str, params: dict = {}):
    """
    Fetches an access token and makes a request to the Blizzard API.
    """
    client_id = dlt.secrets["wow_ah"]["client_id"]
    client_secret = dlt.secrets["wow_ah"]["client_secret"]
    client = RESTClient(
        base_url=BASE_URL,
        auth=OAuth2ClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
            access_token_url="https://oauth.battle.net/token",
        ),
    )
    response = client.get(path=endpoint, params=params)
    return response


if __name__ == "__main__":
    pass