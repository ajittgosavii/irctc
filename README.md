# 🚆 Indian Railways Live Tracker & Planner

A comprehensive multi-user Streamlit application for tracking Indian Railways trains, checking seat availability, PNR status, live train running status, and full timetables.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Train Search** | Search any train by number or name |
| 🚉 **Trains Between Stations** | Find all trains on a route with availability |
| 💺 **Seat Availability** | Real-time seat check by class, quota & date (multi-date) |
| 📋 **PNR Status** | Booking & passenger status with berth details |
| 🔴 **Live Train Status** | Real-time running position, delays, speed |
| 📅 **Train Schedule** | Full station-wise timetable (timeline + table view) |
| ⚠️ **Cancelled Trains** | Today's cancellations and alerts |
| 👤 **Multi-User Auth** | Register/login, persistent search history, favourites |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd indian_railways_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
streamlit run app.py
```

### 4. Get a Free API Key
1. Go to [rapidapi.com](https://rapidapi.com)
2. Search for **IRCTC1** (by IRCTCAPI)
3. Subscribe to the **Basic (free)** tier — 100 requests/day
4. Copy your `X-RapidAPI-Key`
5. Open ⚙️ Settings in the app and paste your key

---

## ☁️ Deploy to Streamlit Cloud

1. Push to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `app.py` as the main file
5. Add secrets (optional) in Streamlit Cloud dashboard:
   ```toml
   [secrets]
   RAPIDAPI_KEY = "your-key-here"
   ```
6. Click **Deploy**

---

## 📁 Project Structure

```
indian_railways_app/
├── app.py                        # Home dashboard
├── requirements.txt
├── .streamlit/
│   └── config.toml               # Theme & server config
├── utils/
│   ├── api_client.py             # IRCTC RapidAPI wrapper
│   ├── session.py                # Multi-user auth + SQLite
│   └── ui.py                     # Shared UI components & CSS
└── pages/
    ├── 1_🔍_Train_Search.py
    ├── 2_🚉_Between_Stations.py
    ├── 3_💺_Seat_Availability.py
    ├── 4_📋_PNR_Status.py
    ├── 5_🔴_Live_Status.py
    ├── 6_📅_Schedule.py
    ├── 7_⚙️_Settings.py
    └── 8_⚠️_Alerts.py
```

---

## 🔌 API Reference

**Primary API:** [IRCTC1 on RapidAPI](https://rapidapi.com/IRCTCAPI/api/irctc1)

| Endpoint | Used For |
|---|---|
| `/api/v1/searchTrain` | Train search by number/name |
| `/api/v3/trainBetweenStations` | Trains between two stations |
| `/api/v1/checkSeatAvailability` | Seat availability |
| `/api/v3/getPNRStatus` | PNR status check |
| `/api/v1/liveTrainStatus` | Live running status |
| `/api/v3/getTrainSchedule` | Full timetable |
| `/api/v1/getCancelledTrains` | Cancellation alerts |

---

## 🎫 Train Classes & Quotas

**Classes:** 1A, 2A, 3A, SL, CC, 2S, FC, EC, 3E  
**Quotas:** GN (General), TQ (Tatkal), PT (Premium Tatkal), LD (Ladies), HP (Handicapped), SS (Senior Citizen)

---

## ⚠️ Disclaimer

This is an **unofficial third-party application**. For official bookings, visit [irctc.co.in](https://www.irctc.co.in).  
All data is sourced from IRCTC via RapidAPI. Always verify critical travel information on the official platform.

---

## 📞 Railway Helpline: **139**
