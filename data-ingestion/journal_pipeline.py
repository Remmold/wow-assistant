import dlt
import requests
import time
from typing import Optional
from auth import get_access_token

@dlt.source
def journal_api_source(limit: Optional[int] = 10):  # Default to 10 for testing
    @dlt.resource(write_disposition="replace", name="journal_instances")
    def fetch_journal_instances():
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://us.api.blizzard.com"
        namespace = "static-us"
        locale = "en_US"

        print("[🔄] Fetching journal instance index...")
        try:
            index_response = requests.get(
                f"{base_url}/data/wow/journal-instance/index",
                headers=headers,
                params={"namespace": namespace, "locale": locale}
            )
            index_response.raise_for_status()
            instances = index_response.json()["instances"]
        except Exception as e:
            print(f"[❌] Failed to fetch instance index → {e}")
            return

        print(f"[✅] Found {len(instances)} journal instances.")

        total = len(instances) if limit is None else min(limit, len(instances))

        for i, instance in enumerate(instances[:total], start=1):
            detail_url = instance["key"]["href"]
            try:
                detail_response = requests.get(detail_url, headers=headers, timeout=10)
                detail_response.raise_for_status()
                detail = detail_response.json()
                print(f"[{i}/{total}] 📘 {detail['name']} (ID: {detail['id']})")
                yield detail
            except Exception as e:
                print(f"[❌] Failed to fetch instance {detail_url} → {e}")
                continue

            if i % 25 == 0:
                print(f"[⏸️] Sleeping 1s after {i} requests.")
                time.sleep(1)

        print("[🏁] Finished fetching journal instances.")

    return fetch_journal_instances
