import numpy as np
import itertools
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
import subprocess


cwd = os.getcwd()
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/'
os.chdir(basepath)

datatable = {}

fieldlist = "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41"

rows = []

for imtype,dirname in zip(('12M', '7M12M'), ('fullcubes_12m', 'fullcubes_7m12m')):
    rows.append(f"{imtype}\n")
    for band in (3,6):
        rows.append(f"B{band}\n")

        rows.append("    " + " ".join([f"{x:10s}" for x in fieldlist.split()]) + "\n")
        spws = range(4) if band == 3 else range(8)
        for spw in spws:
            exists = [os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_spw{spw}.image.pbcor')
                      or ("WIPim" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_spw{spw}.image')
                          else "WIPpsf" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_spw{spw}.psf')
                          else False)
                      for field in fieldlist.split()]

            rows.append(f"{spw:<4d}" + " ".join([f"{str(x):10s}" for x in exists]) + "\n")

        for field in fieldlist.split():
            datatable[field] = {3: {ii:{} for ii in range(4)},
                                6: {ii:{} for ii in range(8)}}

            for spw in spws:

                # /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/G008.67_B6_spw5_12M_spw5.image/
                datatable[field][band][spw][imtype] = {"image": os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_spw{spw}.image'),
                                                       "pbcor": os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_spw{spw}.image.pbcor'),}
    rows.append("\n")

import json
with open('/orange/adamginsburg/web/secure/ALMA-IMF/tables/line_completeness_grid.json', 'w') as fh:
    json.dump(datatable, fh)

with open('/orange/adamginsburg/web/secure/ALMA-IMF/tables/line_completeness_grid.tbl', 'w') as fh:
    fh.writelines(rows)


os.chdir(cwd)
