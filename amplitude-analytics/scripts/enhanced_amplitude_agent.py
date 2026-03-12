#!/usr/bin/env python3
"""
Enhanced Amplitude Analytics Client with Device Categorization
Fetches signup funnel data broken down by OS and Device Tier
"""

import os
import requests
import json
import base64
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

class DeviceCategorizer:
    """Categorizes devices into tiers based on model"""

    LOW_TIER_KEYWORDS = [
        'j2', 'j3', 'j4', 'j5', 'j6', 'j7',  # Samsung J series
        'redmi 6', 'redmi 7', 'redmi 8', 'redmi 9',  # Redmi budget
        'realme c', 'realme 3', 'realme 5',  # Realme budget
        'moto e', 'moto e4', 'moto e5',  # Moto E series
        'infinix', 'tecno', 'nokia 1', 'nokia 2',  # Budget brands
        'micromax', 'lava', 'intex'
    ]

    MID_TIER_KEYWORDS = [
        'samsung a', 'samsung m', 'samsung note',  # Samsung A/M/Note
        'samsung s20', 'samsung s21',  # Older flagships
        'poco', 'poco x2', 'poco x3',  # Poco series
        'redmi note', 'redmi k30',  # Redmi mid
        'realme 6', 'realme 7', 'realme 8',  # Realme mid
        'oneplus nord', 'oneplus 7', 'oneplus 8',  # OnePlus mid
        'moto g', 'moto g10', 'moto g20',  # Moto G series
        'vivo v17', 'vivo v19', 'vivo v20',  # Vivo mid
        'oppo f', 'oppo a'  # Oppo mid
    ]

    PREMIUM_KEYWORDS = [
        'samsung s22', 'samsung s23', 'samsung s24',  # Samsung flagship
        'samsung s ultra',  # Samsung Ultra
        'oneplus 9', 'oneplus 10', 'oneplus 11',  # OnePlus flagship
        'pixel 6', 'pixel 7', 'pixel 8',  # Google Pixel
        'poco f', 'poco f3', 'poco f4',  # Poco F series (flagship killer)
    ]

    @staticmethod
    def categorize(device_model: str, os_name: str) -> str:
        """Categorize device into tier"""

        if not device_model:
            return f"{os_name} - Unknown Model"

        device_lower = device_model.lower()

        # Handle iOS
        if 'ios' in os_name.lower() or 'iphone' in device_lower or 'ipad' in device_lower:
            return "iOS"

        # Handle Web
        if 'web' in os_name.lower() or 'windows' in device_lower or 'mac' in device_lower:
            return "Web"

        # Categorize Android by tier
        if any(keyword in device_lower for keyword in DeviceCategorizer.PREMIUM_KEYWORDS):
            return "Premium Android"
        elif any(keyword in device_lower for keyword in DeviceCategorizer.MID_TIER_KEYWORDS):
            return "Mid-tier Android"
        elif any(keyword in device_lower for keyword in DeviceCategorizer.LOW_TIER_KEYWORDS):
            return "Low-tier Android"
        else:
            # Default to mid-tier if unknown
            return "Mid-tier Android (Unknown model)"

    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all device categories"""
        return [
            "Low-tier Android",
            "Mid-tier Android",
            "Premium Android",
            "iOS",
            "Web"
        ]


class EnhancedAmplitudeAnalyticsClient:
    """Enhanced Amplitude client with device tier breakdown"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://amplitude.com/api/2"
        self.auth_string = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth_string}',
            'Accept': 'application/json'
        }

    def get_funnel_by_device_tier(self, hours: int = 48) -> Dict:
        """Get signup funnel conversion broken down by device tier"""

        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours)

        print(f"\n🔄 Fetching events from Amplitude...")
        print(f"   Period: {from_date.strftime('%Y-%m-%d %H:%M')} to {to_date.strftime('%Y-%m-%d %H:%M')}")

        try:
            # Query both events
            view_events = self._fetch_events('SIGNIN_PAGE_VIEW')
            enter_events = self._fetch_events('SIGNIN_PAGE_NUMBER_ENTERED')

            if not view_events or not enter_events:
                return {
                    'status': 'error',
                    'error': 'Could not fetch events from Amplitude',
                    'timestamp': datetime.now().isoformat()
                }

            # Group by device tier
            view_by_tier = self._group_by_device_tier(view_events)
            enter_by_tier = self._group_by_device_tier(enter_events)

            # Calculate conversions per tier
            conversions = self._calculate_conversions(view_by_tier, enter_by_tier)

            return {
                'status': 'success',
                'period': f"{from_date.isoformat()} to {to_date.isoformat()}",
                'conversions': conversions,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _fetch_events(self, event_name: str) -> List[Dict]:
        """Fetch events from Amplitude"""
        endpoint = f"{self.base_url}/events/list"

        params = {
            'event': event_name,
            'limit': 10000
        }

        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"⚠️ Could not fetch {event_name}: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error fetching {event_name}: {str(e)}")
            return []

    def _group_by_device_tier(self, events: List[Dict]) -> Dict:
        """Group events by device tier"""

        tier_users = defaultdict(set)

        for event in events:
            # Extract device info
            device_model = (
                event.get('device_model') or
                event.get('properties', {}).get('device_model') or
                'Unknown'
            )

            os_name = (
                event.get('os_name') or
                event.get('properties', {}).get('os_name') or
                'Unknown'
            )

            # Categorize device
            tier = DeviceCategorizer.categorize(device_model, os_name)

            # Track unique users per tier
            user_id = event.get('user_id') or event.get('amplitude_id')
            if user_id:
                tier_users[tier].add(user_id)

        # Convert sets to counts
        return {tier: len(users) for tier, users in tier_users.items()}

    def _calculate_conversions(self, view_by_tier: Dict, enter_by_tier: Dict) -> Dict:
        """Calculate conversion rates per device tier"""

        conversions = {}

        # Ensure all categories are represented
        all_tiers = set(list(view_by_tier.keys()) + list(enter_by_tier.keys()))

        for tier in sorted(all_tiers):
            views = view_by_tier.get(tier, 0)
            entries = enter_by_tier.get(tier, 0)

            if views > 0:
                conversion_rate = entries / views
            else:
                conversion_rate = 0

            conversions[tier] = {
                'views': views,
                'entries': entries,
                'rate': conversion_rate,
                'percent': round(conversion_rate * 100, 1),
                'status': 'healthy' if conversion_rate > 0.45 else 'anomaly'
            }

        return conversions


