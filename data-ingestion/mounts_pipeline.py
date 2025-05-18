import dlt
import requests
import time
from auth import get_access_token

@dlt.source
def blizzard_api_source():
    @dlt.resource(write_disposition="replace", name="mounts")
    def fetch_mount_details():
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://us.api.blizzard.com"

        print("[🔄] Fetching mount index...")
        index_response = requests.get(
            f"{base_url}/data/wow/mount/index",
            headers=headers,
            params={"namespace": "static-us", "locale": "en_US"}
        )
        index_response.raise_for_status()
        mounts = index_response.json()["mounts"]
        print(f"[✅] Retrieved {len(mounts)} mounts.")

        for i, mount in enumerate(mounts, start=1):
            detail_url = mount["key"]["href"]
            try:
                detail = requests.get(detail_url, headers=headers, timeout=10).json()
                print(f"[{i}/{len(mounts)}] ➜ {detail.get('name', 'Unknown')} (ID: {detail.get('id')})")
                yield detail
            except Exception as e:
                print(f"[❌] Failed to fetch: {detail_url} → {e}")
                continue

            if i % 100 == 0:
                print(f"[⏸️] Pausing for 1s after {i} calls to respect rate limits.")
                time.sleep(1)

        print("[🏁] Finished fetching all mount details.")

    return fetch_mount_details
