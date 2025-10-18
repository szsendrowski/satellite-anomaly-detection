import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import timezone, timedelta
from skyfield.api import load, EarthSatellite, wgs84
from tqdm import tqdm
import swami

# ======================
# USTAWIENIA ŚRODOWISKA
# ======================
swami.SWAMI_EXE = r"C:\Users\kipki\Documents\GitHub\satellite-anomaly-detection\.venv\Lib\site-packages\swami\swami.x"
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ["PATH"]
os.environ["TMPDIR"] = os.path.abspath("./tmp")
os.makedirs("./tmp", exist_ok=True)

# ======================
# WCZYTANIE TLE Z PLIKU
# ======================
def load_tle_pairs(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    pairs = []
    i = 0
    while i < len(lines) - 1:
        # obsługa ewentualnych nagłówków 3-liniowych
        if lines[i].startswith("0 ") and i + 2 < len(lines):
            if lines[i+1].startswith("1 ") and lines[i+2].startswith("2 "):
                pairs.append((lines[i+1], lines[i+2]))
                i += 3
                continue
        if lines[i].startswith("1 ") and lines[i+1].startswith("2 "):
            pairs.append((lines[i], lines[i+1]))
            i += 2
            continue
        i += 1
    return pairs

def period_from_tle_line2(tle2: str) -> float:
    """Zwraca okres w minutach z mean motion (rev/day) z linii 2 TLE."""
    mean_motion_str = tle2[52:63].strip()
    n_rev_per_day = float(mean_motion_str)
    return 1440.0 / n_rev_per_day

tle_path = "LEO_data.tle"
pairs = load_tle_pairs(tle_path)
if not pairs:
    raise ValueError("❌ Nie znaleziono żadnych poprawnych zestawów TLE w pliku.")

# wybór najlepszego zestawu (LEO: 70–120 min)
candidates = []
for (l1, l2) in pairs:
    try:
        T = period_from_tle_line2(l2)
        candidates.append((abs(T - 95.0), T, l1, l2))
    except Exception:
        continue

if candidates:
    leo = [c for c in candidates if 70.0 <= c[1] <= 120.0]
    chosen = min(leo, key=lambda x: x[0]) if leo else min(candidates, key=lambda x: x[0])
    period_minutes, tle1, tle2 = chosen[1], chosen[2], chosen[3]
else:
    tle1, tle2 = pairs[0]
    period_minutes = period_from_tle_line2(tle2)

ts = load.timescale()
sat = EarthSatellite(tle1, tle2, "LEO", ts)

# ======================
# CZAS STARTU I OKRES ORBITY
# ======================
epoch = sat.epoch.utc_datetime().replace(tzinfo=timezone.utc)
print(f"🛰️ Wybrany TLE – okres jednego obiegu ≈ {period_minutes:.2f} min")

# ======================
# TRAJEKTORIA: JEDEN OBIEG
# ======================
duration = timedelta(minutes=period_minutes)
dt_seconds = 120  # krok próbkowania
times = [epoch + timedelta(seconds=i * dt_seconds)
         for i in range(int(duration.total_seconds() // dt_seconds) + 1)]
t_sky = ts.from_datetimes(times)

geoc = sat.at(t_sky)
sub = wgs84.subpoint(geoc)
lats = sub.latitude.degrees
lons = sub.longitude.degrees
alts_km = sub.elevation.km

# ======================
# MODEL SWAMI / DTM2020
# ======================
mcm = swami.MCM()

f107, f107m, kp1, kp2 = 235.0, 150.0, 1, 1
doy = epoch.timetuple().tm_yday
altitude_km = float(np.nanmedian(alts_km))
print(f"📏 Wysokość mapy ustawiona na ~{altitude_km:.1f} km (mediana z obiegu)")

# ======================
# GLOBALNA MAPA GĘSTOŚCI — SIATKA 5° × 5°
# ======================
print("🌍 Obliczanie gęstości atmosfery globalnie (siatka co 5°)...")

lat_grid = np.arange(-90, 91, 5)     # co 5°
lon_grid = np.arange(-180, 181, 5)   # co 5°
density_map_kg = np.zeros((lat_grid.size, lon_grid.size), dtype=float)

for i, lat in enumerate(tqdm(lat_grid, desc="Szerokość geogr.")):
    for j, lon in enumerate(lon_grid):
        local_time = (epoch.hour + epoch.minute / 60.0 + lon / 15.0) % 24
        out = mcm.run(
            altitude=float(altitude_km),
            latitude=float(lat),
            longitude=float(lon),
            local_time=float(local_time),
            day_of_year=int(doy),
            f107=float(f107),
            f107m=float(f107m),
            kp1=int(kp1),
            kp2=int(kp2),
            get_winds=False,
            get_uncertainty=False,
        )
        # g/cm³ → kg/m³
        density_map_kg[i, j] = out.dens * 1000.0

# ======================
# RYSOWANIE MAPY
# ======================
print("🗺️ Rysowanie mapy gęstości…")

fig = plt.figure(figsize=(13, 5))
proj = ccrs.PlateCarree(central_longitude=0)  # ✅ stabilniejsza niż Mollweide
ax = plt.axes(projection=proj)
ax.set_global()

# poprawienie zakresu długości, żeby Cartopy nie przeskakiwało przez ±180°
lons_wrapped = np.unwrap(np.radians(lons)) * 180 / np.pi
lons_wrapped = ((lons_wrapped + 180) % 360) - 180

# siatka mapy
lon2d, lat2d = np.meshgrid(lon_grid, lat_grid)
dens_units = density_map_kg / 1e-11

im = ax.pcolormesh(
    lon2d, lat2d, dens_units,
    cmap="RdPu",
    transform=ccrs.PlateCarree(),
    shading="auto"
)

# tło i elementy mapy
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linestyle=":", linewidth=0.6)
ax.add_feature(cfeature.LAND, facecolor="lightgray", alpha=0.5)
ax.add_feature(cfeature.OCEAN, facecolor="aliceblue", alpha=0.6)
ax.gridlines(draw_labels=True, color="gray", alpha=0.3, linestyle="--")

# trajektoria satelity — rysowana geodezyjnie
ax.plot(lons_wrapped, lats, color="red", linewidth=2,
        transform=ccrs.Geodetic(), label="Orbita satelity")

# kolorbar
cb = plt.colorbar(im, ax=ax, orientation="vertical", pad=0.02, shrink=0.85)
cb.set_label("Gęstość [10⁻¹¹ kg/m³]")

title = (f"DTM2020 – gęstość na ~{altitude_km:.0f} km  |  "
         f"DOY={doy}; F10.7={f107}; Kp={kp1}\n"
         f"Trajektoria: {epoch:%Y-%m-%d %H:%M} UTC  •  T≈{period_minutes:.1f} min")
ax.set_title(title, fontsize=12)
ax.legend(loc="lower left")

plt.tight_layout()
plt.show()
