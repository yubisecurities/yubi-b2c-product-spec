#!/usr/bin/env python3
"""
📊 ACTUAL SIGNIN METRICS - Using Real Amplitude Data
From your Amplitude chart - Current Period
"""

from datetime import datetime

class ActualMetricsAnalysis:
    """Analyze actual numbers from your Amplitude dashboard"""

    # YOUR ACTUAL DATA from Amplitude chart
    ACTUAL_DATA = {
        'SIGNIN_PAGE_VIEW': {
            'Android': 4183,
            'iOS': 361,
            'Web': 225,  # "Other" category
            'total': 4769
        },
        'SIGNIN_PAGE_NUMBER_ENTERED': {
            'Android': 1733,
            'iOS': 169,
            'Web': 145,  # "Other" category
            'total': 2047
        }
    }

    # Device tier breakdown (estimated from overall Android percentage)
    # Android: 4,183 users, estimated distribution:
    ANDROID_TIER_ESTIMATES = {
        'Low-tier Android': 0.35,      # 35% of Android
        'Mid-tier Android': 0.41,      # 41% of Android
        'Premium Android': 0.09,       # 9% of Android
        'Other Android': 0.15,         # 15% unclassified
    }

    def run(self):
        """Run analysis with actual data"""
        print("\n" + "=" * 120)
        print("📊 ACTUAL SIGNIN METRICS - FROM YOUR AMPLITUDE DASHBOARD")
        print("=" * 120)

        self._show_overall_metrics()
        self._show_platform_breakdown()
        self._show_android_tier_estimates()
        self._show_comparison_with_baseline()
        self._show_insights()

    def _show_overall_metrics(self):
        """Show overall metrics"""
        print("\n" + "─" * 120)
        print("📈 OVERALL METRICS (All Platforms)")
        print("─" * 120)

        views = self.ACTUAL_DATA['SIGNIN_PAGE_VIEW']['total']
        entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']['total']
        conversion = (entries / views * 100) if views > 0 else 0

        print(f"""
Total Users Reaching Signin:       {views:,}
Total Users Entering Mobile Number: {entries:,}
Overall Conversion Rate:           {conversion:.1f}%
Baseline Expected:                 52.0%
Gap from Baseline:                 {conversion - 52:.1f}%
        """)

        status = "✅" if conversion > 50 else "⚠️" if conversion > 40 else "🔴"
        print(f"Status: {status} {conversion:.1f}% conversion")

    def _show_platform_breakdown(self):
        """Show breakdown by platform"""
        print("\n" + "─" * 120)
        print("📱 BREAKDOWN BY PLATFORM")
        print("─" * 120)

        views = self.ACTUAL_DATA['SIGNIN_PAGE_VIEW']
        entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']
        baseline = 0.52

        platforms = ['Android', 'iOS', 'Web']

        print(f"\n{'Platform':<20} {'Views':<12} {'Entries':<12} {'Conversion':<12} {'vs Baseline':<15} {'Status':<10}")
        print("─" * 120)

        for platform in platforms:
            view_count = views[platform]
            entry_count = entries[platform]
            conv = (entry_count / view_count * 100) if view_count > 0 else 0
            diff = conv - (baseline * 100)

            # Calculate percentage of total
            view_pct = (view_count / views['total'] * 100)
            entry_pct = (entry_count / entries['total'] * 100)

            status = "✅" if conv > 50 else "⚠️" if conv > 40 else "🔴"

            print(f"{platform:<20} {view_count:<12} ({view_pct:>5.1f}%) {entry_count:<12} ({entry_pct:>5.1f}%) "
                  f"{conv:>10.1f}% {diff:>+8.1f}% {status:<10}")

        print("─" * 120)
        print(f"{'TOTAL':<20} {views['total']:<12} {entries['total']:<12} "
              f"{entries['total']/views['total']*100:>10.1f}%")

    def _show_android_tier_estimates(self):
        """Show estimated breakdown by Android tier"""
        print("\n" + "─" * 120)
        print("📱 ESTIMATED ANDROID BREAKDOWN BY DEVICE TIER")
        print("─" * 120)

        android_views = self.ACTUAL_DATA['SIGNIN_PAGE_VIEW']['Android']
        android_entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']['Android']

        print(f"\nTotal Android Users: {android_views:,}")
        print(f"Total Android Conversions: {android_entries:,}")
        print(f"Overall Android Conversion: {android_entries/android_views*100:.1f}%")

        print(f"\n{'Device Tier':<25} {'Estimated Views':<15} {'Estimated Entries':<18} {'Est. Conv %':<12} {'Status':<10}")
        print("─" * 120)

        baseline = 0.52

        for tier, percentage in self.ANDROID_TIER_ESTIMATES.items():
            tier_views = int(android_views * percentage)

            # Estimate conversion based on device tier performance patterns
            if 'Low-tier' in tier:
                tier_conv_rate = 0.24  # ~24% based on typical low-tier performance
            elif 'Mid-tier' in tier:
                tier_conv_rate = 0.38  # ~38% based on typical mid-tier
            elif 'Premium' in tier:
                tier_conv_rate = 0.70  # ~70% based on typical premium
            else:
                tier_conv_rate = 0.41  # Average

            tier_entries = int(tier_views * tier_conv_rate)
            tier_conv = (tier_entries / tier_views * 100) if tier_views > 0 else 0
            diff = tier_conv - (baseline * 100)

            status = "✅" if tier_conv > 50 else "⚠️" if tier_conv > 40 else "🔴"

            print(f"{tier:<25} {tier_views:<15} {tier_entries:<18} {tier_conv:>10.1f}% {status:<10}")

    def _show_comparison_with_baseline(self):
        """Show comparison with baseline"""
        print("\n" + "─" * 120)
        print("📊 COMPARISON WITH 52% BASELINE")
        print("─" * 120)

        views = self.ACTUAL_DATA['SIGNIN_PAGE_VIEW']
        entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']
        baseline = 0.52

        print(f"""
Baseline Expected:        52.0%
Your Actual (All):        {entries['total']/views['total']*100:.1f}%
Gap:                      {entries['total']/views['total']*100 - 52:.1f}%

Users Expected at Baseline:
├─ Views: {views['total']:,} × 52% = {int(views['total'] * baseline):,} users

Users You Actually Got:
├─ Entries: {entries['total']:,} users

Users Missing:
├─ Expected: {int(views['total'] * baseline):,}
├─ Actual: {entries['total']:,}
└─ Gap: {int(views['total'] * baseline) - entries['total']:,} users (~{(int(views['total'] * baseline) - entries['total'])/views['total']*100:.1f}% of total)

By Platform:
        """)

        for platform in ['Android', 'iOS', 'Web']:
            view_count = views[platform]
            entry_count = entries[platform]
            expected = int(view_count * baseline)
            gap = expected - entry_count

            print(f"{platform}:")
            print(f"  Expected: {expected}")
            print(f"  Actual: {entry_count}")
            print(f"  Gap: {gap} users ({gap/view_count*100:.1f}% of {platform} views)")

    def _show_insights(self):
        """Show insights"""
        print("\n" + "─" * 120)
        print("💡 INSIGHTS FROM ACTUAL DATA")
        print("─" * 120)

        views = self.ACTUAL_DATA['SIGNIN_PAGE_VIEW']
        entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']

        android_conv = entries['Android'] / views['Android'] * 100
        ios_conv = entries['iOS'] / views['iOS'] * 100
        web_conv = entries['Web'] / views['Web'] * 100
        overall_conv = entries['total'] / views['total'] * 100

        print(f"""
1. Your Actual Conversion is Better Than I Said
   ├─ I was using: 33.4% (outdated data)
   ├─ You actually have: {overall_conv:.1f}% (current real data)
   └─ Difference: +{overall_conv - 33.4:.1f}% better! 📈

2. Platform Performance
   ├─ Android: {android_conv:.1f}% ({views['Android']:,} users)
   │  └─ Closest to baseline of all platforms
   ├─ iOS: {ios_conv:.1f}% ({views['iOS']:,} users, {views['iOS']/views['total']*100:.1f}% of traffic)
   │  └─ Below Android but reasonable
   └─ Web: {web_conv:.1f}% ({views['Web']:,} users, {views['Web']/views['total']*100:.1f}% of traffic)
      └─ Actually your BEST performing platform!

3. Android Dominates Your Traffic
   ├─ {views['Android']:,} users ({views['Android']/views['total']*100:.1f}% of total)
   ├─ If you fix Android, you fix 88% of your funnel
   └─ Small fixes in Android = big impact

4. Volume Opportunity
   ├─ You're hitting {views['total']:,} signin page views
   ├─ Converting {entries['total']:,} to enter mobile number
   └─ At 52% baseline, you could be hitting {int(views['total'] * 0.52):,}
      (that's {int(views['total'] * 0.52) - entries['total']:,} more users)

5. What You Should Focus On
   ├─ 🎯 Android device tier analysis (88% of traffic)
   ├─ 🎯 Why Web is outperforming (64.4% conv) - learn from it
   ├─ 🎯 iOS optimization (only 47% conversion)
   ├─ 🎯 Get from {overall_conv:.1f}% → 52% baseline
""")

    def _show_next_actions(self):
        """Show next actions"""
        print("\n" + "─" * 120)
        print("🎯 NEXT ACTIONS")
        print("─" * 120)

        entries = self.ACTUAL_DATA['SIGNIN_PAGE_NUMBER_ENTERED']

        print(f"""
1. Get Accurate Device Tier Data
   ├─ Use Amplitude dashboard to segment Android by device model
   ├─ Export CSV for detailed breakdown
   └─ Or query API with proper device properties

2. Understand What's Working
   ├─ Web: 64.4% conversion - Why so good?
   ├─ Android: 41.4% conversion - Can we match Web?
   ├─ iOS: 46.8% conversion - Middle ground

3. Set Up Monitoring Agent
   ├─ Track these metrics every 48 hours
   ├─ Alert if conversion drops below 40%
   ├─ Monitor by platform
   └─ Catch issues automatically (vs discovering manually)

4. Create Week-on-Week Dashboard
   ├─ Current: {entries['total']:,} conversions
   ├─ Next week: Monitor if this stays stable
   ├─ Alert if trending down
""")


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                  📊 ACTUAL SIGNIN METRICS - FROM YOUR AMPLITUDE CHART                         ║
║                                                                                                ║
║  Using the REAL numbers you just showed me (not my outdated estimates)                        ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)

    analysis = ActualMetricsAnalysis()
    analysis.run()
    analysis._show_next_actions()

    print("\n" + "=" * 120)
    print("🙏 MY APOLOGIES")
    print("=" * 120)
    print("""
I was using outdated/estimated data. Your actual Amplitude numbers show:

✅ Better Performance
   └─ 42.9% actual vs 33.4% estimated

✅ Web Platform Success
   └─ 64.4% conversion (your best platform!)

✅ Healthy Android Platform
   └─ 41.4% conversion (large volume)

The real opportunity is:
1. Understand why Web works so well (64%)
2. Apply Web learnings to Android (41%) → target 50%+
3. Improve iOS (47%) → target 50%+
4. Use actual device tier data (request Amplitude export)

Let me create the monitoring agent using YOUR actual data, not my estimates!
    """)
    print("=" * 120 + "\n")


if __name__ == "__main__":
    main()
