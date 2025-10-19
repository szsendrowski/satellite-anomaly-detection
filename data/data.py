import requests
import configparser
from datetime import datetime, timedelta

def TLEdata():
    class MyError(Exception):
        """Custom exception for TLE data download errors."""
        def __init__(self, *args):
            super().__init__(*args)

    # --- Configuration ---
    uriBase = "https://www.space-track.org"
    requestLogin = "/ajaxauth/login"
    requestCmdAction = "/basicspacedata/query"

    # Query for all TLEs from the last 3 days
    date3days = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    requestTLE = f"/class/tle/EPOCH/>{date3days}/format/tle/orderby/EPOCH%20desc"

    # --- Read login credentials from config.ini ---
    config = configparser.ConfigParser()
    config.read("./config.ini")
    configUsr = config.get("configuration", "username")
    configPwd = config.get("configuration", "password")
    output_file = config.get("configuration", "output", fallback="LEO_data.tle")
    siteCred = {"identity": configUsr, "password": configPwd}

    # --- Login and data download ---
    print("🔑 Logging in to space-track.org...")
    with requests.Session() as session:
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise MyError(f"Login failed ({resp.status_code})")

        print("📡 Downloading TLE data (last 3 days)...")
        resp = session.get(uriBase + requestCmdAction + requestTLE)
        if resp.status_code != 200:
            raise MyError(f"GET request failed ({resp.status_code})")

        tle_text = resp.text
        print(f"✅ Retrieved approximately {len(tle_text.splitlines()) // 3} satellites.")

    # --- Save data to file ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tle_text)

    print(f"💾 TLE data saved to {output_file}")

# Run the function
tledada = TLEdata()