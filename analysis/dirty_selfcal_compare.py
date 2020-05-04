import numpy as np
import warnings
import glob
import os
from astropy.io import fits
from astropy import visualization
from astropy.table import Table, Column
from spectral_cube import SpectralCube
from astropy.stats import mad_std
from astropy import log
import pylab as pl

from before_after_selfcal_quicklooks import make_comparison_image, get_selfcal_number

cwd = os.getcwd()
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'
os.chdir(basepath)
prepostpath = '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/comparisons/prepost/'

allstats = []

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
#for field in ("G333.60",):
    for band in (3,6):
        for imtype in ('cleanest', 'bsens', '7m12m', ):

            prefns = [x for x in
                    glob.glob(f"{basepath}/{field}*_B{band}_*_{imtype}_*preselfcal*.image.tt0")
                    if 'robust0_' in x]
            postfns = [fn.replace("pre","post") for fn in prefns]

            config = '7M12M' if '7m' in imtype else '12M'

            for pre, post in zip(prefns, postfns):
                print(pre, post)

                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore')
                        ax1, ax2, ax3, fig, diffstats = make_comparison_image(pre,
                                post)
                    pl.savefig(f"{prepostpath}/{field}_B{band}_{config}_post-pre_dirty_comparison.png",
                            bbox_inches='tight')
                except IndexError:
                    raise
                except Exception as ex:
                    log.error(f"Failure for pre={pre} post={post}")
                    log.error((field, band, config, imtype, ex))
                    continue

                allstats.append(diffstats)

                print(prefns, postfns)
            else:
                print(f"No hits for {field}_B{band}_{config}")

            print()
            print()

#with open('prepost_dirty_stats.json', 'w') as fh:
#    json.dump(allstats, fh)

os.chdir(cwd)

