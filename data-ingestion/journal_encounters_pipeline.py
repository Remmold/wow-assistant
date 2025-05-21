import dlt
import requests
import time
from typing import Optional
from auth import get_access_token

@dlt.source
def journal_encounter_source(limit: Optional[int] = 10):  # Allow None for full run
    @dlt.resource(write_disposition="replace", name="journal_encounters")
    def fetch_journal_encounters():
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://us.api.blizzard.com"
        namespace = "static-us"
        locale = "en_US"

        print("[🔄] Fetching journal encounter index...")
        try:
            index_response = requests.get(
                f"{base_url}/data/wow/journal-encounter/index",
                headers=headers,
                params={"namespace": namespace, "locale": locale}
            )
            index_response.raise_for_status()
            encounters = index_response.json()["encounters"]
        except Exception as e:
            print(f"[❌] Failed to fetch encounter index → {e}")
            return

        print(f"[✅] Found {len(encounters)} journal encounters.")

        total = len(encounters) if limit is None else min(limit, len(encounters))

        for i, enc in enumerate(encounters[:total], start=1):
            url = enc["key"]["href"]
            try:
                detail_response = requests.get(url, headers=headers, timeout=10)
                detail_response.raise_for_status()
                detail = detail_response.json()
                print(f"[{i}/{total}] ⚔️ {detail['name']} (ID: {detail['id']})")
                yield detail
            except Exception as e:
                print(f"[❌] Failed: {url} → {e}")
                continue

            if i % 50 == 0:
                print(f"[⏸️] Pausing after {i} calls.")
                time.sleep(1)

        print("[🏁] Done fetching journal encounters.")

    return fetch_journal_encounters
