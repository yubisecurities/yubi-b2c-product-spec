"""
Amplitude Analytics Client

Two APIs used:
  1. Funnel API (/api/2/funnels) — for signup funnel conversion data.
     Counts unique users who completed steps IN ORDER within the date window.
     Matches what Amplitude's dashboard Funnel chart shows.
     NOTE: do NOT pass the `n` (conversion window) param — it causes HTTP 400.

  2. Segmentation API (/api/2/events/segmentation) — for individual event
     counts (failure events, etc.) that aren't part of an ordered funnel.

Auth: Basic auth (base64 of api_key:secret_key)
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

    def get_funnel(
        self, event_names: List[str], start: str, end: str
    ) -> Dict[str, int]:
        """
        Run a funnel analysis and return {event_name: cumulative_count} per step.
        Counts unique users who completed steps in order — matches the dashboard.
        """
        data = self._funnel(event_names, start, end, group_by=None)
        if not data:
            return {e: 0 for e in event_names}
        raw = data[0].get("cumulativeRaw", [])
        return {event_names[i]: raw[i] for i in range(min(len(event_names), len(raw)))}

    def get_funnel_by_platform(
        self, event_names: List[str], start: str, end: str
    ) -> Dict[str, Dict[str, int]]:
        """
        Run a funnel analysis grouped by platform.
        Returns {platform: {event_name: cumulative_count}}.
        groupValue in the response gives the platform name ("Android", "iOS", "Web").
        """
        data = self._funnel(event_names, start, end, group_by="platform")
        if not data:
            return {}
        result: Dict[str, Dict[str, int]] = {}
        for item in data:
            platform = item.get("groupValue") or "Unknown"
            raw = item.get("cumulativeRaw", [])
            result[str(platform)] = {
                event_names[i]: raw[i]
                for i in range(min(len(event_names), len(raw)))
            }
        return result

    def get_event_by_device_type(
        self, event_name: str, start: str, end: str
    ) -> Dict[str, int]:
        """
        Return unique users for `event_name` broken down by device_type.
        device_type returns full device model strings:
          e.g. "Apple iPhone 15", "Samsung Galaxy A52", "Windows", "Mac"
        """
        data = self._segmentation(event_name, start, end, group_by="device_type")
        if data is None:
            return {}

        series = data.get("series", [])
        labels = data.get("seriesLabels", [])

        result: Dict[str, int] = {}
        for i, label_group in enumerate(labels):
            if i >= len(series):
                continue
            if isinstance(label_group, list):
                device = str(label_group[0]) if label_group else "Unknown"
            else:
                device = str(label_group) if label_group is not None else "Unknown"
            if not device or device in ("None", "(none)"):
                continue
            total = sum(v for v in series[i] if v is not None)
            if total > 0:
                result[device] = result.get(device, 0) + total

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

    def _funnel(
        self,
        event_names: List[str],
        start: str,
        end: str,
        group_by: Optional[str],
        retries: int = 2,
    ) -> Optional[List[Dict]]:
        """
        Call the Amplitude Funnel Analysis API.
        IMPORTANT: do NOT pass `n` (conversion window param) — it causes HTTP 400.
        Returns the `data` list from the response, or None on failure.
        """
        # Funnel API takes one `e` param per step as a list of tuples
        params: List = [("e", json.dumps({"event_type": e})) for e in event_names]
        params += [("start", start), ("end", end)]
        if group_by:
            params.append(("g", group_by))

        for attempt in range(retries + 1):
            try:
                resp = requests.get(
                    f"{self.BASE_URL}/funnels",
                    params=params,
                    headers=self.headers,
                    timeout=30,
                )

                if resp.status_code == 200:
                    return resp.json().get("data", [])

                if resp.status_code == 429:
                    wait = 2 ** attempt
                    print(f"    ⏳ Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                print(
                    f"    ⚠️  Funnel API [{group_by or 'overall'}]: "
                    f"HTTP {resp.status_code} — {resp.text[:120]}"
                )
                return None

            except requests.exceptions.Timeout:
                print(f"    ⚠️  Funnel API: request timed out (attempt {attempt + 1})")
                if attempt < retries:
                    time.sleep(1)
                    continue
                return None

            except Exception as e:
                print(f"    ⚠️  Funnel API error: {e}")
                return None

        return None
