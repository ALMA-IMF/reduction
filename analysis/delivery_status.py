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
import subprocess

from compare_images import make_comparison_image

from before_after_selfcal_quicklooks import get_selfcal_number
from imstats import parse_fn

cwd = os.getcwd()
basepath = '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020'
os.chdir(basepath)

datatable = {}

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in (3,6):
        for imtype in ('cleanest', 'bsens', '7m12m', '7m12m_bsens'):

            # for not all-in-the-same-place stuff
            fns = [x for x in glob.glob(f"{field}/B{band}/{imtype}/{field}*_B{band}_*selfcal*.image.tt0*.fits")
                   if 'robust0_' in x]

            config = '7M12M' if '7m' in imtype else '12M'


            if any(fns):
                print("Found hits for ",field, band, imtype)
                selfcal_nums = [get_selfcal_number(fn) for fn in fns]

                last_selfcal = max(selfcal_nums)

                if last_selfcal > 0:
                    if any('finaliter' in x for x in fns):
                        postselfcal_name = [x for x in fns if f'selfcal{last_selfcal}_finaliter' in x if 'diff' not in x][0]
                    else:
                        postselfcal_name = [x for x in fns if f'selfcal{last_selfcal}' in x if 'diff' not in x][0]

                    preselfcal_name = postselfcal_name.replace(f"_selfcal{last_selfcal}","_preselfcal")
                    if "_finaliter" in preselfcal_name:
                        preselfcal_name = preselfcal_name.replace("_finaliter","")
                    if not os.path.exists(preselfcal_name) and '_v0.1' in preselfcal_name:
                        preselfcal_name = preselfcal_name.replace("_v0.1", "")
                    if not os.path.exists(preselfcal_name):
                        print(f"No preselfcal file called {preselfcal_name} found, using alternatives")
                        # try alternate naming scheme
                        preselfcal_name = postselfcal_name.replace(f"_selfcal{last_selfcal}","")
                        if "_finaliter" in preselfcal_name:
                            preselfcal_name = preselfcal_name.replace("_finaliter","")
                    if "_selfcal" in preselfcal_name:
                        raise ValueError("?!?!?!")

                    meta_post = parse_fn(postselfcal_name.split(".image")[0])
                else:
                    postselfcal_name = ''
                    preselfcal_names = [x for x in fns if 'preselfcal' in x]
                    if any(preselfcal_names):
                        preselfcal_name = preselfcal_names[0]
                    else:
                        preselfcal_name = ''

                meta_pre = parse_fn(preselfcal_name.split(".image")[0])

                meta = meta_pre
                meta['pre'] = os.path.exists(preselfcal_name)
                meta['post'] = ('finaliter' in postselfcal_name) and os.path.exists(postselfcal_name)
                if 'uid' not in meta['muid']:
                    meta['muid'] = ''

                datatable[(field, band, imtype)] = meta



                print(fns)
                print(f"{field}_B{band}:{last_selfcal}")
            else:
                print(f"No hits for {field}_B{band}_{config} imtype={imtype}")

            print()


keys = next(iter(datatable.values()))
tbldata = {key: [datatable[xx][key] for xx in datatable] for key in keys}
tbl = Table(tbldata)

tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/tables/delivery_metadata.ecsv',
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/tables/delivery_metadata.html',
          format='ascii.html', overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/tables/delivery_metadata.js.html',
          #formats=formats,
          format='jsviewer')

grid = {'region': list(set(tbl['region'])),}
for band in (3,6):
    for imtype in ('cleanest', 'bsens', '7m12m', '7m12m_bsens'):
        for prepost in ('pre','post'):
            grid[imtype+str(band)+prepost] = ['' for reg in grid['region']]
for row in tbl:
    if row['bsens']:
        if row['array'] == '7M12M':
            imtype = '7m12m_bsens'
        else:
            imtype = 'bsens'
    else:
        if row['array'] == '7M12M':
            imtype = '7m12m'
        else:
            imtype = 'cleanest'
    band = row['band'][1]
    ii = grid['region'].index(row['region'])
    if row['pre']:
        grid[imtype+band+'pre'][ii] = 'X'
    if row['post']:
        grid[imtype+band+'post'][ii] = 'X'

gtbl = Table(grid)
gtbl.sort('region')
gtbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/tables/delivery_grid.html',
           format='ascii.html', overwrite=True, htmldict={'css':'table, th, td, tr { border: 1px solid black; text-align: center}'})

os.chdir(cwd)
