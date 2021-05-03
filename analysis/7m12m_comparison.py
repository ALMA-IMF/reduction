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

from compare_images import make_comparison_image

cwd = os.getcwd()
basepath = '/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021'
os.chdir(basepath)

import imstats


tbl = imstats.savestats(basepath=basepath)

#tbl = Table.read('/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021/metadata.ecsv')
tbl.add_column(Column(name='casaversion_7m12m', data=['             ']*len(tbl)))
tbl.add_column(Column(name='casaversion_cleanest', data=['             ']*len(tbl)))
tbl.add_column(Column(name='7m12mMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='7m12mMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='7m12mMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='7m12mMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='7m12mMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='7m12mSumDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='shape', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='ppbeam', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='masksum_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='masksum_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_7m12m', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in (3,6):
        for config in ("7M12M",):


            fns = glob.glob(f"{basepath}/{field}/B{band}/7m12m/*_{config}_robust0_*final*.image.tt0.pbcor.fits")
            if len(fns) > 1:
                raise ValueError("Too many matches!")
            elif len(fns) == 0:
                log.error(f"No matches to field={field} band={band} config={config}")
                continue
                raise ValueError("No matches!")
            fn = fns[0]

            pl.clf()
            f7m12m = fn
            cleanest = fn.replace("_7m12m","").replace("/7m12m/","/cleanest/").replace("_7M12M_","_12M_")
            #print(os.path.exists(7m12m), os.path.exists(clean))
            #field = fn.split("_uid")[0].split("/")[-1]

            filepath = fn.split("7m12m")[0]

            f7m12m_fh = fits.open(f7m12m)
            try:
                clean_fh = fits.open(cleanest)
            except Exception as ex:
                log.error(f"Failed to open 'cleanest' image {cleanest}")
                print(ex)
                continue


            fig = pl.figure(1, figsize=(14,6))

            if fig.get_figheight() != 6:
                fig.set_figheight(6)
            if fig.get_figwidth() != 14:
                fig.set_figwidth(14)

            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    ax1, ax2, ax3, fig, diffstats = make_comparison_image(filename1=cleanest,
                                                                          filename2=f7m12m,
                                                                          title1='cleanest',
                                                                          title2='7m12m',
                                                                          allow_reproj=True
                                                                         )
            except IndexError:
                raise
            except Exception as ex:
                log.error(f"Failure for 7m12m={f7m12m} cleanest={cleanest}")
                log.error((field, band, config, ex))
                raise
                continue

            if not os.path.exists(f"{basepath}/{field}/B{band}/comparisons/"):
                os.mkdir(f"{basepath}/{field}/B{band}/comparisons/")
            pl.savefig(f"{basepath}/{field}/B{band}/comparisons/{field}_B{band}_{config}_7m12m_vs_cleanest_comparison.png",
                       bbox_inches='tight', dpi=200)

            matchrow = ((tbl['region'] == field) &
                        (tbl['band'] == f'B{band}') &
                        (tbl['array'] == ('12Monly' if config == '12M' else config)) &
                        (tbl['robust'] == 'r0.0')
                       )
            tbl['7m12mMaxDiff'][matchrow] = diffstats['max']
            tbl['7m12mMinDiff'][matchrow] = diffstats['min']
            tbl['7m12mMADDiff'][matchrow] = diffstats['mad']
            tbl['7m12mMeanDiff'][matchrow] = diffstats['mean']
            tbl['7m12mMedianDiff'][matchrow] = diffstats['median']
            tbl['7m12mSumDiff'][matchrow] = diffstats['sum']
            tbl['dr_7m12m'][matchrow] = diffstats['dr_pre']
            tbl['dr_cleanest'][matchrow] = diffstats['dr_post']
            tbl['min_7m12m'][matchrow] = diffstats['min_pre']
            tbl['min_cleanest'][matchrow] = diffstats['min_post']
            tbl['max_7m12m'][matchrow] = diffstats['max_pre']
            tbl['max_cleanest'][matchrow] = diffstats['max_post']
            tbl['sum_7m12m'][matchrow] = diffstats['sum_pre']
            tbl['sum_cleanest'][matchrow] = diffstats['sum_post']
            tbl['masksum_7m12m'][matchrow] = diffstats['masksum_pre']
            tbl['masksum_cleanest'][matchrow] = diffstats['masksum_post']
            tbl['shape'][matchrow] = diffstats['shape']
            tbl['ppbeam'][matchrow] = diffstats['ppbeam']
            tbl['mad_7m12m'][matchrow] = diffstats['mad_pre']
            tbl['mad_cleanest'][matchrow] = diffstats['mad_post']
            tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']
            tbl['casaversion_7m12m'][matchrow] = fits.getheader(f7m12m)['ORIGIN']
            tbl['casaversion_cleanest'][matchrow] = fits.getheader(cleanest)['ORIGIN']

            print(fns)
            print(f"{field}_B{band}: matched {matchrow.sum()} rows")

            print()


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'contselMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

tbl.write('/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021/tables/metadata_7m12m_cleanest.ecsv',
          overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021/tables/metadata_7m12m_cleanest.html',
          formats=formats,
          format='ascii.html', overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021/tables/metadata_7m12m_cleanest.tex',
          formats=formats,
          overwrite=True)
tbl.write('/orange/adamginsburg/web/secure/ALMA-IMF/Feb2021/tables/metadata_7m12m_cleanest.js.html',
          #formats=formats,
          format='jsviewer')

os.chdir(cwd)
