"""
Compare delivered files to auto-produced ones
"""
import pylab as pl
import numpy as np
import glob
import os
from astropy.io import fits
from astropy.stats import mad_std
from astropy import visualization
from spectral_cube import SpectralCube

from compare_images import make_comparison_image

filelist = glob.glob("/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/*/*/*/*.image.tt0.pbcor.fits")
imresults = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'

for fn in filelist:
    pl.clf()
    basename = os.path.split(fn)[-1]
    if os.path.exists(f'{imresults}/{basename}'):
        autoname = f'{imresults}/{basename}'
    else:
        pfx = basename.split("uid")[0]
        sfx = basename.split("continuum_merged")[1]
        glb = glob.glob(f"{imresults}/{pfx}*{sfx}")
        if len(glb) == 1:
            autoname = glb[0]
        else:
            print(f"Skipping {basename} because there's no match.")
            continue

    field = basename.split("_uid")[0].split("/")[-1]

    fh1 = fits.open(fn)
    fh2 = fits.open(autoname)

    if (fh1[0].data.shape == fh2[0].data.shape):
        make_comparison_image(fn, autoname, title1='Delivered', title2='Auto')
        pl.savefig(f"comparisons/auto_vs_not_{basename.replace('.fits','')}.png", bbox_inches='tight', dpi=200)
    else:
        print(f"Skipping {fn} because there was a shape mismatch.")
