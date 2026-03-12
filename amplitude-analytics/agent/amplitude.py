"""
Amplitude Analytics Client
Uses the Events Segmentation API (/api/2/events/segmentation) — the correct
endpoint for getting daily unique user counts per event.

Auth: Basic auth (base64 of api_key:secret_key)
Docs: https://www.docs.developers.amplitude.com/analytics/apis/event-segmentation-api/
"""

import base64
import json
import time
import requests
from typing import Dict, List, Optional


class AmplitudeClient:

    BASE_URL = "https://amplitude.com/api/2"

    def __init__(self, api_key: str, secret_key: str):
        token = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def get_event_totals(self, event_name: str, start: str, end: str) -> int:
        """
        Return total unique users who fired `event_name` in [start, end].
        start/end format: YYYYMMDD
        """
        data = self._segmentation(event_name, start, end, group_by=None)
        if data is None:
            return 0
        series = data.get("series", [[]])
        if series and series[0]:
            return sum(v for v in series[0] if v is not None)
        return 0

    def get_event_by_platform(
        self, event_name: str, start: str, end: str
    ) -> Dict[str, int]:
        """
        Return unique users for `event_name` broken down by platform.
        Returns e.g. {"Android": 1200, "iOS": 400, "Web": 180}
        """
        data = self._segmentation(event_name, start, end, group_by="platform")
        if data is None:
            return {}

        series = data.get("series", [])
        labels = data.get("seriesLabels", [])

        result: Dict[str, int] = {}
        for i, label_group in enumerate(labels):
            if i >= len(series):
                continue
            # seriesLabels can be ["Android", "iOS"] OR [["Android"], ["iOS"]]
            # Handle both cases
            if isinstance(label_group, list):
                platform = str(label_group[0]) if label_group else "Unknown"
            else:
                platform = str(label_group) if label_group is not None else "Unknown"
            if not platform or platform == "None":
                platform = "Unknown"
            total = sum(v for v in series[i] if v is not None)
            if total > 0:
                result[platform] = result.get(platform, 0) + total

        return result

    def get_daily_series(
        self, event_name: str, start: str, end: str
    ) -> List[int]:
        """
        Return a list of daily unique user counts for `event_name`.
        Useful for sparkline / trend visualisation.
        """
        data = self._segmentation(event_name, start, end, group_by=None)
        if data is None:
            return []
        series = data.get("series", [[]])
        if series and series[0]:
            return [v if v is not None else 0 for v in series[0]]
        return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _segmentation(
        self,
        event_name: str,
        start: str,
        end: str,
        group_by: Optional[str],
        retries: int = 2,
    ) -> Optional[Dict]:
        """
        Call the Amplitude Events Segmentation API.
        Returns the `data` dict from the response, or None on failure.
        """
        params = {
            "e":     json.dumps({"event_type": event_name}),
            "start": start,
            "end":   end,
            "m":     "uniques",   # unique users (not raw event count)
            "i":     1,           # daily intervals
        }
        if group_by:
            params["g"] = group_by

        for attempt in range(retries + 1):
            try:
                resp = requests.get(
                    f"{self.BASE_URL}/events/segmentation",
                    params=params,
                    headers=self.headers,
                    timeout=20,
                )

                if resp.status_code == 200:
                    return resp.json().get("data", {})

                if resp.status_code == 429:
                    # Rate limited — back off and retry
                    wait = 2 ** attempt
                    print(f"    ⏳ Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                print(
                    f"    ⚠️  {event_name} [{group_by or 'total'}]: "
                    f"HTTP {resp.status_code} — {resp.text[:120]}"
                )
                return None

            except requests.exceptions.Timeout:
                print(f"    ⚠️  {event_name}: request timed out (attempt {attempt + 1})")
                if attempt < retries:
                    time.sleep(1)
                    continue
                return None

            except Exception as e:
                print(f"    ⚠️  {event_name}: {e}")
                return None

        return None
