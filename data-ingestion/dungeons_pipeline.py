import dlt
import requests
from auth import get_access_token
import time

@dlt.source
def dungeon_api_source():
    @dlt.resource(write_disposition="replace", name="dungeons")
    def fetch_dungeon_details():
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://us.api.blizzard.com"

        print("[🔄] Fetching dungeon index...")
        index_response = requests.get(
            f"{base_url}/data/wow/dungeon/index",
            headers=headers,
            params={"namespace": "static-us", "locale": "en_US"}
        )
        index_response.raise_for_status()
        dungeons = index_response.json()["dungeons"]
        print(f"[✅] Retrieved {len(dungeons)} dungeons.")

        for i, dungeon in enumerate(dungeons, start=1):
            detail_url = dungeon["key"]["href"]
            try:
                detail = requests.get(detail_url, headers=headers, timeout=10).json()
                print(f"[{i}/{len(dungeons)}] 🏰 {detail.get('name', 'Unknown')} (ID: {detail.get('id')})")
                yield detail
            except Exception as e:
                print(f"[❌] Failed to fetch dungeon: {detail_url} → {e}")
                continue

            if i % 50 == 0:
                print(f"[⏸️] Sleeping 1s after {i} calls to avoid throttling.")
                time.sleep(1)

        print("[🏁] Finished fetching all dungeon details.")

    return fetch_dungeon_details
