import pylab as pl
import numpy as np
import glob
import os
from astropy.io import fits
from astropy.stats import mad_std
from astropy import visualization
from spectral_cube import SpectralCube

from compare_images import make_comparison_image

print("{4:14s}{0:>15s} {1:>15s} {2:>15s} {3:>15s} {5:>15s} {6:>15s}".format("bsens_sum", "bsens_mad",  "clean_sum",  "clean_mad", "field & band", "diff_sum", "diff_mad"))

basepath = "/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/"

for fn in glob.glob(f"{basepath}/*/*/bsens/*.image.tt0.pbcor.fits"):
    pl.clf()
    bsens = fn
    clean = fn.replace("_bsens","").replace("/bsens/","/cleanest/")
    #print(os.path.exists(bsens), os.path.exists(clean))
    field = fn.split("_uid")[0].split("/")[-1]

    filepath = fn.split("bsens")[0]

    bsens_fh = fits.open(bsens)
    try:
        clean_fh = fits.open(clean)
    except Exception as ex:
        print(ex)
        continue

    if (bsens_fh[0].data.shape == clean_fh[0].data.shape):
        bsd = bsens_fh[0].data
        cld = clean_fh[0].data
        diff = bsd-cld
        bsens_fh[0].data = diff
        try:
            bsens_fh.writeto(fn.replace("_bsens_reclean", "_bsens_minus_clean_reclean"), overwrite=False)
        except Exception as ex:
            print(ex)
        print(f"{field:14s}"
              f"{bsd[np.isfinite(bsd)].sum():15.3f} {mad_std(bsd, ignore_nan=True):15.5f} "
              f"{cld[np.isfinite(cld)].sum():15.3f} {mad_std(cld, ignore_nan=True):15.5f} "
              f"{diff[np.isfinite(diff)].sum():15.3f} {mad_std(diff, ignore_nan=True):15.5f} "
             )
        try:
            make_comparison_image(bsens, clean)
        except Exception as ex:
            if "operands could not be broadcast together with shapes" in str(ex):
                print("Shapes: ",bsens_fh[0].data.shape, clean_fh[0].data.shape)
            print(ex)
        if not os.path.exists(f'{filepath}/comparisons/'):
            os.mkdir(f'{filepath}/comparisons/')
        pl.savefig(f"{filepath}/comparisons/{field}_12M_bsens_vs_cleanest_comparison.png", bbox_inches='tight', dpi=200)
    else:
        print(f"Skipping {bsens} because there was a shape mismatch.")
