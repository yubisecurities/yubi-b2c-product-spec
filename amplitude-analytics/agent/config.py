# Amplitude event catalog, baselines, and alert thresholds
# Based on AMPLITUDE_CONTEXT.md — Aspero B2C Signup Funnel

AMPLITUDE_PROJECT_ID = "506002"

# All funnel steps in order — is_key marks milestone events, is_registration = user signed up
FUNNEL_STEPS = [
    {
        "event": "SIGNIN_PAGE_VIEW",
        "label": "Signin Page View",
        "stage": "Stage 1 · Mobile OTP",
    },
    {
        "event": "SIGNIN_PAGE_NUMBER_ENTERED",
        "label": "Mobile Number Entered",
        "stage": "Stage 1 · Mobile OTP",
    },
    {
        "event": "VERIFY_OTP_SUCCESS",
        "label": "OTP Verified",
        "stage": "Stage 1 · Mobile OTP",
        "is_key": True,
    },
    {
        "event": "EMAIL_PAGE_VIEW",
        "label": "Email Page View",
        "stage": "Stage 2 · Email Verification",
    },
    {
        "event": "EMAIL_VERIFY_OTP_SUCCESS",
        "label": "Email Verified",
        "stage": "Stage 2 · Email Verification",
        "is_key": True,
    },
    {
        "event": "SETUP_SECURE_PIN_PAGE_VIEW",
        "label": "PIN Setup Page",
        "stage": "Stage 3 · PIN Setup",
    },
    {
        "event": "SETUP_SECURE_PIN_SUCCESS",
        "label": "PIN Setup Complete",
        "stage": "Stage 3 · PIN Setup",
        "is_key": True,
        "is_registration": True,
    },
]

# Failure events — tracked for anomaly detection
FAILURE_EVENTS = [
    "VERIFY_OTP_FAILED",
    "EMAIL_VERIFY_OTP_FAILED",
    "SETUP_SECURE_PIN_FAILED",
]

# Historical platform conversion baselines: SIGNIN_PAGE_VIEW → VERIFY_OTP_SUCCESS
PLATFORM_BASELINES = {
    "Android": 29.2,
    "iOS":     53.8,
    "Web":     51.3,
}

# Alert thresholds — below these triggers a 🔴 alert
PLATFORM_ALERT_THRESHOLDS = {
    "Android": 22.0,   # -7pp below historical
    "iOS":     40.0,   # -14pp below historical
    "Web":     40.0,   # -11pp below historical
}

# Warning thresholds — below these triggers a ⚠️ warning
PLATFORM_WARNING_THRESHOLDS = {
    "Android": 26.0,
    "iOS":     48.0,
    "Web":     46.0,
}

# Expected step-to-step conversion rates (from→to: min acceptable %)
STEP_THRESHOLDS = {
    ("SIGNIN_PAGE_VIEW", "VERIFY_OTP_SUCCESS"):             40.0,
    ("VERIFY_OTP_SUCCESS", "EMAIL_VERIFY_OTP_SUCCESS"):     35.0,
    ("EMAIL_VERIFY_OTP_SUCCESS", "SETUP_SECURE_PIN_SUCCESS"): 80.0,
}
