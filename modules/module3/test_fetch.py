import matplotlib.pyplot as plt
from scipy import ndimage

import sunpy.map
from sunpy.data.sample import AIA_193_JUN2012

aiamap_mask = sunpy.map.Map(AIA_193_JUN2012)
aiamap = sunpy.map.Map(AIA_193_JUN2012)

#mask of brihtest 10%
mask = aiamap.data < aiamap.max() * 0.10

aiamap_mask.mask = mask

fig = plt.figure()
ax = fig.add_subplot(projection=aiamap_mask)
aiamap_mask.plot(axes=ax)
plt.colorbar()
plt.show()

#2D Gaussian smoothing function
data2 = ndimage.gaussian_filter(aiamap.data * ~mask, 14)

data2[data2 < 100] = 0
#map with this smoothed data
aiamap2 = sunpy.map.Map(data2, aiamap.meta)

#counrting connected regions
labels, n = ndimage.label(aiamap2.data)

fig = plt.figure()
ax = fig.add_subplot(projection=aiamap)
aiamap.plot(axes=ax)
ax.contour(labels)
plt.figtext(0.3, 0.2, f'Number of regions = {n}', color='white')

plt.show()