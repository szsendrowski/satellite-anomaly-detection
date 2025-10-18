import requests
import configparser
from datetime import datetime, timedelta

def TLEdata():
    class MyError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    # --- konfiguracja ---
    uriBase = "https://www.space-track.org"
    requestLogin = "/ajaxauth/login"
    requestCmdAction = "/basicspacedata/query"

    # 3 dni temu (UTC)
    date3days = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Zapytanie o wszystkie TLE z ostatnich 3 dni (format TLE)
    requestTLE = f"/class/tle/EPOCH/>{date3days}/format/tle/orderby/EPOCH%20desc"

    # --- dane logowania z pliku INI ---
    config = configparser.ConfigParser()
    config.read("./SLTrack.ini")
    configUsr = config.get("configuration", "username")
    configPwd = config.get("configuration", "password")
    output_file = config.get("configuration", "output", fallback="LEO_data.tle")
    siteCred = {'identity': configUsr, 'password': configPwd}

    # --- logowanie i pobieranie danych ---
    print("🔑 Logging in to space-track.org...")
    with requests.Session() as session:
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise MyError(f"Login failed ({resp.status_code})")

        print("📡 Downloading TLE data (last 3 days)...")
        resp = session.get(uriBase + requestCmdAction + requestTLE)
        if resp.status_code != 200:
            raise MyError(f"GET fail on query ({resp.status_code})")

        tle_text = resp.text
        print(f"✅ Retrieved {len(tle_text.splitlines())//3} satellites (approx).")

    # --- zapis do pliku ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tle_text)

    print(f"💾 Saved TLE data to {output_file}")

tledada = TLEdata()