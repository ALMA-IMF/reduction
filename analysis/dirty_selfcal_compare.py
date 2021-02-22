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
prepostpath = '/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/comparisons/prepost/'
octoberpath = '/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/'

import imstats

tbl = imstats.savestats(basepath=octoberpath)

#tbl = Table.read('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/metadata.ecsv')
tbl.add_column(Column(name='casaversion_pre', data=['             ']*len(tbl)))
tbl.add_column(Column(name='casaversion_post', data=['             ']*len(tbl)))
tbl.add_column(Column(name='scMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

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

                matchrow = ((tbl['region'] == field) &
                            (tbl['band'] == f'B{band}') &
                            (tbl['array'] == ('12Monly' if config == '12M' else config)) &
                            (tbl['robust'] == 'r0.0') &
                            (tbl['bsens'] if 'bsens' in imtype else ~tbl['bsens'])
                           )
                tbl['scMaxDiff'][matchrow] = diffstats['max']
                tbl['scMinDiff'][matchrow] = diffstats['min']
                tbl['scMADDiff'][matchrow] = diffstats['mad']
                tbl['scMeanDiff'][matchrow] = diffstats['mean']
                tbl['scMedianDiff'][matchrow] = diffstats['median']
                tbl['dr_pre'][matchrow] = diffstats['dr_pre']
                tbl['dr_post'][matchrow] = diffstats['dr_post']
                tbl['max_pre'][matchrow] = diffstats['max_pre']
                tbl['max_post'][matchrow] = diffstats['max_post']
                tbl['min_pre'][matchrow] = diffstats['min_pre']
                tbl['min_post'][matchrow] = diffstats['min_post']
                tbl['mad_pre'][matchrow] = diffstats['mad_pre']
                tbl['mad_post'][matchrow] = diffstats['mad_post']
                tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']
                if pre.endswith('fits'):
                    tbl['casaversion_pre'][matchrow] = fits.getheader(pre)['ORIGIN']
                    tbl['casaversion_post'][matchrow] = fits.getheader(post)['ORIGIN']

                print(prefns, postfns)
            else:
                print(f"No hits for {field}_B{band}_{config}")

            print()
            print()


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'scMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

tbl.write('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/tables/metadata_sc_dirty.ecsv',
          overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/tables/metadata_sc_dirty.html',
          formats=formats,
          format='ascii.html', overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/tables/metadata_sc_dirty.tex',
          formats=formats,
          overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/October2020/tables/metadata_sc_dirty.js.html',
          #formats=formats,
          format='jsviewer')



os.chdir(cwd)
