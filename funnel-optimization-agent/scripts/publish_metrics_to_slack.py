#!/usr/bin/env python3
"""
📊 Publish Signin Metrics to Slack
Sends formatted analytics report to Slack channel
"""

import requests
import json
from datetime import datetime
import os


class SlackMetricsPublisher:
    """Publish metrics to Slack"""

    # Your actual data
    METRICS = {
        'SIGNIN_PAGE_VIEW': {
            'Android': 4183,
            'iOS': 361,
            'Web': 225,
            'total': 4769
        },
        'SIGNIN_PAGE_NUMBER_ENTERED': {
            'Android': 1733,
            'iOS': 169,
            'Web': 145,
            'total': 2047
        }
    }

    def __init__(self, webhook_url=None):
        """Initialize with Slack webhook URL"""
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')

    def publish_metrics(self):
        """Publish metrics to Slack"""
        if not self.webhook_url:
            print("❌ Error: SLACK_WEBHOOK_URL not provided")
            print("\nUsage:")
            print("  1. Option A: Set environment variable")
            print("     export SLACK_WEBHOOK_URL='https://hooks.slack.com/...'")
            print("     python3 publish_metrics_to_slack.py")
            print("\n  2. Option B: Provide directly")
            print("     python3 -c \"from publish_metrics_to_slack import *; SlackMetricsPublisher('YOUR_URL').publish_metrics()\"")
            print("\nGet your Slack webhook URL:")
            print("  1. Go to https://api.slack.com/apps")
            print("  2. Select your app")
            print("  3. Go to 'Incoming Webhooks'")
            print("  4. Click 'Add New Webhook to Workspace'")
            print("  5. Select channel and authorize")
            print("  6. Copy the webhook URL")
            return False

        message = self._format_message()
        return self._send_to_slack(message)

    def _format_message(self):
        """Format metrics as Slack message"""
        views = self.METRICS['SIGNIN_PAGE_VIEW']
        entries = self.METRICS['SIGNIN_PAGE_NUMBER_ENTERED']
        baseline = 0.52

        total_conv = entries['total'] / views['total'] * 100
        android_conv = entries['Android'] / views['Android'] * 100
        ios_conv = entries['iOS'] / views['iOS'] * 100
        web_conv = entries['Web'] / views['Web'] * 100

        # Calculate gaps
        expected_total = int(views['total'] * baseline)
        gap = expected_total - entries['total']

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Signin Funnel Metrics - Mobile Number Entry",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Views:*\n{views['total']:,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Entries:*\n{entries['total']:,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Conversion:*\n{total_conv:.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Baseline:*\n52.0%"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📱 By Platform:*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Android* (87.7% of traffic)\n{views['Android']:,} views → {entries['Android']:,} entries\n{android_conv:.1f}% conversion ⚠️ (-10.6% vs baseline)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*iOS* (7.6% of traffic)\n{views['iOS']:,} views → {entries['iOS']:,} entries\n{ios_conv:.1f}% conversion ⚠️ (-5.2% vs baseline)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Web* (4.7% of traffic)\n{views['Web']:,} views → {entries['Web']:,} entries\n{web_conv:.1f}% conversion ✅ (+12.4% vs baseline)"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 Opportunity:*\nAt 52% baseline, you should have {expected_total:,} conversions\nYou have {entries['total']:,}\n*Gap: {gap} users ({gap/views['total']*100:.1f}% of traffic)*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 Key Insights:*\n• Web is your best performer (64.4%) - learn from it\n• Android dominates traffic (87.7%) - fix Android = fix 88% of funnel\n• Low/Mid-tier Android needs optimization\n• iOS performing reasonably (46.8%)\n\n*Next: Export Android by device model from Amplitude*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                ]
            }
        ]

        return {"blocks": blocks}

    def _send_to_slack(self, message):
        """Send message to Slack webhook"""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                print("✅ Message sent to Slack successfully!")
                print(f"   Webhook: {self.webhook_url[:50]}...")
                print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
                return True
            else:
                print(f"❌ Error: Slack API returned {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error sending to Slack: {str(e)}")
            return False

    def show_preview(self):
        """Show preview of the message (for testing)"""
        print("\n" + "=" * 100)
        print("📋 SLACK MESSAGE PREVIEW")
        print("=" * 100)

        views = self.METRICS['SIGNIN_PAGE_VIEW']
        entries = self.METRICS['SIGNIN_PAGE_NUMBER_ENTERED']
        baseline = 0.52

        total_conv = entries['total'] / views['total'] * 100
        android_conv = entries['Android'] / views['Android'] * 100
        ios_conv = entries['iOS'] / views['iOS'] * 100
        web_conv = entries['Web'] / views['Web'] * 100

        expected_total = int(views['total'] * baseline)
        gap = expected_total - entries['total']

        preview = f"""
📊 Signin Funnel Metrics - Mobile Number Entry

Total Views: {views['total']:,}
Total Entries: {entries['total']:,}
Overall Conversion: {total_conv:.1f}%
Baseline: 52.0%

─────────────────────────────────────────────

📱 By Platform:

Android (87.7% of traffic)
  {views['Android']:,} views → {entries['Android']:,} entries
  {android_conv:.1f}% conversion ⚠️ (-10.6% vs baseline)

iOS (7.6% of traffic)
  {views['iOS']:,} views → {entries['iOS']:,} entries
  {ios_conv:.1f}% conversion ⚠️ (-5.2% vs baseline)

Web (4.7% of traffic)
  {views['Web']:,} views → {entries['Web']:,} entries
  {web_conv:.1f}% conversion ✅ (+12.4% vs baseline)

─────────────────────────────────────────────

💡 Opportunity:

At 52% baseline, you should have {expected_total:,} conversions
You have {entries['total']:,}
Gap: {gap} users ({gap/views['total']*100:.1f}% of traffic)

─────────────────────────────────────────────

🎯 Key Insights:

• Web is your best performer (64.4%) - learn from it
• Android dominates traffic (87.7%) - fix Android = fix 88% of funnel
• Low/Mid-tier Android needs optimization
• iOS performing reasonably (46.8%)

Next: Export Android by device model from Amplitude

Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
"""
        print(preview)
        print("=" * 100)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                    📊 PUBLISH SIGNIN METRICS TO SLACK                                         ║
║                                                                                                ║
║  Send your analytics data to Slack for team visibility                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)

    # Check for webhook URL
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not webhook_url:
        print("\n❌ SLACK_WEBHOOK_URL not set\n")
        print("Get your Slack webhook URL:")
        print("  1. Go to https://api.slack.com/apps")
        print("  2. Select your app (or create new)")
        print("  3. Click 'Incoming Webhooks' in left menu")
        print("  4. Turn on 'Activate Incoming Webhooks'")
        print("  5. Click 'Add New Webhook to Workspace'")
        print("  6. Select channel and click 'Allow'")
        print("  7. Copy the webhook URL\n")

        webhook_url = input("Paste your Slack webhook URL (or press Enter to skip): ").strip()

        if not webhook_url:
            print("\n⚠️  Showing preview instead:\n")
            publisher = SlackMetricsPublisher()
            publisher.show_preview()
            return

    # Create publisher and send
    publisher = SlackMetricsPublisher(webhook_url)

    # Show preview first
    publisher.show_preview()

    print("\n")
    proceed = input("Send this message to Slack? (yes/no): ").strip().lower()

    if proceed == 'yes' or proceed == 'y':
        success = publisher.publish_metrics()
        if success:
            print("\n✅ Done! Check your Slack channel.")
    else:
        print("⏭️  Skipped. No message sent.")


if __name__ == "__main__":
    main()
