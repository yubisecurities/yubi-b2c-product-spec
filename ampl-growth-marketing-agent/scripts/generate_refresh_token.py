"""
Generate a Google OAuth2 Refresh Token for use with the Google Ads API.

Run this ONCE to get your refresh token, then add it to your .env file.

Usage:
    cd ampl-growth-marketing-agent/
    pip install google-auth-oauthlib
    python scripts/generate_refresh_token.py

Prerequisites:
    1. Go to https://console.cloud.google.com/
    2. Create (or open) a project
    3. Enable the Google Ads API
    4. Create OAuth2 credentials → Desktop App
    5. Download the client_secret JSON — you'll need client_id and client_secret below

What this script does:
    1. Opens your browser to Google's OAuth consent screen
    2. You log in with the Google account that owns (or has access to) the Ads manager account
    3. Returns a refresh_token — paste it into your .env
"""

import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Install dependency first:  pip install google-auth-oauthlib")
    sys.exit(1)


# ── Google Ads API OAuth2 scope ───────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    client_id     = input("Enter your OAuth2 Client ID:     ").strip()
    client_secret = input("Enter your OAuth2 Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Client ID and secret are required.")
        sys.exit(1)

    # Build a minimal client config dict (same format as client_secret JSON)
    client_config = {
        "installed": {
            "client_id":                  client_id,
            "client_secret":              client_secret,
            "redirect_uris":              ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri":                   "https://accounts.google.com/o/oauth2/auth",
            "token_uri":                  "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    print("\nOpening browser for Google sign-in...")
    print("Log in with the account that has access to your Google Ads manager account.\n")

    credentials = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("SUCCESS — add these to your agent/.env file:")
    print("=" * 60)
    print(f"GOOGLE_ADS_CLIENT_ID={client_id}")
    print(f"GOOGLE_ADS_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
    print("=" * 60)
    print("\nRefresh tokens don't expire unless revoked — store it securely.")


if __name__ == "__main__":
    main()
