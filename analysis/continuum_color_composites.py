import os
import glob
import numpy as np
import reproject
from astropy.io import fits
from astropy.wcs import WCS

from astropy.visualization import simple_norm
import pylab as pl

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults'


for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for imtype in ('cleanest', 'bsens', '7m12m', ):

        pl.close('all')
        pl.figure()

        b3path = glob.glob(f'{basepath}/{field}/B3/{imtype}/*robust0_*finaliter.image.tt0.fits')
        b6path = glob.glob(f'{basepath}/{field}/B6/{imtype}/*robust0_*finaliter.image.tt0.fits')
        if len(b3path) == 1:
            b3path = b3path[0]
        else:
            continue
        if len(b6path) == 1:
            b6path = b6path[0]
        else:
            continue

        try:
            fh_b3 = fits.open(b3path)
            fh_b6 = fits.open(b6path)
        except Exception as ex:
            print(ex)

        b6_proj_to_b3,covg = reproject.reproject_interp((fh_b6[0].data.squeeze(),
                                                         WCS(fh_b6[0].header).celestial),
                                                        WCS(fh_b3[0].header).celestial,
                                                        shape_out=fh_b3[0].data.squeeze().shape)

        b3_plus_b6 = (fh_b3[0].data+b6_proj_to_b3)

        imgc = (np.array([b6_proj_to_b3 / np.nanmax(b6_proj_to_b3), b3_plus_b6.squeeze()/np.nanmax(b3_plus_b6), fh_b3[0].data.squeeze()/np.nanmax(fh_b3[0].data)]))

        zrx = imgc.shape[2] // 5
        zry = imgc.shape[1] // 5

        imgcc = imgc[:, zry:-zry, zrx:-zrx]
        img = simple_norm(imgcc, min_percent=0.1, max_percent=99.9, stretch='asinh')(imgcc.T.swapaxes(0,1))
        img[~np.isfinite(img)] = 0

        pl.imshow(1-img, origin='lower')
        pl.xticks([])
        pl.yticks([])

        if not os.path.exists(f'{basepath}/{field}/continuum_colorcomposites'):
            os.mkdir(f'{basepath}/{field}/continuum_colorcomposites')
        pl.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_colorcomposite.pdf', bbox_inches='tight')
        pl.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_colorcomposite.png', bbox_inches='tight', dpi=300)