def main():
    """Test the enhanced client"""

    api_key = os.getenv("AMPLITUDE_API_KEY", "")  # Set AMPLITUDE_API_KEY env var
    secret_key = os.getenv("AMPLITUDE_SECRET_KEY", "")  # Set AMPLITUDE_SECRET_KEY env var

    print("=" * 90)
    print("📊 ENHANCED AMPLITUDE AGENT - DEVICE TIER BREAKDOWN")
    print("=" * 90)

    client = EnhancedAmplitudeAnalyticsClient(api_key, secret_key)

    result = client.get_funnel_by_device_tier(hours=168)  # Last 7 days

    print("\n" + "=" * 90)
    print("📈 SIGNUP FUNNEL BY DEVICE TIER")
    print("=" * 90)

    if result['status'] == 'success':
        conversions = result['conversions']

        print(f"\nPeriod: {result['period']}")
        print("\n" + "-" * 90)
        print(f"{'Device Tier':<30} {'Views':<10} {'Entries':<10} {'Conversion':<15} {'Status':<10}")
        print("-" * 90)

        for tier in sorted(conversions.keys()):
            data = conversions[tier]
            views = data['views']
            entries = data['entries']
            percent = data['percent']
            status = "✅ Healthy" if data['status'] == 'healthy' else "⚠️ Anomaly"

            print(f"{tier:<30} {views:<10} {entries:<10} {percent:>7}% {status:<10}")

        print("\n" + "=" * 90)
        print("📊 SUMMARY")
        print("=" * 90)

        # Calculate overall
        total_views = sum(d['views'] for d in conversions.values())
        total_entries = sum(d['entries'] for d in conversions.values())
        overall_rate = (total_entries / total_views * 100) if total_views > 0 else 0

        print(f"\nTotal Views: {total_views}")
        print(f"Total Entries: {total_entries}")
        print(f"Overall Conversion: {overall_rate:.1f}%")
        print(f"Baseline: 52%")
        print(f"Gap: {overall_rate - 52:.1f}%")

        # Identify problem areas
        print(f"\n⚠️ DEVICE TIERS WITH CONVERSION < 45%:")
        problem_tiers = [t for t, d in conversions.items() if d['percent'] < 45]
        if problem_tiers:
            for tier in problem_tiers:
                data = conversions[tier]
                print(f"   • {tier}: {data['percent']}% (drop of {data['percent'] - 52:.1f}%)")
        else:
            print("   None - All tiers performing well!")

    else:
        print(f"\n❌ Error: {result['error']}")

    print("\n" + "=" * 90)


if __name__ == "__main__":
    main()
