# Amplitude event catalog, baselines, and alert thresholds
# Source: AMPLITUDE_CONTEXT.md — Aspero B2C Signup Funnel (Project 506002)

AMPLITUDE_PROJECT_ID = "506002"

# ── Stage 1: Signin Page → OTP Verified (Mobile Verification) ────────────────
# Note: SIGNIN_PAGE_VERIFY_API_SUCCESS is the correct Amplitude event name
#       (documented as SIGNIN_PAGE_VERIFY_OTP_SENT in AMPLITUDE_CONTEXT.md)
STAGE1_STEPS = [
    {"event": "SIGNIN_PAGE_VIEW",              "label": "Signin Page View"},
    {"event": "SIGNIN_PAGE_NUMBER_ENTERED",    "label": "Number Entered"},
    {"event": "SIGNIN_PAGE_VERIFY_API_SUCCESS","label": "OTP Sent"},
    {"event": "VERIFY_OTP_PAGE_VIEW",          "label": "OTP Page View"},
    {"event": "VERIFY_OTP_ENTERED",            "label": "OTP Entered"},
    {"event": "VERIFY_OTP_SUCCESS",            "label": "OTP Verified", "is_key": True},
]

# ── Stage 2: Email Verification (new users only — fires once per mobile) ──────
STAGE2_STEPS = [
    {"event": "EMAIL_PAGE_VIEW",              "label": "Email Page View"},
    {"event": "EMAIL_PAGE_VERIFY_CLICKED",    "label": "Verify Clicked"},
    {"event": "EMAIL_PAGE_VERIFY_API_SUCCESS","label": "Email OTP Sent"},
    {"event": "EMAIL_VERIFY_OTP_PAGE_VIEW",   "label": "Email OTP Page"},
    {"event": "EMAIL_VERIFY_OTP_ENTERED",     "label": "Email OTP Entered"},
    {"event": "EMAIL_VERIFY_OTP_SUCCESS",     "label": "Email Verified", "is_key": True},
]

# ── Stage 3: Secure PIN Setup (new users only — fires once per mobile) ────────
# Note: SETUP_SECURE_PIN_SUBMIT_CLICK does not exist in this Amplitude project
STAGE3_STEPS = [
    {"event": "SETUP_SECURE_PIN_PAGE_VIEW", "label": "PIN Setup Page"},
    {
        "event": "SETUP_SECURE_PIN_SUCCESS",
        "label": "PIN Setup Complete",
        "is_key": True,
        "is_registration": True,
    },
]

# All steps combined (used for WoW comparison funnel)
FUNNEL_STEPS = STAGE1_STEPS + STAGE2_STEPS + STAGE3_STEPS

# ── Milestone events for the compact device-tier report ──────────────────────
# VERIFY_OTP_SUCCESS    = Mobile verified (new + returning)
# EMAIL_VERIFY_OTP_SUCCESS = Email verified via OTP (new users only)
# SSO_VERIFICATION_SUCCESS = Email verified via Google SSO (new users only)
# SETUP_SECURE_PIN_SUCCESS = Registration complete (new users only)
MILESTONE_EVENTS = {
    "otp":     "VERIFY_OTP_SUCCESS",
    "email_otp": "EMAIL_VERIFY_OTP_SUCCESS",
    "email_sso": "SSO_VERIFICATION_SUCCESS",
    "signup":  "SETUP_SECURE_PIN_SUCCESS",
}

# ── Failure events — tracked via segmentation API ─────────────────────────────
FAILURE_EVENTS = [
    "VERIFY_OTP_FAILED",
    "EMAIL_PAGE_VERIFY_API_FAILED",
    "EMAIL_VERIFY_OTP_FAILED",
    "SETUP_SECURE_PIN_FAILED",
]

# ── Platform baselines (SIGNIN_PAGE_VIEW → VERIFY_OTP_SUCCESS) ───────────────
PLATFORM_BASELINES = {
    "Android": 29.2,
    "iOS":     53.8,
    "Web":     51.3,
}

PLATFORM_ALERT_THRESHOLDS = {
    "Android": 22.0,
    "iOS":     40.0,
    "Web":     40.0,
}

PLATFORM_WARNING_THRESHOLDS = {
    "Android": 26.0,
    "iOS":     48.0,
    "Web":     46.0,
}

# ── Device tier classification ────────────────────────────────────────────────
# Matched against lowercased device_type strings from Amplitude.
# Order matters: check premium before mid, mid before low.
DEVICE_TIER_PATTERNS = {
    "premium_android": [
        "samsung s22", "samsung s23", "samsung s24", "samsung s25",
        "samsung galaxy s22", "samsung galaxy s23", "samsung galaxy s24", "samsung galaxy s25",
        "oneplus 9", "oneplus 10", "oneplus 11", "oneplus 12",
        "google pixel", "pixel 6", "pixel 7", "pixel 8", "pixel 9",
        "poco f",
    ],
    "mid_android": [
        "samsung a", "samsung galaxy a", "samsung m", "samsung galaxy m",
        "poco m", "poco x",
        "redmi note",
        "oneplus nord", "oneplus 11r", "oneplus 12r",
        "moto g",
        "vivo v", "vivo t",
        "oppo f", "oppo a",
        "realme 9", "realme 10", "realme 11", "realme 12",
        "realme narzo",
    ],
    "low_android": [
        "redmi a", "redmi 13c", "redmi 12c", "redmi 10c",
        "realme c",
        "moto e",
        "samsung j2", "samsung j3", "samsung j4", "samsung j5", "samsung j6", "samsung j7",
        "samsung galaxy j",
        "infinix", "tecno",
        "nokia 1", "nokia 2",
        "itel", "lava", "micromax",
    ],
}

# Expected end-to-end conversion: SIGNIN_PAGE_VIEW → SETUP_SECURE_PIN_SUCCESS
DEVICE_TIER_BASELINES = {
    "low_android":     30.0,
    "mid_android":     45.0,
    "premium_android": 65.0,
    "ios":             65.0,
    "web":             50.0,
    "other_android":   35.0,
}

DEVICE_TIER_LABELS = {
    "low_android":     "Low Android",
    "mid_android":     "Mid Android",
    "premium_android": "Premium Android",
    "ios":             "iOS",
    "web":             "Web",
    "unknown_android": "Unknown Android†",
    "other_android":   "Other Android",
    "other":           "Other",
}
