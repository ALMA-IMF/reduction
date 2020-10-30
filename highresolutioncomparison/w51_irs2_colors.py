import numpy as np
import reproject
from astropy.io import fits
from astropy.wcs import WCS

from astropy.visualization import simple_norm
import pylab as pl

fh_b3 = fits.open('W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_bsens_12M_robust0_selfcal4_finaliter.image.tt0.fits')
fh_b6 = fits.open('W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_bsens_12M_robust0_selfcal8_finaliter.image.tt0.fits')

b6_proj_to_b3,covg = reproject.reproject_interp((fh_b6[0].data.squeeze(), WCS(fh_b6[0].header).celestial), WCS(fh_b3[0].header).celestial, shape_out=fh_b3[0].data.squeeze().shape)

imgc = (np.array([b6_proj_to_b3 / np.nanmax(b6_proj_to_b3), b3_plus_b6.squeeze()/np.nanmax(b3_plus_b6), fh_b3[0].data.squeeze()/np.nanmax(fh_b3[0].data)]))


imgcc = imgc[:,1000:2400,1000:2800]
img = simple_norm(imgcc, min_percent=0.1, max_percent=99.9, stretch='asinh')(imgcc.T.swapaxes(0,1))
img[~np.isfinite(img)] = 0

pl.imshow(1-img, origin='lower')
pl.xticks([])
pl.yticks([])
pl.savefig('W51-IRS2_B3_B6.pdf', bbox_inches='tight')
