"""Minimal, polite MediaWiki API client: rate limit, retries, continuation merging."""
from __future__ import annotations

import os
import sys
import threading
import time
from typing import Iterator

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "formulaci/0.1 (knowledge verification research)"

# Wikimedia's 2026 API rate limits (https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits):
# a User-Agent without contact info is "Unidentified" and limited to 10 requests/minute; a
# compliant one (contact email or URL) gets 200/minute. Set FORMULACI_CONTACT to opt in.
UNIDENTIFIED_RPS = 10 / 62
IDENTIFIED_RPS = 3.0


def user_agent() -> str:
    contact = os.environ.get("FORMULACI_CONTACT", "").strip()
    return f"formulaci/0.1 (knowledge verification research; {contact})" if contact else USER_AGENT


def default_rps() -> float:
    if os.environ.get("FORMULACI_RPS"):
        return float(os.environ["FORMULACI_RPS"])
    return IDENTIFIED_RPS if os.environ.get("FORMULACI_CONTACT", "").strip() else UNIDENTIFIED_RPS


class APIError(RuntimeError):
    pass


class WikiClient:
    def __init__(self, api_url: str = API_URL, rps: float | None = None, max_retries: int = 10):
        self.api_url = api_url
        self.min_interval = 1.0 / min(rps or default_rps(), 5.0)
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent()
        self.session.headers["Accept-Encoding"] = "gzip"
        self._last = 0.0
        self._lock = threading.Lock()
        self.n_requests = 0

    def _wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            delay = self._last + self.min_interval - now
            if delay > 0:
                time.sleep(delay)
            self._last = time.monotonic()

    def get(self, params: dict) -> dict:
        """One API request (format=json, formatversion=2, maxlag=5) with retry/backoff."""
        p = {"format": "json", "formatversion": "2", "maxlag": "5", **params}
        backoff = 2.0
        for attempt in range(self.max_retries):
            self._wait()
            try:
                r = self.session.get(self.api_url, params=p, timeout=120)
                self.n_requests += 1
            except requests.RequestException as e:
                print(f"[api] network error {e!r}; retry in {backoff:.0f}s", file=sys.stderr)
                time.sleep(backoff)
                backoff = min(backoff * 2, 120)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                wait = max(float(r.headers.get("Retry-After", backoff)), 5.0)
                print(f"[api] HTTP {r.status_code}; retry in {wait:.0f}s: {r.text[:60]!r}", file=sys.stderr)
                time.sleep(wait)
                backoff = min(backoff * 2, 120)
                continue
            r.raise_for_status()
            data = r.json()
            err = data.get("error")
            if err:
                if err.get("code") in ("maxlag", "ratelimited", "internal_api_error_DBQueryTimeoutError"):
                    wait = float(r.headers.get("Retry-After", backoff))
                    print(f"[api] {err.get('code')}; retry in {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    backoff = min(backoff * 2, 120)
                    continue
                raise APIError(f"{err.get('code')}: {err.get('info')}")
            return data
        raise APIError(f"giving up after {self.max_retries} attempts: {params}")

    def query(self, params: dict) -> Iterator[dict]:
        """Yield each response of an action=query request, following `continue`."""
        params = {"action": "query", **params}
        cont: dict = {}
        while True:
            data = self.get({**params, **cont})
            yield data
            if "continue" not in data:
                return
            cont = data["continue"]

    def query_pages(self, params: dict) -> dict[int, dict]:
        """Run a prop query to completion and merge page records by pageid.

        List-valued props (revisions, categories) are concatenated across continuations;
        dict-valued props (pageviews) are merged.
        """
        merged: dict[int, dict] = {}
        for data in self.query(params):
            for page in data.get("query", {}).get("pages", []):
                pid = page.get("pageid")
                key = pid if pid is not None else page.get("title")
                cur = merged.setdefault(key, {})
                for k, v in page.items():
                    if isinstance(v, list) and isinstance(cur.get(k), list):
                        cur[k].extend(v)
                    elif isinstance(v, dict) and isinstance(cur.get(k), dict):
                        cur[k].update(v)
                    else:
                        cur[k] = v
        return merged
