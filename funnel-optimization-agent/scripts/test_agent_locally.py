#!/usr/bin/env python3
"""
🔬 LOCAL AGENT TEST - Full agent simulation with your real Amplitude data
Tests the exact logic that will run on AWS Lambda every 48 hours
"""

import os
import json
import base64
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple


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


class AnomalyDetector:
    """Detects anomalies in conversion rates"""

    BASELINE_CONVERSION = 0.52  # 52%

    # Thresholds for anomaly levels
    CRITICAL_THRESHOLD = 0.35   # < 35% = CRITICAL
    HIGH_THRESHOLD = 0.45       # < 45% = HIGH
    MEDIUM_THRESHOLD = 0.50     # < 50% = MEDIUM

    @staticmethod
    def detect(conversion_rate: float) -> Tuple[str, str]:
        """Detect anomaly severity and return (severity, emoji)"""
        if conversion_rate < AnomalyDetector.CRITICAL_THRESHOLD:
            return "CRITICAL", "🔴"
        elif conversion_rate < AnomalyDetector.HIGH_THRESHOLD:
            return "HIGH", "⚠️"
        elif conversion_rate < AnomalyDetector.MEDIUM_THRESHOLD:
            return "MEDIUM", "⚡"
        else:
            return "HEALTHY", "✅"


class LocalAgentTest:
    """Full agent test with real Amplitude data"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://amplitude.com/api/2"
        self.auth_string = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth_string}',
            'Accept': 'application/json'
        }

    def run_test(self, hours: int = 168):
        """Run the full agent test"""
        print("\n" + "=" * 100)
        print("🔬 LOCAL AGENT TEST - Testing agent logic with real Amplitude data")
        print("=" * 100)

        # Fetch real data
        print("\n🔄 Step 1: Fetching events from Amplitude...")
        view_data = self._fetch_events('SIGNIN_PAGE_VIEW', hours)
        enter_data = self._fetch_events('SIGNIN_PAGE_NUMBER_ENTERED', hours)

        if not view_data or not enter_data:
            print("⚠️ Could not fetch raw events from Amplitude (API limitation)")
            print("   → Using demo data for testing agent logic\n")
            self._run_with_demo_data()
            return

        # Process data
        print("\n📊 Step 2: Processing events...")
        conversions = self._process_events(view_data, enter_data)

        # Detect anomalies
        print("\n🚨 Step 3: Detecting anomalies...")
        anomalies = self._detect_anomalies(conversions)

        # Display results
        self._display_results(conversions, anomalies)

    def _fetch_events(self, event_name: str, hours: int) -> List[Dict]:
        """Fetch events from Amplitude"""
        endpoint = f"{self.base_url}/events/list"

        params = {
            'event': event_name,
            'limit': 10000
        }

        try:
            print(f"   → Querying {event_name}...")
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])
                print(f"     ✓ Received {len(events)} events")
                return events
            else:
                print(f"     ✗ Status {response.status_code}")
                return []

        except Exception as e:
            print(f"     ✗ Error: {str(e)}")
            return []

    def _process_events(self, view_events: List[Dict], enter_events: List[Dict]) -> Dict:
        """Process events and calculate conversions by device tier"""

        # Group by device tier
        view_by_tier = defaultdict(set)
        enter_by_tier = defaultdict(set)

        for event in view_events:
            tier = self._categorize_event(event)
            user_id = event.get('user_id') or event.get('amplitude_id')
            if user_id:
                view_by_tier[tier].add(user_id)

        for event in enter_events:
            tier = self._categorize_event(event)
            user_id = event.get('user_id') or event.get('amplitude_id')
            if user_id:
                enter_by_tier[tier].add(user_id)

        # Calculate conversions
        conversions = {}
        all_tiers = set(list(view_by_tier.keys()) + list(enter_by_tier.keys()))

        for tier in sorted(all_tiers):
            views = len(view_by_tier.get(tier, set()))
            entries = len(enter_by_tier.get(tier, set()))
            conversion = entries / views if views > 0 else 0

            conversions[tier] = {
                'views': views,
                'entries': entries,
                'conversion': conversion,
                'percent': round(conversion * 100, 1)
            }

        return conversions

    def _categorize_event(self, event: Dict) -> str:
        """Extract device info from event and categorize"""
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
        return DeviceCategorizer.categorize(device_model, os_name)

    def _detect_anomalies(self, conversions: Dict) -> List[Dict]:
        """Detect anomalies in conversion data"""
        anomalies = []

        for tier, data in conversions.items():
            conversion = data['conversion']
            severity, emoji = AnomalyDetector.detect(conversion)

            if severity != "HEALTHY":
                drop_percent = (AnomalyDetector.BASELINE_CONVERSION - conversion) * 100
                anomalies.append({
                    'tier': tier,
                    'conversion': conversion,
                    'drop': drop_percent,
                    'severity': severity,
                    'emoji': emoji
                })

        return sorted(anomalies, key=lambda x: x['drop'], reverse=True)

    def _display_results(self, conversions: Dict, anomalies: List[Dict]):
        """Display test results"""
        print("\n" + "─" * 100)
        print("📈 RESULTS - Device Tier Conversion Breakdown")
        print("─" * 100)

        total_views = sum(d['views'] for d in conversions.values())
        total_entries = sum(d['entries'] for d in conversions.values())
        overall_conversion = total_entries / total_views if total_views > 0 else 0

        print(f"\nTotal Users: {total_views}")
        print(f"Total Conversions: {total_entries}")
        print(f"Overall Rate: {overall_conversion*100:.1f}%")
        print(f"Baseline: {AnomalyDetector.BASELINE_CONVERSION*100:.1f}%")
        print(f"Gap: {(overall_conversion - AnomalyDetector.BASELINE_CONVERSION)*100:.1f}%")

        print(f"\n{'Device Tier':<25} {'Views':<10} {'Conv':<10} {'Rate':<10} {'vs Base':<12} {'Status':<12}")
        print("─" * 100)

        for tier in sorted(conversions.keys()):
            data = conversions[tier]
            severity, emoji = AnomalyDetector.detect(data['conversion'])
            drop = (AnomalyDetector.BASELINE_CONVERSION - data['conversion']) * 100

            print(f"{tier:<25} {data['views']:<10} {data['entries']:<10} "
                  f"{data['percent']:>7}% {drop:>+7.1f}% {emoji} {severity:<8}")

        # Show anomalies
        if anomalies:
            print("\n" + "─" * 100)
            print("🚨 ANOMALIES DETECTED")
            print("─" * 100)
            for i, anom in enumerate(anomalies, 1):
                print(f"\n{i}. {anom['emoji']} {anom['tier']} ({anom['severity']})")
                print(f"   Conversion: {anom['conversion']*100:.1f}%")
                print(f"   Drop from baseline: {anom['drop']:.1f}%")

        # Show what would be sent to Slack
        print("\n" + "─" * 100)
        print("💬 SLACK ALERT THAT WOULD BE SENT")
        print("─" * 100)
        self._show_slack_alert(conversions, anomalies)

    def _show_slack_alert(self, conversions: Dict, anomalies: List[Dict]):
        """Format and show Slack alert"""
        alert = f"""
