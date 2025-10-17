# interp_demo_full.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, Rbf
import xarray as xr
from mpl_toolkits.mplot3d import Axes3D  # ensures 3D projection is available
from matplotlib import cm

np.random.seed(1)

# 1) Wygeneruj syntetyczne "pasy satelitarne" (trajektorie)
n_passes = 30
points_per_pass = 300
lats = []
lons = []
times = []  # UTC hours 0..24
for i in range(n_passes):
    start_lon = np.random.uniform(-180, 180)
    lat = np.linspace(-80, 80, points_per_pass) * (1 if np.random.rand() < 0.5 else -1)
    # avoid duplicate endpoint at 360
    lon = (start_lon + np.linspace(0, 360, points_per_pass, endpoint=False) * np.random.uniform(0.5, 1.5)) % 360
    lon = np.where(lon > 180, lon - 360, lon)
    t0 = np.random.uniform(0, 24)
    time = (t0 + np.linspace(0, 1.5, points_per_pass, endpoint=False)) % 24
    lats.append(lat)
    lons.append(lon)
    times.append(time)

lats = np.concatenate(lats)
lons = np.concatenate(lons)
times = np.concatenate(times)

# 2) "Prawdziwe" pole gęstości jako funkcja lat, lon, local time
local_time = (times + lons/15.0) % 24
rho_true = (3e-12 * (1 + 0.6 * np.cos(np.deg2rad(lats))**2)
            * (1 + 0.2 * np.sin(2*np.pi*local_time/24.0))
            * (1 + 0.1 * np.cos(np.deg2rad(lons*2))))
noise_level = 0.15
rho_obs = rho_true * (1 + noise_level * np.random.randn(rho_true.size))

# 3) Siatka globalna
grid_lat = np.linspace(-90, 90, 181)
grid_lon = np.linspace(-180, 180, 361)
GLON, GLAT = np.meshgrid(grid_lon, grid_lat)

# 4) RBF na współrzędnych sferycznych
def sph2cart(lon, lat):
    lonr = np.deg2rad(lon)
    latr = np.deg2rad(lat)
    x = np.cos(latr) * np.cos(lonr)
    y = np.cos(latr) * np.sin(lonr)
    z = np.sin(latr)
    return x, y, z

x_obs, y_obs, z_obs = sph2cart(lons, lats)
xg, yg, zg = sph2cart(GLON.ravel(), GLAT.ravel())

# --- SAFETY: użycie losowego podzbioru dla RBF żeby uniknąć O(N^3) ---
max_rbf_points = 2000  # zmniejsz jeśli na Twoim komputerze nadal będzie za dużo
if x_obs.size > max_rbf_points:
    idx = np.random.choice(x_obs.size, max_rbf_points, replace=False)
    x_rbf, y_rbf, z_rbf, rho_rbf_vals = x_obs[idx], y_obs[idx], z_obs[idx], rho_obs[idx]
    print(f"Używam podzbioru {max_rbf_points} punktów do RBF (z {x_obs.size})")
else:
    x_rbf, y_rbf, z_rbf, rho_rbf_vals = x_obs, y_obs, z_obs, rho_obs

try:
    rbf = Rbf(x_rbf, y_rbf, z_rbf, rho_rbf_vals, function='multiquadric', epsilon=0.5)
    rho_rbf = rbf(xg, yg, zg).reshape(GLAT.shape)
except MemoryError as e:
    print("MemoryError podczas tworzenia RBF:", e)
    rho_rbf = np.full(GLAT.shape, np.nan)
except Exception as e:
    print("Błąd podczas RBF:", e)
    rho_rbf = np.full(GLAT.shape, np.nan)

# 5) griddata (lin.)
points = np.vstack([lons, lats]).T
grid_points = np.vstack([GLON.ravel(), GLAT.ravel()]).T
rho_griddata = griddata(points, rho_obs, grid_points, method='linear', fill_value=np.nan).reshape(GLAT.shape)

# 6) Referencyjne pole "true" na gridzie (do ewaluacji)
LT_grid = (12 + GLON/15.0) % 24
rho_grid_true = (3e-12 * (1 + 0.6 * np.cos(np.deg2rad(GLAT))**2)
                 * (1 + 0.2 * np.sin(2*np.pi*LT_grid/24.0))
                 * (1 + 0.1 * np.cos(np.deg2rad(GLON*2))))

