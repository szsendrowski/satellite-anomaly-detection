import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt, exp

# === STAŁE FIZYCZNE ===
MU = 3.986004418e14   # m^3/s^2, gravitational Earth parameter 
R_EARTH = 6371000.0   # m, Earth radius


def rho_exponential(h, rho_ref, h_ref, H):
    #atmospheric density model: exponential
    return rho_ref * np.exp(-(h - h_ref) / H)

def circular_velocity(h):
    #Circular speed at a given altitude (for a circular orbit).
    return sqrt(MU / (R_EARTH + h))

def simulate_orbital_decay(B_values, h_start=520e3, h_end=180e3,
                           rho_ref=5e-12, h_ref=520e3, H=60e3,
                           dt=5.0, max_time_days=365):
    max_time = max_time_days * 86400  
    results = {}
    altitudes = np.arange(h_start, h_end - 1, -10.0)  # 10m steps

    for B in B_values:
        a = R_EARTH + h_start
        t = 0.0
        rec = []
        idx = 0
        h = h_start
        while h > h_end and t < max_time:
            rho = rho_exponential(h, rho_ref, h_ref, H)
            adot = - (rho / B) * sqrt(MU * (R_EARTH + h))
            a += adot * dt
            t += dt
            h = a - R_EARTH
            if idx % 100 == 0:
                rec.append({
                    "time_s": t,
                    "time_d": t/86400,
                    "altitude_km": h / 1000,
                    "rho": rho,
                    "v_circular": circular_velocity(h),
                    "B": B
                })
            idx += 1
            if abs(adot) < 1e-12:
                break
        results[B] = pd.DataFrame(rec)
    return results
# simulation parameters
B_values = [20.0, 50.0, 100.0]
results = simulate_orbital_decay(B_values)
# Plotting results
plt.figure(figsize=(6,4))
for B in B_values:
    df = results[B]
    plt.plot(df["altitude_km"], df["time_d"], label=f"B={B} kg/m²")
x_marker = 180  # km
plt.gca().invert_xaxis()
plt.axvline(x=x_marker, color="red", linestyle="--", linewidth=1)
plt.text(x_marker + 50 , plt.ylim()[0] + 0.85*(plt.ylim()[1]-plt.ylim()[0]),
         f"{x_marker} km", color="red", fontsize=10)
plt.xlabel("Height (km)")
plt.ylabel("Time (days)")
plt.title("Change in satellite altitude over time for different ballistic coefficients")
plt.legend()
plt.grid(True)
plt.show()
