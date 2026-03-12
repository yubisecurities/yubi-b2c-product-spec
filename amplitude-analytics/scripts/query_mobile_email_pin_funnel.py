#!/usr/bin/env python3
"""
📊 Query Mobile Verification → Email Verification → PIN Setup funnel
Show conversion rates across device tiers
"""

import os
import base64
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

class DeviceCategorizer:
    """Categorizes devices into tiers"""

    LOW_TIER_KEYWORDS = [
        'j2', 'j3', 'j4', 'j5', 'j6', 'j7',
        'redmi 6', 'redmi 7', 'redmi 8', 'redmi 9',
        'realme c', 'realme 3', 'realme 5',
        'moto e', 'moto e4', 'moto e5',
        'infinix', 'tecno', 'nokia 1', 'nokia 2'
    ]

    MID_TIER_KEYWORDS = [
        'samsung a', 'samsung m', 'samsung note',
        'poco', 'poco x2', 'poco x3',
        'redmi note', 'redmi k30',
        'realme 6', 'realme 7', 'realme 8',
        'oneplus nord', 'oneplus 7', 'oneplus 8',
        'moto g', 'moto g10', 'moto g20',
        'vivo v17', 'vivo v19', 'vivo v20',
        'oppo f', 'oppo a'
    ]

    PREMIUM_KEYWORDS = [
        'samsung s22', 'samsung s23', 'samsung s24',
        'samsung s ultra',
        'oneplus 9', 'oneplus 10', 'oneplus 11',
        'pixel 6', 'pixel 7', 'pixel 8',
        'poco f'
    ]

    @staticmethod
    def categorize(device_model: str, os_name: str) -> str:
        if not device_model:
            return f"{os_name} - Unknown"
        device_lower = device_model.lower()
        if 'ios' in os_name.lower() or 'iphone' in device_lower or 'ipad' in device_lower:
            return "iOS"
        if 'web' in os_name.lower() or 'windows' in device_lower or 'mac' in device_lower:
            return "Web"
        if any(keyword in device_lower for keyword in DeviceCategorizer.PREMIUM_KEYWORDS):
            return "Premium Android"
        elif any(keyword in device_lower for keyword in DeviceCategorizer.MID_TIER_KEYWORDS):
            return "Mid-tier Android"
        elif any(keyword in device_lower for keyword in DeviceCategorizer.LOW_TIER_KEYWORDS):
            return "Low-tier Android"
        else:
            return "Mid-tier Android (Unknown)"