# 7) RMSE (bezpiecznie)
def safe_rmse(pred, truth):
    mask = ~np.isnan(pred) & ~np.isnan(truth)
    if mask.sum() == 0:
        return np.nan
    return np.sqrt(np.mean((pred[mask] - truth[mask])**2))

rmse_rbf = safe_rmse(rho_rbf, rho_grid_true)
rmse_gd = safe_rmse(rho_griddata, rho_grid_true)

# 8) Zapis do netCDF z fallbackiem
ds = xr.Dataset(
    {
        "rho_rbf": (("lat", "lon"), rho_rbf),
        "rho_griddata": (("lat", "lon"), rho_griddata),
        "rho_true_grid": (("lat", "lon"), rho_grid_true)
    },
    coords={"lat": grid_lat, "lon": grid_lon}
)
try:
    ds.to_netcdf("interp_demo_output.nc")
    print("Zapisano: interp_demo_output.nc")
except Exception as e:
    print("Nie udało się zapisać NetCDF (brak backendu netCDF4/h5netcdf?). Błąd:", e)
    print("Zapisuję fallback jako .npz")
    np.savez("interp_demo_output.npz", rho_rbf=rho_rbf, rho_griddata=rho_griddata, rho_true_grid=rho_grid_true)

# 9) Wykresy 2D (oryginalne)
plt.figure(figsize=(12, 5))
plt.subplot(1,3,1)
plt.scatter(lons, lats, c=rho_obs, s=8)
plt.title("Próbki (obs)")
plt.xlabel("Lon"); plt.ylabel("Lat")
plt.colorbar(label="rho (obs)")

plt.subplot(1,3,2)
plt.imshow(rho_rbf, origin='lower', extent=[-180,180,-90,90], aspect='auto')
plt.title(f"RBF (RMSE={rmse_rbf:.2e})")
plt.xlabel("Lon"); plt.ylabel("Lat")
plt.colorbar(label="rho_rbf")

plt.subplot(1,3,3)
plt.imshow(rho_griddata, origin='lower', extent=[-180,180,-90,90], aspect='auto')
plt.title(f"griddata (RMSE={rmse_gd:.2e})")
plt.xlabel("Lon"); plt.ylabel("Lat")
plt.colorbar(label="rho_griddata")

plt.tight_layout()
plt.savefig("interp_demo_plot.png", dpi=150)
plt.show()

print("Liczba próbek:", lons.size)
print("RMSE RBF:", rmse_rbf)
print("RMSE griddata:", rmse_gd)
print("Zapisane: interp_demo_output.nc, interp_demo_plot.png")

# -----------------------
# 10) DODATKOWE: 3D WIZUALIZACJE NA KULI (POPRAWIONE, DOWNSAMPLE + FALLBACK)
# -----------------------
# Przygotuj siatkę 3D (kształt jak GLAT/GLON)
Xg = xg.reshape(GLAT.shape)
Yg = yg.reshape(GLAT.shape)
Zg = zg.reshape(GLAT.shape)

# Kolorowanie: normalizuj względem referencyjnego pola (rho_grid_true)
vmin = np.nanmin(rho_grid_true)
vmax = np.nanmax(rho_grid_true)
norm = plt.Normalize(vmin=vmin, vmax=vmax)
sm = cm.ScalarMappable(norm=norm, cmap='viridis')

def facecolors_from_data(data2d):
    """Zwraca facecolors RGBA dla powierzchni; NaN -> alpha=0."""
    colors = sm.to_rgba(data2d)  # shape (M,N,4)
    nanmask = np.isnan(data2d)
    if nanmask.any():
        colors[nanmask, :] = np.array([0.0, 0.0, 0.0, 0.0])
    return colors

# --- DOWNSAMPLE dla rysunku 3D (zostaw pełne dane w pamięci) ---
# dobierz krok tak, by rysunek miał ~50-120 rzędów (miarka: max 80)
max_plot_rows = 80
step = max(1, int(np.ceil(GLAT.shape[0] / max_plot_rows)))
# opcjonalnie możesz ustawić statycznie step = 3 lub 4
# step = 4

Xg_ds = Xg[::step, ::step]
Yg_ds = Yg[::step, ::step]
Zg_ds = Zg[::step, ::step]

