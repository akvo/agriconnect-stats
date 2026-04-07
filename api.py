import requests
import streamlit as st
from typing import Optional
from datetime import date


def get_api_config():
    """Get API configuration from secrets."""
    return {
        "domain": st.secrets["api"]["domain"],
        "token": st.secrets["api"]["token"],
    }


def get_headers():
    """Get authorization headers."""
    config = get_api_config()
    return {"Authorization": f"Bearer {config['token']}"}


def api_get(endpoint: str, params: Optional[dict] = None, auth: bool = True):
    """Make a GET request to the API."""
    config = get_api_config()
    url = f"{config['domain']}/api{endpoint}"
    headers = get_headers() if auth else {}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


# Administrative endpoints (public)
def get_administrative_levels():
    """Get list of administrative levels."""
    return api_get("/administrative/levels", auth=False)


def get_administrative_by_level(level: str):
    """Get administrative areas by level."""
    return api_get("/administrative/", params={"level": level}, auth=False)


def get_administrative_by_parent(parent_id: int):
    """Get child administrative areas."""
    return api_get("/administrative/", params={"parent_id": parent_id}, auth=False)


# Farmer statistics endpoints
def get_farmer_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    administrative_id: Optional[int] = None,
    phone_prefix: str = "+254",
    crop_type: Optional[str] = None,
    active_days: int = 30,
):
    """Get comprehensive farmer statistics."""
    params = {"phone_prefix": phone_prefix, "active_days": active_days}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if administrative_id:
        params["administrative_id"] = administrative_id
    if crop_type:
        params["crop_type"] = crop_type
    return api_get("/statistic/farmers/stats", params=params)


def get_farmer_stats_by_ward(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    administrative_id: Optional[int] = None,
    phone_prefix: str = "+254",
    crop_type: Optional[str] = None,
):
    """Get farmer statistics grouped by ward."""
    params = {"phone_prefix": phone_prefix}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if administrative_id:
        params["administrative_id"] = administrative_id
    if crop_type:
        params["crop_type"] = crop_type
    return api_get("/statistic/farmers/stats/by-ward", params=params)


def get_farmer_registrations(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    administrative_id: Optional[int] = None,
    phone_prefix: str = "+254",
    crop_type: Optional[str] = None,
    group_by: str = "day",
):
    """Get time series data of farmer registrations."""
    params = {"phone_prefix": phone_prefix, "group_by": group_by}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if administrative_id:
        params["administrative_id"] = administrative_id
    if crop_type:
        params["crop_type"] = crop_type
    return api_get("/statistic/farmers/registrations", params=params)


# EO statistics endpoints
def get_eo_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    eo_id: Optional[int] = None,
    administrative_id: Optional[int] = None,
):
    """Get EO statistics."""
    params = {}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if eo_id:
        params["eo_id"] = eo_id
    if administrative_id:
        params["administrative_id"] = administrative_id
    return api_get("/statistic/eo/stats", params=params)


def get_eo_stats_by_eo(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    administrative_id: Optional[int] = None,
):
    """Get statistics for each individual EO."""
    params = {}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if administrative_id:
        params["administrative_id"] = administrative_id
    return api_get("/statistic/eo/stats/by-eo", params=params)


def get_eo_count(administrative_id: Optional[int] = None):
    """Get total count of EOs."""
    params = {}
    if administrative_id:
        params["administrative_id"] = administrative_id
    return api_get("/statistic/eo/count", params=params)


def get_eo_list():
    """Get list of all EOs for filter dropdown."""
    return api_get("/statistic/eo/list")


# Aggregate endpoints (for dashboard views with available filters)
def get_aggregate_farmers(
    level: str = "region",
    administrative_id: Optional[int] = None,
    crop_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Get farmer statistics aggregated by administrative level.

    Returns data grouped by level and an 'available' object listing
    all regions, districts, wards, and crop_types that have data.
    """
    params = {"level": level}
    if administrative_id:
        params["administrative_id"] = administrative_id
    if crop_type:
        params["crop_type"] = crop_type
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    return api_get("/statistic/aggregate/farmers", params=params)


def get_aggregate_eo(
    level: str = "region",
    administrative_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Get EO statistics aggregated by administrative level.

    Returns data grouped by level and an 'available' object listing
    all regions, districts, wards that have data.
    """
    params = {"level": level}
    if administrative_id:
        params["administrative_id"] = administrative_id
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    return api_get("/statistic/aggregate/eo", params=params)
