import os
import warnings
import glob

from astropy import log
from pathlib import Path

from compare_images import make_comparison_image

cwd = os.getcwd()
maypath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/May2021Release/')
junepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/June2021Release/')
outpath = Path('/orange/adamginsburg/web/secure/ALMA-IMF/compare_May2021_June2021/')

# configurable, kinda
overwrite = False

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in ('B3','B6'):
        for imtype,itgl in zip(('cleanest', 'bsens',),# 'bsens_nobright', 'bsens_nobright'),
                               ('continuum_merged_12M', 'bsens_12M',)):# 'bsens_noco_12M', 'bsens_non2hp_12M')):

            suffix = '.image.tt0'
            config = '12M'
            #for suffix in ('image.tt0.fits', 'image.tt0.pbcor.fits',
            #               "image.tt0", "model.tt0", "image.tt1", "model.tt1", "psf.tt0",
            #               "psf.tt1", "residual.tt0", "residual.tt1", "mask"):

            robust = 0
            
            # G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter.image.tt0/ 
            path1 = junepath / field / band / imtype / f"{field}_{band}_*{config}_robust{robust}_selfcal*_finaliter{suffix}"
            path2 = maypath / field / band / imtype / f"{field}_{band}_*{config}_robust{robust}_selfcal*_finaliter{suffix}"

            print(f"{field} {band} {imtype}:{itgl}")

            fn1 = glob.glob(str(path1))
            fn2 = glob.glob(str(path2))
            if len(fn1) == 1:
                fn1 = fn1[0]
            elif len(fn1) == 0:
                if len(fn2) > 0:
                    print(f"Found {fn2} but not {path1}")
                else:
                    print("Found neither.")
                continue
            else:
                raise
            if len(fn2) == 1:
                fn2 = fn2[0]
            elif len(fn2) == 0:
                print(f"Found {fn1} but not {path2}")
                continue
            else:
                raise

            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    ax1, ax2, ax3, fig, diffstats = make_comparison_image(fn2,
                                                                          fn1,
                                                                          title1='May 2021',
                                                                          title2='June 2021',
                                                                          writediff=True,
                                                                          allow_zero_diff=True
                                                                         )
                if not os.path.exists(f"{outpath}"):
                    os.mkdir(f"{outpath}")
                fig.savefig(f"{outpath}/{field}_B{band}_{config}_{imtype}_MvJ_comparison.png", bbox_inches='tight')
            except IndexError:
                raise
            except Exception as ex:
                log.error(f"Failure for {path1} {path2}")
                log.error((field, band, config, imtype, ex))
                raise ex
                #continue