rho_rbf_ds = None if rho_rbf is None else rho_rbf[::step, ::step]
rho_gd_ds = rho_griddata[::step, ::step]
rho_true_ds = rho_grid_true[::step, ::step]

cols_rbf_ds = None
if rho_rbf is not None:
    cols_rbf_ds = facecolors_from_data(rho_rbf_ds)
cols_gd_ds = facecolors_from_data(rho_gd_ds)

# Tworzenie figury 3D z trzema panelami (z obsługą błędów)
fig = plt.figure(figsize=(18, 6))

# 3D scatter: próbki na kuli (kolorowane wg rho_obs)
ax1 = fig.add_subplot(1, 3, 1, projection='3d')
p = ax1.scatter(x_obs, y_obs, z_obs, c=rho_obs, cmap='viridis', s=6, depthshade=True)
ax1.set_title("Próbki (na kuli)")
try:
    ax1.set_box_aspect([1,1,1])
except Exception:
    pass
ax1.set_axis_off()
fig.colorbar(p, ax=ax1, shrink=0.6, pad=0.05, label='rho_obs')

# Powierzchnia RBF (downsampled)
ax2 = fig.add_subplot(1, 3, 2, projection='3d')
try:
    if rho_rbf is not None and not np.all(np.isnan(rho_rbf_ds)):
        surf2 = ax2.plot_surface(Xg_ds, Yg_ds, Zg_ds, rstride=1, cstride=1,
                                 facecolors=cols_rbf_ds, linewidth=0, antialiased=False, shade=False)
        ax2.set_title(f"RBF na kuli (RMSE={rmse_rbf:.2e})")
    else:
        # fallback informacyjny
        ax2.text(0, 0, 0, "RBF failed / all NaN", horizontalalignment='center', verticalalignment='center')
        ax2.set_title("RBF na kuli (brak danych)")
    try:
        ax2.set_box_aspect([1,1,1])
    except Exception:
        pass
    ax2.set_axis_off()
    fig.colorbar(sm, ax=ax2, shrink=0.6, pad=0.05, label='rho')
except Exception as e:
    # Jeśli plot_surface wyrzuci błąd (np. zbyt ciężkie), narysuj rozproszony punktowy fallback
    ax2.cla()
    ax2.set_title("RBF (fallback scatter)")
    ax2.scatter(Xg_ds.ravel(), Yg_ds.ravel(), Zg_ds.ravel(), c=rho_rbf_ds.ravel(), cmap='viridis', s=8)
    ax2.set_axis_off()
    try:
        ax2.set_box_aspect([1,1,1])
    except Exception:
        pass
    fig.colorbar(sm, ax=ax2, shrink=0.6, pad=0.05, label='rho')
    print("Uwaga: plot_surface dla RBF nie powiódł się, użyto scatter jako fallback. Błąd:", e)

# Powierzchnia griddata (downsampled)
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
try:
    if not np.all(np.isnan(rho_gd_ds)):
        surf3 = ax3.plot_surface(Xg_ds, Yg_ds, Zg_ds, rstride=1, cstride=1,
                                 facecolors=cols_gd_ds, linewidth=0, antialiased=False, shade=False)
        ax3.set_title(f"griddata na kuli (RMSE={rmse_gd:.2e})")
    else:
        ax3.text(0, 0, 0, "griddata failed / all NaN", horizontalalignment='center', verticalalignment='center')
        ax3.set_title("griddata na kuli (brak danych)")
    try:
        ax3.set_box_aspect([1,1,1])
    except Exception:
        pass
    ax3.set_axis_off()
    fig.colorbar(sm, ax=ax3, shrink=0.6, pad=0.05, label='rho')
except Exception as e:
    ax3.cla()
    ax3.set_title("griddata (fallback scatter)")
    ax3.scatter(Xg_ds.ravel(), Yg_ds.ravel(), Zg_ds.ravel(), c=rho_gd_ds.ravel(), cmap='viridis', s=8)
    ax3.set_axis_off()
    try:
        ax3.set_box_aspect([1,1,1])
    except Exception:
        pass
    fig.colorbar(sm, ax=ax3, shrink=0.6, pad=0.05, label='rho')
    print("Uwaga: plot_surface dla griddata nie powiódł się, użyto scatter jako fallback. Błąd:", e)

plt.tight_layout()
plt.savefig("interp_demo_plot_3d.png", dpi=200)
plt.show()
print("Zapisane: interp_demo_plot_3d.png")