class FunnelAnalyzer:
    """Analyze funnel across device tiers"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://amplitude.com/api/2"
        self.auth_string = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth_string}',
            'Accept': 'application/json'
        }

    def find_events(self):
        """Find available events in Amplitude"""
        print("\n🔍 Searching for funnel events in Amplitude...\n")

        endpoint = f"{self.base_url}/events/list"

        try:
            response = requests.get(
                endpoint,
                params={'limit': 1000},
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])

                # Filter for funnel-related events
                print(f"Total events in Amplitude: {len(events)}\n")

                funnel_keywords = [
                    'mobile', 'verification', 'verify',
                    'email', 'pin', 'setup', 'onboard',
                    'otp', 'password', 'kyc', 'aadhar', 'pan',
                    'success', 'complete', 'finish'
                ]

                relevant_events = []
                for event in events:
                    event_name = event.get('name', '').lower()
                    if any(keyword in event_name for keyword in funnel_keywords):
                        relevant_events.append({
                            'name': event.get('name'),
                            'totals': event.get('totals', 0)
                        })

                # Sort by popularity
                relevant_events.sort(key=lambda x: x['totals'], reverse=True)

                print("📊 FUNNEL-RELATED EVENTS (Top 30):\n")
                print(f"{'Event Name':<60} {'Count':<10}")
                print("─" * 70)

                for i, event in enumerate(relevant_events[:30], 1):
                    print(f"{i:2}. {event['name']:<57} {event['totals']:<10}")

                return [e['name'] for e in relevant_events[:30]]
            else:
                print(f"Error: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error fetching events: {str(e)}")
            return []

    def query_funnel(self, events: list, hours: int = 168):
        """Query a funnel across device tiers"""

        print(f"\n\n{'='*100}")
        print(f"📈 FUNNEL ANALYSIS: {' → '.join(events)}")
        print(f"{'='*100}\n")

        # Fetch data for each event
        event_data = {}
        for event_name in events:
            print(f"📡 Fetching {event_name}...")

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
                    count = len(data.get('data', []))
                    print(f"   ✓ {count} events received")
                    event_data[event_name] = data.get('data', [])
                else:
                    print(f"   ✗ Status {response.status_code}")
                    event_data[event_name] = []

            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                event_data[event_name] = []

        # Process funnel by device tier
        print(f"\n{'─'*100}")
        print("📱 DEVICE TIER BREAKDOWN")
        print(f"{'─'*100}\n")

        self._analyze_by_device_tier(event_data, events)

    def _analyze_by_device_tier(self, event_data: dict, events: list):
        """Analyze funnel by device tier"""

        # Track users at each step per device tier
        device_tiers = {}

        for event_name, raw_events in event_data.items():
            # Group by device tier (using user sets)
            tier_users = defaultdict(set)

            for event in raw_events:
                # Try to extract device info
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

                tier = DeviceCategorizer.categorize(device_model, os_name)
                user_id = event.get('user_id') or event.get('amplitude_id')

                if user_id:
                    tier_users[tier].add(user_id)

            # Store for this event
            device_tiers[event_name] = {tier: len(users) for tier, users in tier_users.items()}

        # Build funnel table
        if not device_tiers:
            print("⚠️ No device data available from Amplitude API")
            print("   (Amplitude REST API limitation: doesn't return raw event device properties)")
            return

        # Get all tiers
        all_tiers = set()
        for tier_dict in device_tiers.values():
            all_tiers.update(tier_dict.keys())

        all_tiers = sorted(all_tiers)

        # Print header
        header = "Device Tier".ljust(25)
        for event in events:
            header += f" {event[:15]:<15}"
        header += " Overall Conv"
        print(header)
        print("─" * (len(header) + 20))

        # Print rows
        for tier in all_tiers:
            row = tier.ljust(25)
            values = []

            for event in events:
                count = device_tiers.get(event, {}).get(tier, 0)
                values.append(count)
                row += f" {count:<15}"

            # Calculate conversion
            if values and values[0] > 0:
                conversion = values[-1] / values[0] * 100
                row += f" {conversion:.1f}%"

            print(row)

        # Print summary
        print("─" * (len(header) + 20))
        total_row = "TOTAL".ljust(25)
        totals = []
        for event in events:
            total = sum(device_tiers.get(event, {}).values())
            totals.append(total)
            total_row += f" {total:<15}"

        if totals and totals[0] > 0:
            overall_conv = totals[-1] / totals[0] * 100
            total_row += f" {overall_conv:.1f}%"

        print(total_row)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║           📊 MOBILE VERIFICATION → EMAIL → PIN SETUP FUNNEL ANALYSIS                         ║
║                                                                                                ║
║  Queries Amplitude for your verification/onboarding funnel and breaks down by device tier     ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)

    # Credentials
    api_key = os.getenv("AMPLITUDE_API_KEY", "")  # Set AMPLITUDE_API_KEY env var
    secret_key = os.getenv("AMPLITUDE_SECRET_KEY", "")  # Set AMPLITUDE_SECRET_KEY env var

    analyzer = FunnelAnalyzer(api_key, secret_key)

    # Step 1: Find available events
    events = analyzer.find_events()

    if events:
        # Step 2: Ask which events to analyze
        print(f"\n\n{'='*100}")
        print("🎯 WHICH EVENTS DO YOU WANT TO ANALYZE?")
        print(f"{'='*100}\n")

        print("Common funnel patterns:")
        print("1. Mobile Verification → Email Verification → PIN Setup Success")
        print("2. KYC Flow: Aadhar Start → Pan Upload → Verification Success")
        print("3. Onboarding: Initial Screen → Account Setup → First Transaction")

        print("\n\nSearching for these events in your account...\n")

        # Look for common patterns
        mobile_events = [e for e in events if any(x in e.lower() for x in ['mobile', 'phone', 'otp', 'verify'])]
        email_events = [e for e in events if 'email' in e.lower()]
        pin_events = [e for e in events if any(x in e.lower() for x in ['pin', 'password', 'setup', 'success'])]
        kyc_events = [e for e in events if any(x in e.lower() for x in ['kyc', 'aadhar', 'pan', 'digilocker'])]

        print("📱 Mobile/Phone/OTP Events:")
        for i, event in enumerate(mobile_events[:5], 1):
            print(f"   {i}. {event}")

        print("\n📧 Email Events:")
        for i, event in enumerate(email_events[:5], 1):
            print(f"   {i}. {event}")

        print("\n🔐 PIN/Password/Setup Events:")
        for i, event in enumerate(pin_events[:5], 1):
            print(f"   {i}. {event}")

        print("\n🪪 KYC/Aadhar/Pan Events:")
        for i, event in enumerate(kyc_events[:5], 1):
            print(f"   {i}. {event}")

        # Try common funnel
        print(f"\n\n{'='*100}")
        print("🔄 ATTEMPTING TO QUERY COMMON FUNNELS...")
        print(f"{'='*100}\n")

        # Funnel 1: Mobile → Email → PIN
        funnel1 = [
            e for e in events
            if 'mobile' in e.lower() and 'verified' in e.lower()
        ]
        if funnel1:
            email_funnel = [e for e in events if 'email' in e.lower() and 'verified' in e.lower()]
            pin_funnel = [e for e in events if any(x in e.lower() for x in ['pin', 'password']) and 'success' in e.lower()]

            if email_funnel and pin_funnel:
                analyzer.query_funnel([funnel1[0], email_funnel[0], pin_funnel[0]])

        # Funnel 2: KYC flow
        kyc_start = [e for e in kyc_events if any(x in e.lower() for x in ['start', 'initial', 'screen'])]
        kyc_complete = [e for e in kyc_events if any(x in e.lower() for x in ['success', 'complete', 'verified'])]

        if kyc_start and kyc_complete:
            analyzer.query_funnel([kyc_start[0], kyc_complete[0]])

    else:
        print("⚠️ Could not fetch events from Amplitude")
        print("\nTo manually specify events, edit this script and set:")
        print('  analyzer.query_funnel(["EVENT_1", "EVENT_2", "EVENT_3"])')


if __name__ == "__main__":
    main()
