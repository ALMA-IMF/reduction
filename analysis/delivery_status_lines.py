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

# baseband, spw: name
line_maps = {(3,0): 'n2hp',
             (6,1): 'sio'}


for imtype,dirname in zip(('12M', '7M12M', '12M', '7M12M'),
                          ('fullcubes_12m', 'fullcubes_7m12m',
                           'linecubes_12m', 'linecubes_7m12m')):
    rows.append(f"{imtype} - {dirname}\n")
    for band in (3,6):
        sband = f'B{band}'
        rows.append(f"{sband} {imtype} {dirname}\n")

        rows.append("    " + " ".join([f"{x:10s}" for x in fieldlist.split()]) + "\n")
        spws = range(4) if band == 3 else range(8)
        for spw in spws:
            if 'fullcube' in dirname:
                spw2 = f'spw{spw}'
            else:
                if (band, spw) in line_maps:
                    spw2 = line_maps[(band, spw)]
                else:
                    continue
            exists = [os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_{spw2}.image.pbcor')
                      or ("WIPim" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_{spw2}.image')
                          else "WIPpsf" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_{spw2}.psf')
                          else False)
                      for field in fieldlist.split()]

            rows.append(f"{spw2:5s}" + " ".join([f"{str(x):10s}" for x in exists]) + "\n")

        for field in fieldlist.split():
            if field not in datatable:
                datatable[field] = {'B3': {f'spw{ii}':{} for ii in range(4)},
                                    'B6': {f'spw{ii}':{} for ii in range(8)}}

            for spw in spws:
                if 'fullcube' in dirname:
                    spw2 = f'spw{spw}'
                else:
                    if (band, spw) in line_maps:
                        spw2 = line_maps[(band, spw)]
                        if spw2 not in datatable[field][sband]:
                            datatable[field][sband][spw2] = {}
                    else:
                        continue

                # /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/G008.67_B6_spw5_12M_spw5.image/
                datatable[field][sband][spw2][imtype] = {"image": os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_{spw2}.image'),
                                                         "pbcor": os.path.exists(f'{basepath}/{field}_B{band}_spw{spw}_{imtype}_{spw2}.image.pbcor'),
                                                         "WIP": ("WIPim" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_{spw2}.image')
                                                                 else "WIPpsf" if os.path.exists(f'/blue/adamginsburg/adamginsburg/almaimf/workdir/{field}_B{band}_spw{spw}_{imtype}_{spw2}.psf')
                                                                 else False)
                                                        }
    rows.append("\n")

import json
with open('/orange/adamginsburg/web/secure/ALMA-IMF/tables/line_completeness_grid.json', 'w') as fh:
    json.dump(datatable, fh)

with open('/orange/adamginsburg/web/secure/ALMA-IMF/tables/line_completeness_grid.tbl', 'w') as fh:
    fh.writelines(rows)


os.chdir(cwd)