🚨 SIGNUP FUNNEL ANOMALY ALERT

📊 Overall Metrics:
   Baseline: 52.0%
   Current: {sum(c['entries'] for c in conversions.values()) / sum(c['views'] for c in conversions.values()) * 100:.1f}%
   Status: {'✅ HEALTHY' if not anomalies else '⚠️ ANOMALIES DETECTED'}

📱 Device Breakdown:
"""
        for tier in sorted(conversions.keys()):
            data = conversions[tier]
            severity, emoji = AnomalyDetector.detect(data['conversion'])
            alert += f"   {emoji} {tier}: {data['percent']}%\n"

        if anomalies:
            alert += f"\n🔴 TOP ISSUES:\n"
            for anom in anomalies[:3]:
                alert += f"   • {anom['tier']}: {anom['drop']:.1f}% drop\n"

        print(alert)

    def _run_with_demo_data(self):
        """Run agent test with demo data"""
        # Demo data based on your actual metrics
        conversions = {
            'Low-tier Android': {'views': 240, 'entries': 57, 'conversion': 0.238, 'percent': 23.8},
            'Mid-tier Android': {'views': 280, 'entries': 107, 'conversion': 0.382, 'percent': 38.2},
            'Premium Android': {'views': 60, 'entries': 42, 'conversion': 0.700, 'percent': 70.0},
            'iOS': {'views': 82, 'entries': 18, 'conversion': 0.220, 'percent': 22.0},
            'Web': {'views': 21, 'entries': 4, 'conversion': 0.190, 'percent': 19.0},
        }

        anomalies = self._detect_anomalies(conversions)
        self._display_results(conversions, anomalies)


def main():
    # Get credentials
    api_key = os.getenv("AMPLITUDE_API_KEY", "")  # Set AMPLITUDE_API_KEY env var
    secret_key = os.getenv("AMPLITUDE_SECRET_KEY", "")  # Set AMPLITUDE_SECRET_KEY env var

    print("""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                  🔬 TESTING SIGNUP FUNNEL MONITORING AGENT LOCALLY                            ║
║                                                                                                ║
║  This script tests the exact logic that will run on AWS Lambda every 48 hours.                ║
║  It will:                                                                                      ║
║    1. Fetch events from Amplitude (real data)                                                 ║
║    2. Categorize users by device tier                                                         ║
║    3. Calculate conversion rates per tier                                                     ║
║    4. Detect anomalies using configurable thresholds                                          ║
║    5. Show what would be sent to Slack                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)

    # Create and run test
    test = LocalAgentTest(api_key, secret_key)
    test.run_test(hours=168)  # Last 7 days

    print("\n" + "=" * 100)
    print("✨ WHAT THIS MEANS FOR YOUR DEPLOYMENT")
    print("=" * 100)
    print("""
✅ This agent will run automatically on AWS Lambda every 48 hours:

1. Query Amplitude for last 48 hours of events
2. Categorize 683+ users by device tier
3. Calculate conversion rates per tier
4. Detect anomalies vs 52% baseline
5. Send Slack alert with exact issues

📌 To deploy to production:

   Step 1: Get credentials
   • Claude API Key: https://console.anthropic.com
   • Slack Webhook: https://api.slack.com/apps

   Step 2: Deploy to Lambda
   • Run: ./deploy_lambda.sh (from AGENT_IMPLEMENTATION.md)
   • Lambda runs automatically every 48 hours (cron: 0 2 */2 * ? *)

   Step 3: You're done!
   • Slack alerts every 2 days
   • Cost: ~$13-20/month
   • Time saved: Hours per week

📖 Documentation:
   • DEPLOYMENT_READY.md - Full deployment guide
   • AGENT_IMPLEMENTATION.md - Lambda code
   • DEVICE_TIER_BREAKDOWN_GUIDE.md - Device analysis
    """)
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
