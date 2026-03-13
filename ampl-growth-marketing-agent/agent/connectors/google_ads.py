"""
Google Ads API connector.

Authenticates via OAuth2 and provides methods to pull:
  - Campaign-level performance (impressions, clicks, cost, conversions, ROAS)
  - Ad creative performance (ad-level CTR, conversions, headlines)
  - Audience & device segment breakdowns
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import config


def _build_client() -> GoogleAdsClient:
    """Build an authenticated GoogleAdsClient from environment variables."""
    credentials = {
        "developer_token":   config.GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id":         config.GOOGLE_ADS_CLIENT_ID,
        "client_secret":     config.GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token":     config.GOOGLE_ADS_REFRESH_TOKEN,
        "login_customer_id": config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
        "use_proto_plus":    True,
    }
    return GoogleAdsClient.load_from_dict(credentials)


def get_campaign_performance(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch campaign-level performance metrics for the given date range.

    Args:
        start_date: "YYYY-MM-DD"
        end_date:   "YYYY-MM-DD"

    Returns:
        List of dicts, one per campaign:
        {
            "campaign_id":     str,
            "campaign_name":   str,
            "status":          str,
            "impressions":     int,
            "clicks":          int,
            "cost_micros":     int,   # divide by 1_000_000 to get actual spend
            "conversions":     float,
            "conversion_value": float,
            "ctr":             float, # 0–1
            "avg_cpc_micros":  int,
        }
    """
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")
    customer_id = config.GOOGLE_ADS_CUSTOMER_ID

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            c = row.campaign
            m = row.metrics
            rows.append({
                "campaign_id":      str(c.id),
                "campaign_name":    c.name,
                "status":           c.status.name,
                "impressions":      m.impressions,
                "clicks":           m.clicks,
                "cost_micros":      m.cost_micros,
                "conversions":      m.conversions,
                "conversion_value": m.conversions_value,
                "ctr":              m.ctr,
                "avg_cpc_micros":   m.average_cpc,
            })
    except GoogleAdsException as ex:
        _handle_error(ex)

    return rows


def get_ad_performance(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch ad-level performance for creative analysis.
    Pulls responsive search ads with their top headlines/descriptions.

    Returns:
        List of dicts, one per ad:
        {
            "campaign_name":  str,
            "ad_group_name":  str,
            "ad_id":          str,
            "ad_type":        str,
            "impressions":    int,
            "clicks":         int,
            "cost_micros":    int,
            "conversions":    float,
            "ctr":            float,
            "headlines":      list[str],  # RSA headlines (up to 15)
            "descriptions":   list[str],  # RSA descriptions (up to 4)
        }
    """
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")
    customer_id = config.GOOGLE_ADS_CUSTOMER_ID

    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND ad_group_ad.status != 'REMOVED'
          AND metrics.impressions > 0
        ORDER BY metrics.impressions DESC
        LIMIT 50
    """

    rows = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            ad = row.ad_group_ad.ad
            m  = row.metrics

            headlines    = []
            descriptions = []
            if ad.type_.name == "RESPONSIVE_SEARCH_AD":
                rsa = ad.responsive_search_ad
                headlines    = [h.text for h in rsa.headlines]
                descriptions = [d.text for d in rsa.descriptions]

            rows.append({
                "campaign_name": row.campaign.name,
                "ad_group_name": row.ad_group.name,
                "ad_id":         str(ad.id),
                "ad_type":       ad.type_.name,
                "impressions":   m.impressions,
                "clicks":        m.clicks,
                "cost_micros":   m.cost_micros,
                "conversions":   m.conversions,
                "ctr":           m.ctr,
                "headlines":     headlines,
                "descriptions":  descriptions,
            })
    except GoogleAdsException as ex:
        _handle_error(ex)

    return rows


def get_device_segments(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch campaign performance broken down by device type.

    Returns:
        List of dicts:
        {
            "campaign_name": str,
            "device":        str,  # DESKTOP, MOBILE, TABLET
            "impressions":   int,
            "clicks":        int,
            "cost_micros":   int,
            "conversions":   float,
        }
    """
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")
    customer_id = config.GOOGLE_ADS_CUSTOMER_ID

    query = f"""
        SELECT
            campaign.name,
            segments.device,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            m = row.metrics
            rows.append({
                "campaign_name": row.campaign.name,
                "device":        row.segments.device.name,
                "impressions":   m.impressions,
                "clicks":        m.clicks,
                "cost_micros":   m.cost_micros,
                "conversions":   m.conversions,
            })
    except GoogleAdsException as ex:
        _handle_error(ex)

    return rows


def get_geo_segments(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch campaign performance broken down by country/region.

    Returns:
        List of dicts:
        {
            "campaign_name":   str,
            "country_code":    str,
            "impressions":     int,
            "clicks":          int,
            "cost_micros":     int,
            "conversions":     float,
        }
    """
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")
    customer_id = config.GOOGLE_ADS_CUSTOMER_ID

    query = f"""
        SELECT
            campaign.name,
            geographic_view.country_criterion_id,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM geographic_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY metrics.impressions DESC
        LIMIT 20
    """

    rows = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            m = row.metrics
            rows.append({
                "campaign_name":         row.campaign.name,
                "country_criterion_id":  row.geographic_view.country_criterion_id,
                "impressions":           m.impressions,
                "clicks":                m.clicks,
                "cost_micros":           m.cost_micros,
                "conversions":           m.conversions,
            })
    except GoogleAdsException as ex:
        _handle_error(ex)

    return rows


def _handle_error(ex: GoogleAdsException) -> None:
    print(f"[GoogleAds] Request failed — ID: {ex.request_id}")
    for error in ex.failure.errors:
        print(f"  Error: {error.message}")
        if error.location:
            for field in error.location.field_path_elements:
                print(f"    Field: {field.field_name}")
    raise ex
