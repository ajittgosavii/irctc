"""
Indian Railways API Client
Primary: IRCTC1 RapidAPI (irctc1.p.rapidapi.com)
Fallback: erail.in unofficial endpoints
"""

import requests
import streamlit as st
from datetime import datetime
import time


RAPIDAPI_HOST = "irctc1.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}"


def get_headers():
    api_key = st.session_state.get("rapidapi_key", "")
    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }


def safe_get(url: str, params: dict = None, timeout: int = 12):
    """Safe GET with retry and error handling."""
    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return {"ok": True, "data": data}
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            return {"ok": False, "error": "⚠️ Rate limit exceeded. Please wait a moment and try again."}
        elif e.response is not None and e.response.status_code == 401:
            return {"ok": False, "error": "🔑 Invalid API key. Please check your RapidAPI key in Settings."}
        return {"ok": False, "error": f"API Error: {str(e)}"}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "🌐 Connection failed. Please check your internet connection."}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "⏱️ Request timed out. Please try again."}
    except Exception as e:
        return {"ok": False, "error": f"Unexpected error: {str(e)}"}


# ── Search Trains ──────────────────────────────────────────────
def search_train(query: str):
    url = f"{BASE_URL}/api/v1/searchTrain"
    return safe_get(url, {"query": query})


# ── Search Station ─────────────────────────────────────────────
def search_station(query: str):
    url = f"{BASE_URL}/api/v1/searchStation"
    return safe_get(url, {"query": query})


# ── Trains Between Stations ────────────────────────────────────
def trains_between_stations(from_code: str, to_code: str, date: str):
    """date format: YYYYMMDD"""
    url = f"{BASE_URL}/api/v3/trainBetweenStations"
    return safe_get(url, {
        "fromStationCode": from_code.upper(),
        "toStationCode": to_code.upper(),
        "dateOfJourney": date,
    })


# ── Seat Availability ──────────────────────────────────────────
CLASS_TYPES = {
    "1A": "First AC",
    "2A": "Second AC",
    "3A": "Third AC",
    "SL": "Sleeper",
    "CC": "Chair Car",
    "2S": "Second Sitting",
    "FC": "First Class",
    "3E": "Third AC Economy",
    "EC": "Executive Chair Car",
}

QUOTA_TYPES = {
    "GN": "General",
    "LD": "Ladies",
    "TQ": "Tatkal",
    "PT": "Premium Tatkal",
    "HP": "Physically Handicapped",
    "SS": "Senior Citizen",
}


def check_seat_availability(train_no: str, from_code: str, to_code: str,
                             class_type: str, quota: str, date: str):
    """date format: YYYYMMDD"""
    url = f"{BASE_URL}/api/v1/checkSeatAvailability"
    return safe_get(url, {
        "classType": class_type,
        "fromStationCode": from_code.upper(),
        "quota": quota,
        "toStationCode": to_code.upper(),
        "trainNo": train_no,
        "date": date,
    })


# ── PNR Status ─────────────────────────────────────────────────
def get_pnr_status(pnr: str):
    url = f"{BASE_URL}/api/v3/getPNRStatus"
    return safe_get(url, {"pnrNumber": pnr})


# ── Live Train Status ──────────────────────────────────────────
def get_live_train_status(train_no: str, start_day: int = 0):
    """start_day: 0=today, 1=yesterday, 2=day before"""
    url = f"{BASE_URL}/api/v1/liveTrainStatus"
    return safe_get(url, {"trainNo": train_no, "startDay": str(start_day)})


# ── Train Schedule / Timetable ─────────────────────────────────
def get_train_schedule(train_no: str):
    url = f"{BASE_URL}/api/v3/getTrainSchedule"
    return safe_get(url, {"trainNo": train_no})


# ── Cancelled Trains ───────────────────────────────────────────
def get_cancelled_trains(date: str):
    """date format: YYYYMMDD"""
    url = f"{BASE_URL}/api/v1/getCancelledTrains"
    return safe_get(url, {"date": date})


# ── Train Classes ──────────────────────────────────────────────
def get_train_classes(train_no: str):
    url = f"{BASE_URL}/api/v2/getTrainClasses"
    return safe_get(url, {"trainNo": train_no})


# ── Helpers ────────────────────────────────────────────────────
def format_date_for_api(dt) -> str:
    """Convert date object to YYYYMMDD string."""
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y%m%d")
    return str(dt).replace("-", "")


def format_duration(mins: int) -> str:
    if not mins:
        return "N/A"
    h, m = divmod(int(mins), 60)
    return f"{h}h {m}m"


def availability_color(status: str) -> str:
    s = str(status).upper()
    if any(x in s for x in ["AVAILABLE", "AVL"]):
        return "🟢"
    elif any(x in s for x in ["WL", "WAITLIST", "WAIT"]):
        return "🟡"
    elif any(x in s for x in ["RAC"]):
        return "🟠"
    elif any(x in s for x in ["REGRET", "NOT"]):
        return "🔴"
    return "⚪"


def days_of_run_str(days_dict: dict) -> str:
    """Convert days_of_run dict to readable string."""
    day_map = {"Mon": "M", "Tue": "T", "Wed": "W", "Thu": "T", "Fri": "F", "Sat": "S", "Sun": "S"}
    day_keys = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if not days_dict:
        return "Daily"
    return " ".join(day_map.get(d, "?") if days_dict.get(d) else "·" for d in day_keys)


def demo_mode_notice():
    st.info(
        "🔑 **Demo / No API Key Configured** — Enter your free RapidAPI key in ⚙️ Settings "
        "to fetch live data. Sample data is shown below for UI preview.",
        icon="ℹ️",
    )
