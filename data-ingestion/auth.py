import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()

def get_access_token():
    client_id = os.getenv("BLIZZARD_CLIENT_ID")
    client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")

    response = requests.post(
        "https://oauth.battle.net/token",
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(client_id, client_secret)
    )

    response.raise_for_status()
    return response.json()["access_token"]
