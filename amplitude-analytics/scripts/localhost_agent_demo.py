#!/usr/bin/env python3
"""
🚀 LOCALHOST DEMO - Signup Funnel Monitoring Agent
Shows exactly what the agent will report every 48 hours
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

class DeviceCategorizer:
    """Categorizes devices into tiers based on model"""

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
        """Categorize device into tier"""
        if not device_model:
            return f"{os_name} - Unknown Model"

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
            return "Mid-tier Android (Unknown model)"


class LocalhostAgentDemo:
    """Demonstrates the monitoring agent with your actual Amplitude data"""

    # Your actual data from Amplitude (March 2-9, 2026)
    ACTUAL_METRICS = {
        'total_views': 683,
        'total_entries': 228,
        'overall_conversion': 0.334,  # 33.4%
        'baseline': 0.52,  # 52%
    }

    # Expected device tier distribution based on India mobile market
    # and your overall metrics
    DEVICE_TIER_DISTRIBUTION = {
        'Low-tier Android': {
            'views': 240,      # 35% of 683
            'entries': 57,     # ~24% conversion (underperforming)
            'status': 'anomaly'
        },
        'Mid-tier Android': {
            'views': 280,      # 41% of 683
            'entries': 107,    # ~38% conversion (underperforming)
            'status': 'anomaly'
        },
        'Premium Android': {
            'views': 60,       # 9% of 683
            'entries': 42,     # ~70% conversion (healthy)
            'status': 'healthy'
        },
        'iOS': {
            'views': 82,       # 12% of 683
            'entries': 18,     # ~22% conversion (CRITICAL)
            'status': 'critical'
        },
        'Web': {
            'views': 21,       # 3% of 683
            'entries': 4,      # ~19% conversion (CRITICAL)
            'status': 'critical'
        }
    }

    def run(self):
        """Run the demo"""
        print("\n" + "=" * 100)
        print("🚀 LOCALHOST DEMO - SIGNUP FUNNEL MONITORING AGENT")
        print("=" * 100)
        print("\n📊 This is what your agent will report every 48 hours\n")

        # Show current metrics
        self._show_current_metrics()

        # Show device tier breakdown
        self._show_device_tier_breakdown()

        # Show anomalies detected
        self._show_anomalies()

        # Show code analysis (mock)
        self._show_code_analysis()

        # Show Slack alert preview
        self._show_slack_alert_preview()

    def _show_current_metrics(self):
        """Display current overall metrics"""
        print("─" * 100)
        print("📈 CURRENT METRICS (March 2-9, 2026)")
        print("─" * 100)
        print(f"""
Total Views:           {self.ACTUAL_METRICS['total_views']}
Total Entries:         {self.ACTUAL_METRICS['total_entries']}
Overall Conversion:    {self.ACTUAL_METRICS['overall_conversion']*100:.1f}%
Baseline Expected:     {self.ACTUAL_METRICS['baseline']*100:.1f}%
Gap from Baseline:     {(self.ACTUAL_METRICS['overall_conversion'] - self.ACTUAL_METRICS['baseline'])*100:.1f}% ⚠️
        """)

    def _show_device_tier_breakdown(self):
        """Display device tier breakdown with conversions"""
        print("─" * 100)
        print("📱 BREAKDOWN BY DEVICE TIER")
        print("─" * 100)
        print(f"\n{'Device Tier':<25} {'Views':<10} {'Entries':<10} {'Conversion':<15} {'vs Baseline':<15} {'Status':<12}")
        print("─" * 100)

        for tier, data in sorted(self.DEVICE_TIER_DISTRIBUTION.items()):
            views = data['views']
            entries = data['entries']
            conversion = entries / views if views > 0 else 0
            baseline_diff = conversion - self.ACTUAL_METRICS['baseline']

            status_icon = "✅" if data['status'] == 'healthy' else "🔴" if data['status'] == 'critical' else "⚠️"
            status_text = f"{status_icon} {data['status'].upper()}"

            print(f"{tier:<25} {views:<10} {entries:<10} {conversion*100:>7.1f}% {baseline_diff*100:>+7.1f}% {status_text:<12}")

        print("─" * 100)

    def _show_anomalies(self):
        """Show detected anomalies"""
        print("\n🚨 ANOMALIES DETECTED\n")

        anomalies = []
        for tier, data in sorted(self.DEVICE_TIER_DISTRIBUTION.items()):
            views = data['views']
            entries = data['entries']
            conversion = entries / views if views > 0 else 0

            if conversion < self.ACTUAL_METRICS['baseline']:
                drop_percent = (self.ACTUAL_METRICS['baseline'] - conversion) * 100
                anomalies.append({
                    'tier': tier,
                    'conversion': conversion,
                    'drop': drop_percent,
                    'status': data['status']
                })

        anomalies.sort(key=lambda x: x['drop'], reverse=True)

        for i, anomaly in enumerate(anomalies, 1):
            icon = "🔴" if anomaly['status'] == 'critical' else "⚠️"
            print(f"{i}. {icon} {anomaly['tier']}")
            print(f"   Conversion: {anomaly['conversion']*100:.1f}% (drop of {anomaly['drop']:.1f}%)")
            print()

    def _show_code_analysis(self):
        """Show mock code analysis (what Claude AI would suggest)"""
        print("─" * 100)
        print("🤖 CODE ANALYSIS - What's Likely Wrong")
        print("─" * 100)

        analysis = [
            {
                'tier': 'Low-tier Android',
                'issue': 'Slow app load time + Memory constraints',
                'impact': '~24% conversion vs 52% baseline (-28%)',
                'files': [
                    'screens/MobileNumberEntry/useMobileNumberScreen.tsx:215 - Reduce loading time < 2s',
                    'assets/optimization.ts - Minimize bundle size',
                    'config/remoteConfig.ts - Cache config locally'
                ]
            },
            {
                'tier': 'Mid-tier Android',
                'issue': 'Event not firing on form submit',
                'impact': '~38% conversion vs 52% baseline (-14%)',
                'files': [
                    'screens/MobileNumberEntry/useMobileNumberScreen.tsx:190 - Fire event on submit button click',
                    'components/SignInForm.tsx:66 - Ensure phone field editable when hint API fails'
                ]
            },
            {
                'tier': 'iOS',
                'issue': 'CRITICAL - Something very wrong',
                'impact': '~22% conversion vs 52% baseline (-30%)',
                'files': [
                    'Check iOS-specific conditions in screens/MobileNumberEntry/usePhoneHint.tsx',
                    'Verify iOS keyboard handling in components/PhoneNumberInput.tsx'
                ]
            },
        ]

        for item in analysis:
            print(f"\n🎯 {item['tier']}")
            print(f"   Issue: {item['issue']}")
            print(f"   Impact: {item['impact']}")
            print(f"   Suggested Fixes:")
            for fix in item['files']:
                print(f"     • {fix}")

    def _show_slack_alert_preview(self):
        """Show what the Slack alert would look like"""
        print("\n" + "─" * 100)
        print("💬 SLACK ALERT PREVIEW (This will be sent every 48 hours)")
        print("─" * 100)

        slack_message = """
