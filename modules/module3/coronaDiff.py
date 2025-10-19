import matplotlib.pyplot as plt
from scipy import ndimage
import numpy as np
import sunpy.map
from sunpy.data.sample import AIA_193_IMAGE, AIA_193_JUN2012

# map import
aiamap_new = sunpy.map.Map(AIA_193_IMAGE)  # latest data
aiamap_old = sunpy.map.Map(AIA_193_JUN2012)  # earlier data for comparison

# tonal balance
p_new = np.percentile(aiamap_new.data, 10)
p_old = np.percentile(aiamap_old.data, 10)
scale_factor = p_new / p_old if p_old != 0 else 1.0
aiamap_old_eq = aiamap_old.data * scale_factor
aiamap_old_eq = np.clip(aiamap_old_eq, 0, aiamap_new.data.max())

# difference ΔI
diff = aiamap_new.data - aiamap_old_eq
diff[diff < 0] = 0

# ROI based on ΔI
# tresholding based on mean + 1.5 sigma
threshold = np.median(diff) + 1.5 * np.std(diff)
roi_mask = diff > threshold

# smoothing
diff_smooth = ndimage.gaussian_filter(diff, sigma=3)

# visualization
aiamap_diff = sunpy.map.Map(diff_smooth, aiamap_new.meta)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(projection=aiamap_diff)

im = aiamap_diff.plot(axes=ax, title="Difference ΔI (NEW - OLD) with ROI based on tresholding")

cbar = plt.colorbar(im, ax=ax, orientation='vertical')
cbar.set_label("ΔI [DN] — pixel brightness difference (Digital Numbers)", fontsize=12)

# axes labels
ax.set_xlabel("Solar X [arcsec]", fontsize=12)
ax.set_ylabel("Solar Y [arcsec]", fontsize=12)

ax.set_title("Brightness difference ΔI with marked ROI", fontsize=14)

plt.show()


# Converting ΔI to mass CME

# physical constants
m_p = 1.6726219e-24  # g
He_H_number_fraction = 0.1
mass_per_electron_g = m_p * (1 + 4*He_H_number_fraction) / (1 + 2*He_H_number_fraction)

# Conversion factor ΔB -> number of electrons in the column
C_simple = 1e-10  # [B_ms / electron], approximation
Ne_col = diff_smooth / C_simple

# Pixel area in cm^2 (LASCO approximation)
pixel_area_cm2 = 1e16
Ne_per_pixel = Ne_col * pixel_area_cm2

# Summ ROI
N_e_total = Ne_per_pixel[roi_mask].sum()

# mass CME
M_cme_g = N_e_total * mass_per_electron_g
M_cme_kg = M_cme_g / 1000.0

print(f"Estimated CME mass: {M_cme_kg:.2e} kg")

# Assessing the risk of a CME reaching Earth

# Sample CME velocity data (km/s)
v_kms = 800 
v_ms = v_kms * 1e3

# Earth-Sun distance
d_earth_m = 1.496e11  # [m]

# CME kinetic energy
E_kin_J = 0.5 * M_cme_kg * v_ms**2
E_kin_erg = E_kin_J * 1e7

# Estimated time to reach Earth (without taking into account deceleration)
t_hours = d_earth_m / v_ms / 3600.0

print("\n=== DYNAMICS ANALYSIS CME ===")
print(f"CME velocity: {v_kms:.0f} km/s")
print(f"Kinetic energy: {E_kin_J:.2e} J ({E_kin_erg:.2e} erg)")
print(f"Estimated time to reach Earth: {t_hours:.1f} h")

# Risk assessment based on weight and speed

if M_cme_kg < 1e12:
    mass_risk = "low mass – rather harmless structure"
elif M_cme_kg < 1e13:
    mass_risk = " medium mass – possible weak geomagnetic influence"
else:
    mass_risk = "large mass – potentially strong CME impact"

#Speed ​​and arrival time – the second component of risk
if v_kms < 400:
    speed_risk = "slow ejection – it will probably not arrive or will disperse"
elif v_kms < 800:
    speed_risk = "moderate speed – possible contact with the magnetosphere"
else:
    speed_risk = "fast ejection – high probability of reaching Earth"

# global risk assessment
if v_kms > 800 and M_cme_kg > 1e13:
    global_risk = "⚠️ HIGH risk of CME hitting Earth"
elif v_kms > 500 and M_cme_kg > 1e12:
    global_risk = "⚠️ MEDIUM risk – CME may partially impact Earth"
else:
    global_risk = "✅ LOW risk – CME likely to dissipate before reaching Earth"

print("\n=== CME RISK ASSESSMENT ===")
print(f"CME mass: {M_cme_kg:.2e} kg → {mass_risk}")
print(f"Velocity: {v_kms:.0f} km/s → {speed_risk}")
print(f"Global risk: {global_risk}")

