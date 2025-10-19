import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from skyfield.api import EarthSatellite, load, wgs84

# ------------------ IGRF ------------------
def load_igrf_coeffs(filepath):
    coeffs = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line.startswith('#') or not line.startswith(('g','h')):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            t = parts[0]
            if not (parts[1].isdigit() and parts[2].isdigit()):
                continue
            n = int(parts[1])
            m = int(parts[2])
            values = [float(x) for x in parts[3:]]
            coeffs[(n,m,t)] = values
    return coeffs

def get_coeffs_for_year(coeffs, year):
    epochs = np.arange(1900, 2030, 5)
    gnm, hnm = {}, {}
    for (n,m,t), vals in coeffs.items():
        val = np.interp(year, epochs, vals[:-1])
        (gnm if t=='g' else hnm)[(n,m)] = val
    return gnm, hnm

def igrf_field(lat, lon, alt_km, year, coeffs):
    a = 6371.2
    r = a + alt_km
    theta = np.radians(90 - lat)
    lon_rad = np.radians(lon)
    gnm, hnm = get_coeffs_for_year(coeffs, year)
    max_n = 13
    P = np.zeros((max_n+1,max_n+1))
    P[0,0] = 1.0
    for n in range(1,max_n+1):
        P[n,0] = ((2*n-1)*np.cos(theta)*P[n-1,0])/n
        for m in range(1,n+1):
            if n==m:
                P[n,m] = np.sin(theta)*P[n-1,m-1]
            else:
                P[n,m] = ((2*n-1)*np.cos(theta)*P[n-1,m] - (n+m-1)*P[n-2,m])/(n-m)
    Br = Btheta = Bphi = 0.0
    for n in range(1,max_n+1):
        for m in range(0,n+1):
            g = gnm.get((n,m),0)
            h = hnm.get((n,m),0)
            factor = (a/r)**(n+2)
            term = g*np.cos(m*lon_rad) + h*np.sin(m*lon_rad)
            Br += factor*(n+1)*term*P[n,m]
            Btheta -= factor*term
            Bphi += factor*m*(g*np.sin(m*lon_rad)-h*np.cos(m*lon_rad))*P[n,m]
    X = -Btheta
    Y = Bphi / np.maximum(np.sin(theta),1e-6)
    Z = -Br
    B_total = np.sqrt(X**2 + Y**2 + Z**2)
    return {"X": X,"Y":Y,"Z":Z,"B_total":B_total}

# ------------------ LOAD IGRF ------------------
coeffs = load_igrf_coeffs("igrf14coeffs.txt")

# ------------------ READ ISS TLE FROM LOCAL FILE ------------------
tle_file = "TLE_ISS.txt"
with open(tle_file, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

tle_data = []
for i in range(0,len(lines),3):
    try:
        name, line1, line2 = lines[i], lines[i+1], lines[i+2]
        norad_id = int(line1[2:7])
        tle_data.append({"NORAD_CAT_ID": norad_id, "OBJECT_NAME": name,
                         "TLE_LINE1": line1, "TLE_LINE2": line2})
    except:
        continue

df = pd.DataFrame(tle_data)

# ------------------ ISS ------------------
my_sat_ID = 25544
sat_row = df[df['NORAD_CAT_ID'] == my_sat_ID]
ts = load.timescale()
my_sat = EarthSatellite(sat_row.iloc[0]['TLE_LINE1'],
                        sat_row.iloc[0]['TLE_LINE2'],
                        sat_row.iloc[0]['OBJECT_NAME'],
                        ts)

# ------------------ SIMULATION ------------------
timestep_min = 10
simulation_h = 12
steps = int(simulation_h*60 / timestep_min)
year_fixed = 2025.0
altitude_km = 408.0

trajectory = []
for step in range(steps):
    t_min = step*timestep_min
    t_sf = ts.now()
    geod = wgs84.subpoint(my_sat.at(t_sf))
    lat = geod.latitude.degrees
    lon = geod.longitude.degrees
    B = igrf_field(lat, lon, altitude_km, year_fixed, coeffs)
    trajectory.append({
        "time_min": t_min,
        "latitude_deg": lat,
        "longitude_deg": lon,
        "altitude_km": altitude_km,
        "B_total_μT": B['B_total']
    })

traj_df = pd.DataFrame(trajectory)

# ------------------ GRID ------------------
lats = np.arange(-90,91,5)
lons = np.arange(-180,181,5)
B_grid = np.zeros((len(lats),len(lons)))
for i,lat in enumerate(lats):
    for j,lon in enumerate(lons):
        B = igrf_field(lat, lon, altitude_km, year_fixed, coeffs)
        B_grid[i,j] = B['B_total']

B_grid_uT = B_grid/1000
lon_grid, lat_grid = np.meshgrid(lons,lats)

# ------------------ PLOT ------------------
fig = plt.figure(figsize=(12,10))
ax_map = fig.add_subplot(2,1,1,projection=ccrs.PlateCarree())
im = ax_map.pcolormesh(lon_grid, lat_grid, B_grid_uT, cmap='coolwarm', shading='auto')
ax_map.add_feature(cfeature.COASTLINE)
ax_map.add_feature(cfeature.BORDERS, linestyle=':')
ax_map.set_global()
plt.colorbar(im, ax=ax_map, label='Magnetic field intensity [μT]')
ax_map.set_title(f'Total Magnetic Field from IGRF14 at {altitude_km} km')

ax_plot = fig.add_subplot(2,1,2)
ax_plot.plot(traj_df['time_min']/60, traj_df['B_total_μT']*10, marker='o')
ax_plot.set_xlabel("Time [h]")
ax_plot.set_ylabel("Magnetic field intensity [μT]")
ax_plot.set_title(f"Total Magnetic Field along {my_sat.name} trajectory at {altitude_km} km")
ax_plot.grid(True)

plt.tight_layout()
plt.show()

traj_df.to_csv('ISS_trajectory_magnetic_field.csv', index=False)
print("Trajectory with magnetic field saved to CSV")
