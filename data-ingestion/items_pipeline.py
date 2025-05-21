"""
Full DLT source that fetches every WoW retail item via /search/item,
throttles to stay under Blizzard’s 36 000-requests/h ceiling **and**
recovers automatically from transient 5xx errors.

• `calls_per_hour` – dial overall speed ( ≤ 36 000 )
• `max_pages`      – dev limiter (pages per bucket)
• `fast=True`      – disable throttling (at your own risk)

Table created:  raw.items   (write_disposition="merge", primary_key="id")
"""

import time, random, requests, dlt
from typing import Optional, Tuple, List
from auth import get_access_token
from requests.exceptions import RequestException, HTTPError

# ──────────────────────────── CONSTANTS ────────────────────────────
BASE       = "https://us.api.blizzard.com"
SEARCH_EP  = "/data/wow/search/item"
NAMESPACE  = "static-us"
LOCALE     = "en_US"
HARD_LIMIT = 36_000            # Blizzard’s documented cap

# ───────────────────── helper: robust GET with retries ─────────────
def safe_request(
    url: str,
    *,
    headers: dict,
    params: dict,
    tries: int = 5,
    timeout: int = 30,
):
    """GET with retry/back-off; returns Response or raises after final failure."""
    delay = 1.0
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=timeout)
            if r.status_code >= 500:
                raise HTTPError(f"{r.status_code} {r.reason}")
            return r

        except (RequestException, HTTPError) as e:
            if attempt == tries:
                raise
            retry_after = r.headers.get("Retry-After") if "r" in locals() else None
            delay = float(retry_after) if retry_after else delay
            print(f"[🔁] retry {attempt}/{tries} in {delay:.1f}s → {url} ({e})")
            time.sleep(delay + random.uniform(0, 0.3))
            delay = min(delay * 2, 16.0)      # exponential back-off

# ───────────────────── discovery: all (class,subclass) ─────────────
def discover_buckets(token: str) -> List[Tuple[int, int]]:
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{BASE}/data/wow/item-class/index",
        headers=h,
        params={"namespace": NAMESPACE, "locale": LOCALE},
        timeout=30,
    )
    r.raise_for_status()

    buckets: list[Tuple[int, int]] = []
    for cls in r.json()["item_classes"]:
        cls_id = cls["id"]
        sub_idx = requests.get(
            cls["key"]["href"],
            headers=h,
            params={"namespace": NAMESPACE, "locale": LOCALE},
            timeout=30,
        ).json().get("item_subclasses", [])
        for sub in sub_idx:
            buckets.append((cls_id, sub["id"]))
    return buckets

# ────────────────────────────  DLT SOURCE  ─────────────────────────
@dlt.source
def item_api_source(
    max_pages: Optional[int] = None,      # pages per bucket limiter
    calls_per_hour: int = 25_000,         # global throttle
    fast: bool = False,                   # ignore throttle
):
    if calls_per_hour > HARD_LIMIT:
        raise ValueError("calls_per_hour cannot exceed 36 000")

    INTERVAL = 0 if fast else 3600 / calls_per_hour  # seconds between calls

    @dlt.resource(
        write_disposition="merge",
        name="items",
        primary_key="id",
    )
    def fetch_items():

        token   = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        buckets = discover_buckets(token)
        print(f"[🗂️]  Discovered {len(buckets)} item buckets")

        # ── checkpoint state ──
        st             = dlt.state()
        bucket_idx     = st.get("items.bucket_idx", 0)
        page_resume    = st.get("items.page", 1)

        next_allowed   = time.perf_counter()
        req_total      = 0

        for idx, (cls_id, sub_id) in enumerate(buckets[bucket_idx:], start=bucket_idx):
            page = page_resume
            while True:

                # dev limiter
                if max_pages and page > max_pages:
                    break

                # throttle
                if not fast:
                    now = time.perf_counter()
                    if now < next_allowed:
                        time.sleep(next_allowed - now)
                    next_allowed = time.perf_counter() + INTERVAL

                params = {
                    "namespace": NAMESPACE,
                    "locale": LOCALE,
                    "item_class.id": cls_id,
                    "item_subclass.id": sub_id,
                    "_page": page,
                    "_pageSize": 100,
                    "orderby": "id",
                }

                try:
                    r = safe_request(f"{BASE}{SEARCH_EP}", headers=headers, params=params)
                except Exception as err:
                    print(f"[❌]  skipped cls {cls_id}/{sub_id} page {page} → {err}")
                    break

                if r.status_code == 404:
                    break                              # empty subclass
                results = r.json().get("results", [])
                if not results:
                    break                              # last page

                for entry in results:
                    yield entry["data"]

                req_total += 1
                if req_total % 1000 == 0:
                    print(f"[⏱️]  {req_total} requests so far …")

                print(
                    f"[📦]  cls {cls_id}/{sub_id} page {page} → "
                    f"{len(results)} items"
                )

                # checkpoint
                st["items.bucket_idx"] = idx
                st["items.page"]       = page
                page += 1

            page_resume = 1   # reset for next bucket

        print("[✅] Item crawl complete")
        st.pop("items.bucket_idx", None)
        st.pop("items.page", None)

    return fetch_items
