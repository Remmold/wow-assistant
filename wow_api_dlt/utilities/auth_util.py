from dlt.sources.helpers.rest_client.auth import OAuth2ClientCredentials
import dlt
from dlt.sources.helpers.rest_client import RESTClient
import time

# --- IMPORTANT: Add these imports ---
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# --- END IMPORTANT IMPORTS ---

from ..rate_limiter import blizzard_api_rate_limiter

BASE_URL = "https://eu.api.blizzard.com"

# --- Create a single, global RESTClient instance ---
# This client will handle connection pooling internally for all API calls.
_blizzard_api_client = None

def _initialize_api_client():
    """
    Initializes the global RESTClient instance if it hasn't been initialized yet.
    This ensures that only one client instance is created and reused across all API calls,
    enabling connection pooling and proper retry logic.
    """
    global _blizzard_api_client
    if _blizzard_api_client is None:
        client_id = dlt.secrets["wow_api"]["client_id"]
        client_secret = dlt.secrets["wow_api"]["client_secret"]
        
        # 1. Define the retry strategy for the underlying requests.Session
        _retry_strategy = Retry(
            total=5,  # Total retries
            backoff_factor=1, # Exponential backoff (1s, 2s, 4s, etc.)
            status_forcelist=[429, 500, 502, 503, 504], # HTTP status codes to retry on
            allowed_methods=["HEAD", "GET", "OPTIONS"], # Which HTTP methods to retry
            connect=5, # Crucial: retry connection-related errors like WinError 10055
        )
        
        # 2. Create an HTTPAdapter and mount the retry strategy to it
        _adapter = HTTPAdapter(
            pool_connections=50, # Number of connections to cache
            pool_maxsize=100,    # Max connections allowed in the pool
            max_retries=_retry_strategy # Apply the retry strategy to the adapter
        )
        
        # 3. Create a requests.Session instance and mount the adapter
        # This session will be passed to the dlt RESTClient
        _requests_session = requests.Session()
        _requests_session.mount("http://", _adapter)
        _requests_session.mount("https://", _adapter)
        
        # Set a default timeout for the session
        _requests_session.timeout = 30 # Default timeout for API requests in seconds

        # 4. Initialize the dlt RESTClient, passing the configured requests.Session
        _blizzard_api_client = RESTClient(
            base_url = BASE_URL,
            auth = OAuth2ClientCredentials(
                client_id = client_id,
                client_secret = client_secret,
                access_token_url = "https://oauth.battle.net/token",
            ),
            # Pass the pre-configured requests.Session instance here
            session=_requests_session 
        )
    return _blizzard_api_client

# Initialize the client once when the module is imported.
_initialize_api_client()


def get_api_response(endpoint: str, params: dict = {}):
    """
    Makes a request to the Blizzard API and returns the response.
    This function now uses the globally configured `_blizzard_api_client` instance,
    which handles connection pooling and retries internally.
    """
    blizzard_api_rate_limiter.wait_for_token()  

    # Use the pre-initialized global client
    response = _blizzard_api_client.get(path=endpoint, params=params)
    response.raise_for_status() 
    return response

if __name__ == "__main__":
    print("Testing get_api_response...")
    try:
        test_endpoint = "/data/wow/connected-realm/1304/auctions" # Example realm ID
        test_params = {"namespace": "dynamic-eu"}
        response = get_api_response(test_endpoint, test_params)
        print(f"Test successful! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Test failed: {e}")

