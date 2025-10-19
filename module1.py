import pandas as pd
import requests
from datetime import timedelta


# Pobieranie danych

url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'

r = requests.get(url)
r.raise_for_status()

lines = r.text.strip().splitlines()

dane_TLE = []
for i in range(0, len(lines), 3):
    try:
        name = lines[i].strip()
        line1 = lines[i+1].strip()
        line2 = lines[i+2].strip()
        norad_id = int(line1[2:7])

        dane_TLE.append({
            "NORAD_CAT_ID": norad_id,
            "OBJECT_NAME": name,
            "TLE_LINE1": line1,
            "TLE_LINE2": line2
        })
    except Exception as e:
        print(f"Satellites were not analyzed on the lines: {i}-{i+2}: {e}")

df = pd.DataFrame(dane_TLE)
df.to_csv('satcat.csv', index=False)
print(f"Satellites to analyze: {len(df)}")
print(df.head())

my_sat_ID = 28358  # wpisz NORAD ID satelity

sat_row = df[df['NORAD_CAT_ID'] == my_sat_ID]

if sat_row.empty:
    raise ValueError(f"Satellite with NORAD ID {my_sat_ID} not found!")

from skyfield.api import EarthSatellite, load, wgs84
ts = load.timescale()
my_sat = EarthSatellite(
    sat_row.iloc[0]['TLE_LINE1'],
    sat_row.iloc[0]['TLE_LINE2'],
    sat_row.iloc[0]['OBJECT_NAME'],
    ts
)

print(f"Satellite selected: {my_sat.name}")

timestep_min = 60  # w minutach
simulation_time_h = 24  # czas symulacji w godzinach

steps = int(simulation_time_h * 60 / timestep_min)
t0 = ts.now()

trajectory = []

for step in range(steps):
    t = t0 + timedelta(minutes=step * timestep_min)
    geod = wgs84.subpoint(my_sat.at(t))
    trajectory.append({
        'time_utc': t.utc_datetime(),
        'latitude_deg': geod.latitude.degrees,
        'longitude_deg': geod.longitude.degrees,
        'altitude_km': geod.elevation.km
    })

traj_df = pd.DataFrame(trajectory)
#traj_df.to_csv(L, index=False)
print(f"Trajectory saved to CSV")