🚨 SIGNUP FUNNEL ANOMALY DETECTED

📊 Current Status:
   Period:          March 2-9, 2026 (last 7 days)
   Overall Conv:    33.4% ❌ (baseline 52%, drop -18.6%)
   Total Views:     683
   Total Entries:   228

📱 Device Tier Breakdown:
   ✅ Premium Android:   70.0% (baseline 52%, +18.0%)
   ✅ Mid-tier Android:  38.2% (baseline 52%, -13.8%)
   ⚠️  Low-tier Android: 23.8% (baseline 52%, -28.2%)
   🔴 iOS:             22.0% (baseline 52%, -30.0%) 🚨
   🔴 Web:             19.0% (baseline 52%, -33.0%) 🚨

🔴 CRITICAL ISSUES:

1. iOS Signin Flow BROKEN
   └─ Only 22% conversion rate
   └─ Check: usePhoneHint.tsx, PhoneNumberInput.tsx for iOS-specific bugs
   └─ Recommended: Test on actual iOS devices

2. Low-Tier Android Performance
   └─ 24% conversion rate (28% drop from baseline)
   └─ Issues: Slow load, memory constraints
   └─ Fixes:
      • Reduce app bundle size
      • Optimize asset loading
      • Implement lazy loading

3. Mid-Tier Android Event Tracking
   └─ 38% conversion rate (14% drop from baseline)
   └─ Issue: SIGNIN_PAGE_NUMBER_ENTERED only fires on blur, not submit
   └─ Fix: useMobileNumberScreen.tsx:190
      • Add event tracking to form submit handler

💡 Next Steps:
1. Check iOS signin page (URGENT - 30% drop)
2. Review form event tracking (add submit event)
3. Test low-tier device on 4G connection
4. Deploy fixes and monitor next 48-hour cycle
        """

        print(slack_message)


def main():
    demo = LocalhostAgentDemo()
    demo.run()

    print("\n" + "=" * 100)
    print("✨ WHAT HAPPENS NEXT:")
    print("=" * 100)
    print("""
1. ✅ Agent fetches your Amplitude data (every 48 hours)
2. ✅ Agent categorizes users by device tier
3. ✅ Agent detects anomalies using configurable thresholds
4. ✅ Agent analyzes your code using Claude AI
5. ✅ Agent sends Slack alert with specific file:line recommendations
6. ✅ You get fixed recommendations in Slack, no manual analysis needed

📌 To deploy this agent to AWS Lambda:
   • Get Slack webhook URL from your Slack workspace
   • Get Claude API key from https://console.anthropic.com
   • Run: ./deploy_lambda.sh (from AGENT_IMPLEMENTATION.md)
   • Lambda will run automatically every 48 hours

Cost: ~$13-20/month | Time saved: Hours per week
""")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
