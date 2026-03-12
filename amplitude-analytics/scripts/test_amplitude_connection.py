#!/usr/bin/env python3
"""
Test script to verify Amplitude API connection and fetch signup funnel data
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict
import requests

class AmplitudeAnalyticsClient:
    """Query Amplitude via REST API"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api2.amplitude.com"

    def get_conversion_data(self, hours: int = 48) -> Dict:
        """Get last N hours of signin funnel data from Amplitude"""

        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours)

        try:
            print(f"\n📊 Querying Amplitude for events from {from_date} to {to_date}")

            # Query SIGNIN_PAGE_VIEW events
            print("  → Fetching SIGNIN_PAGE_VIEW events...")
            view_data = self._query_events(
                'SIGNIN_PAGE_VIEW',
                from_date,
                to_date
            )

            # Query SIGNIN_PAGE_NUMBER_ENTERED events
            print("  → Fetching SIGNIN_PAGE_NUMBER_ENTERED events...")
            enter_data = self._query_events(
                'SIGNIN_PAGE_NUMBER_ENTERED',
                from_date,
                to_date
            )

            # Parse and calculate conversions by platform
            conversions = self._parse_amplitude_response(view_data, enter_data)

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

    def _query_events(self, event_name: str, from_date, to_date):
        """Query Amplitude for specific event with platform breakdown"""

        # Amplitude Events API endpoint
        endpoint = f"{self.base_url}/events"

        # Start and end times in milliseconds
        start_time = int(from_date.timestamp() * 1000)
        end_time = int(to_date.timestamp() * 1000)

        params = {
            'start': start_time,
            'end': end_time,
            'limit': 10000  # Max results per request
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }

        print(f"    POST {endpoint}")
        print(f"    Params: start={start_time}, end={end_time}, limit=10000")

        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=30
            )

            print(f"    Status: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            # Log response summary
            if 'data' in data:
                print(f"    ✓ Received {len(data.get('data', []))} events for {event_name}")

            return data

        except requests.exceptions.HTTPError as e:
            print(f"    ✗ HTTP Error: {e}")
            if response.text:
                print(f"    Response: {response.text[:200]}")
            return {'error': str(e)}
        except Exception as e:
            print(f"    ✗ Error querying Amplitude: {str(e)}")
            return {'error': str(e)}

    def _parse_amplitude_response(self, view_data, enter_data) -> Dict:
        """Parse Amplitude response and calculate platform-specific conversions"""

        conversions = {}

        try:
            # Extract platform-level data from Amplitude events
            view_by_platform = self._extract_platform_data(view_data, 'SIGNIN_PAGE_VIEW')
            enter_by_platform = self._extract_platform_data(enter_data, 'SIGNIN_PAGE_NUMBER_ENTERED')

            # Calculate conversion rates per platform
            for platform in ['Android', 'iOS', 'Web']:
                view_users = view_by_platform.get(platform, 0)
                enter_users = enter_by_platform.get(platform, 0)

                if view_users > 0:
                    conversion_rate = enter_users / view_users
                else:
                    conversion_rate = 0

                conversions[platform] = {
                    'views': view_users,
                    'entries': enter_users,
                    'rate': conversion_rate,
                    'percent': round(conversion_rate * 100, 1),
                    'status': 'healthy' if conversion_rate > 0.45 else 'anomaly'
                }

            return conversions

        except Exception as e:
            return {
                'error': f"Failed to parse Amplitude response: {str(e)}"
            }

    def _extract_platform_data(self, response, event_name):
        """Extract unique user counts by platform from Amplitude response"""

        platform_data = {'Android': 0, 'iOS': 0, 'Web': 0}

        try:
            # Amplitude returns events in the 'data' array
            if 'data' not in response:
                print(f"    Warning: No 'data' field in response for {event_name}")
                return platform_data

            events = response.get('data', [])
            print(f"    Parsing {len(events)} events...")

            # Group by platform property
            platform_users = {}

            for event in events:
                platform = self._detect_platform(event)

                if platform in platform_data:
                    user_id = event.get('user_id') or event.get('amplitude_id')
                    if user_id:
                        # Track unique users per platform
                        if platform not in platform_users:
                            platform_users[platform] = set()
                        platform_users[platform].add(user_id)

            # Convert sets to counts
            for platform, users in platform_users.items():
                platform_data[platform] = len(users)

            return platform_data

        except Exception as e:
            print(f"    Error extracting platform data: {str(e)}")
            return platform_data

    def _detect_platform(self, event):
        """Detect platform from Amplitude event properties"""

        # Check event properties
        event_props = event.get('event_properties', {}) or {}
        user_props = event.get('user_properties', {}) or {}

        # Look for OS or platform indicators
        os_name = (
            event_props.get('os_name') or
            event_props.get('operating_system') or
            user_props.get('os_name') or
            user_props.get('operating_system') or
            event.get('os_name') or
            event.get('os') or
            ''
        ).lower()

        if 'android' in os_name:
            return 'Android'
        elif 'ios' in os_name or 'iphone' in os_name or 'ipad' in os_name:
            return 'iOS'
        elif 'web' in os_name or 'windows' in os_name or 'mac' in os_name:
            return 'Web'
        else:
            # Default based on device_type if available
            device_type = event.get('device_type', '').lower()
            if 'phone' in device_type or 'mobile' in device_type:
                return 'Android'
            else:
                return 'Web'


def main():
    """Main test function"""

    print("=" * 70)
    print("🔗 AMPLITUDE API CONNECTION TEST")
    print("=" * 70)

    # Get credentials from environment
    api_key = os.getenv('AMPLITUDE_API_KEY')
    secret_key = os.getenv('AMPLITUDE_SECRET_KEY')

    if not api_key or not secret_key:
        print("\n❌ Error: Amplitude credentials not found in environment")
        print("\nSet these environment variables:")
        print("  export AMPLITUDE_API_KEY='your-api-key'")
        print("  export AMPLITUDE_SECRET_KEY='your-secret-key'")
        print("\nGet credentials from: https://analytics.amplitude.com/settings/api-keys")
        return

    print(f"\n✓ API Key found: {api_key[:10]}...")
    print(f"✓ Secret Key found: {secret_key[:10]}...")

    # Create client
    print("\n🔄 Initializing Amplitude client...")
    client = AmplitudeAnalyticsClient(api_key, secret_key)

    # Fetch data
    print("\n📡 Fetching signup funnel data (last 48 hours)...")
    result = client.get_conversion_data(hours=48)

    # Display results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)

    if result['status'] == 'error':
        print(f"\n❌ Error: {result['error']}")
        return

    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Period: {result['period']}")

    conversions = result.get('conversions', {})

    print("\n📈 CONVERSION RATES BY PLATFORM:")
    print("-" * 70)
    print(f"{'Platform':<12} {'Views':<10} {'Entries':<10} {'Rate':<10} {'Status':<12}")
    print("-" * 70)

    for platform in ['Android', 'iOS', 'Web']:
        data = conversions.get(platform, {})
        views = data.get('views', 0)
        entries = data.get('entries', 0)
        percent = data.get('percent', 0)
        status = data.get('status', 'unknown')

        status_icon = "✓" if status == 'healthy' else "⚠️"
        print(f"{platform:<12} {views:<10} {entries:<10} {percent:>7}% {status_icon} {status:<8}")

    print("\n" + "=" * 70)
    print("📄 FULL RESPONSE:")
    print("=" * 70)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
