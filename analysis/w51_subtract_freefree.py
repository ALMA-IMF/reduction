import numpy as np
from astropy import constants, units as u, table, stats, coordinates, wcs, log, coordinates as coord, convolution, modeling; from astropy.io import fits, ascii
import reproject
fh3mm_r0 = fits.open('W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7.image.tt0.fits')
fh3mm_r2 = fits.open('W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust2_selfcal7_reclean_deeper.image.tt0.pbcor.fits')
fh2cm = fits.open('../../paper_w51_evla/data/W51Ku_BDarray_continuum_2048_both_uniform.hires.clean.image.fits')

rep3mm_r2,_ = reproject.reproject_interp((fh3mm_r2[0].data.squeeze(),
                                          wcs.WCS(fh3mm_r2[0].header).celestial),
                                         wcs.WCS(fh2cm[0].header).celestial,
                                         shape_out=fh2cm[0].data.squeeze().shape)
rep3mm_r0,_ = reproject.reproject_interp((fh3mm_r0[0].data.squeeze(),
                                          wcs.WCS(fh3mm_r0[0].header).celestial),
                                         wcs.WCS(fh2cm[0].header).celestial,
                                         shape_out=fh2cm[0].data.squeeze().shape)

ok = (rep3mm_r2 > 0.001) & (fh2cm[0].data > 0.001).squeeze()
scalefactor_r2 = np.median(rep3mm_r2[ok] / fh2cm[0].data.squeeze()[ok])

diffr2 = rep3mm_r2 - fh2cm[0].data.squeeze() * scalefactor_r2


ok = (rep3mm_r0 > 0.001) & (fh2cm[0].data > 0.001).squeeze()
scalefactor_r0 = np.median(rep3mm_r0[ok] / fh2cm[0].data.squeeze()[ok])
#scalefactor_r0 = 1

diffr0 = rep3mm_r0 - fh2cm[0].data.squeeze() * scalefactor_r0


import pylab as pl
import astropy.visualization

slc = slice(377, 1391), slice(188, 1165)

pl.figure(1)

pl.clf()
norm = astropy.visualization.ImageNormalize(stretch=astropy.visualization.AsinhStretch())
ax1 = pl.subplot(1, 3, 1)
im1 = ax1.imshow(rep3mm_r2[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)
ax1.set_title("3mm robust 2")
ax2 = pl.subplot(1, 3, 2)
im2 = ax2.imshow(diffr2[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)
ax2.set_title("3 mm - 2 cm")
ax3 = pl.subplot(1, 3, 3)
ax3.set_title("2 cm")
im3 = ax3.imshow(fh2cm[0].data.squeeze()[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)

for ax in (ax1,ax2,ax3):
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(direction='in', color='w')

pl.subplots_adjust(wspace=0, hspace=0)

pl.savefig("/Users/adam/work/alma-imf/figures/W51E_b3_r2_minus_freefree.png", bbox_inches='tight', dpi=300)

for ax in (ax1,ax2,ax3):
    ax.axis((531.3346774193549, 694.8245967741934, 704.322802419355, 895.3893346774196))
for im in (im1,im2,im3):
    im.set_clim(-0.0001, 0.002)

pl.savefig("/Users/adam/work/alma-imf/figures/W51E_b3_r2_minus_freefree_zoom1.png", bbox_inches='tight', dpi=300)



pl.clf()
norm = astropy.visualization.ImageNormalize(stretch=astropy.visualization.AsinhStretch())
ax1 = pl.subplot(1, 3, 1)
im1 = ax1.imshow(rep3mm_r0[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)
ax1.set_title("3mm robust 0")
ax2 = pl.subplot(1, 3, 2)
im2 = ax2.imshow(diffr0[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)
ax2.set_title("3 mm - 2 cm")
ax3 = pl.subplot(1, 3, 3)
ax3.set_title("2 cm")
im3 = ax3.imshow(fh2cm[0].data.squeeze()[slc], origin='lower', interpolation='none', vmin=-0.001, vmax=0.01, norm=norm)

for ax in (ax1,ax2,ax3):
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(direction='in', color='w')

pl.subplots_adjust(wspace=0, hspace=0)

pl.savefig("/Users/adam/work/alma-imf/figures/W51E_b3_r0_minus_freefree.png", bbox_inches='tight', dpi=300)

for ax in (ax1,ax2,ax3):
    ax.axis((531.3346774193549, 694.8245967741934, 704.322802419355, 895.3893346774196))
for im in (im1,im2,im3):
    im.set_clim(-0.0001, 0.002)

pl.savefig("/Users/adam/work/alma-imf/figures/W51E_b3_r0_minus_freefree_zoom1.png", bbox_inches='tight', dpi=300)
