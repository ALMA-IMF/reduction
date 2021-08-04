print("Beginning imports")
import glob
from astropy.io import fits
from astropy import visualization
import warnings
from astropy.table import Table


import os
import time
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.stats import mad_std
import pylab as pl
import radio_beam
import tempfile
import dask.array as da
import dask
from pathlib import Path
from spectral_cube import SpectralCube,DaskSpectralCube
from spectral_cube.lower_dimensional_structures import Projection
print("Completed imports")

import pylab as pl
print("Imported pylab")

warnings.simplefilter('ignore')

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'

files = glob.glob(basepath+"/*.weight")

stats = {}

for fn in files:
    basefn = os.path.basename(fn)

    cube = SpectralCube.read(fn, format='casa_image')
    yy, xx = cube.shape[1]//2, cube.shape[2]//2

    # edge channels are often waaaay off
    wtspc = cube[:, yy, xx]

    # remove gigantic outliers
    med = np.nanmedian(wtspc)
    madstd = mad_std(wtspc, ignore_nan=True)
    wtspc[wtspc < med - 10 * madstd] = np.nan
    wtspc[wtspc > med + 10 * madstd] = np.nan

    mn = np.nanmean(wtspc)
    std = np.nanstd(wtspc)
    minim = np.nanmin(wtspc)
    mx = np.nanmax(wtspc)
    maxdiff = mx - minim
    fraction_deviation = maxdiff / mn

    stats[basefn] = {'mean': mn, 'median': med, 'mad': madstd, 'min': minim, 'max': mx, 'std': std, 'maxdiff': maxdiff, 'fraction_deviation': fraction_deviation}
    print(basefn, stats[basefn])

    # if fraction_deviation > 0.01:
    pl.figure(1).clf()
    pl.plot(cube.spectral_axis, wtspc.value, label=f'$W={med:0.3f}\pm{madstd:0.3f}$; $F_{{dev}} = {fraction_deviation:10.3g}$')
    pl.xlabel(cube.spectral_axis.unit.to_string('latex'))
    pl.ylabel("Weight")
    pl.title(basefn)
    pl.legend(loc='best')
    pl.savefig(f'/orange/adamginsburg/web/secure/ALMA-IMF/cube_quicklooks/weights/{basefn}_center.png')

fns = list(stats.keys())
cols = {'name': fns}
for row in stats[fn]:
    cols[row] = [stats[key][row] for key in fns]

tbl = Table(cols)
tbl.write('/orange/adamginsburg/web/secure/ALMA-IMF/cube_quicklooks/weights/weight_stats_table.ipac', format='ascii.ipac', overwrite=True)
