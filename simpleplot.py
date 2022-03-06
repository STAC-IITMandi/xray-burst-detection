
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

d='11'
lcf = fits.open(f'./misc/xsm/data/2021/11/{d}/calibrated/ch2_xsm_202111{d}_v1_level2.lc')
gtf = fits.open(f'./misc/xsm/data/2021/11/{d}/calibrated/ch2_xsm_202111{d}_v1_level2.gti')

print(lcf.info())
table = lcf['RATE'].data
ranges = gtf['GTI'].data.flatten()
where = np.full(table['TIME'].shape, False)

for start, stop in ranges :
    np.logical_or(
        np.logical_and(table['TIME']>=start, table['TIME']<=stop), 
        where, out=where,
    )

plt.fill_between(table['TIME'], 
    table['RATE']+table['ERROR'], 
    table['RATE']-table['ERROR'],
    color=(1,0,0,0.3), where=where
)
plt.plot(table['TIME'], table['RATE'], linewidth=0.7)
plt.show()
