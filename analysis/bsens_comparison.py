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
basepath = '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020'
os.chdir(basepath)

import imstats


tbl = imstats.savestats(basepath=basepath)

#tbl = Table.read('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata.ecsv')
tbl.add_column(Column(name='casaversion_bsens', data=['             ']*len(tbl)))
tbl.add_column(Column(name='casaversion_cleanest', data=['             ']*len(tbl)))
tbl.add_column(Column(name='contselMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='contselMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='contselMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='contselMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='contselMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='shape', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='ppbeam', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_bsens', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_bsens', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_bsens', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_bsens', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_bsens', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_cleanest', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in (3,6):
        for config in ("12M",): # "7M12M"):


            fns = glob.glob(f"{basepath}/{field}/B{band}/bsens/*_{config}_robust0_*final*.image.tt0.pbcor.fits")
            if len(fns) > 1:
                raise ValueError("Too many matches!")
            elif len(fns) == 0:
                log.error(f"No matches to field={field} band={band} config={config}")
                continue
                raise ValueError("No matches!")
            fn = fns[0]

            pl.clf()
            bsens = fn
            cleanest = fn.replace("_bsens","").replace("/bsens/","/cleanest/")
            #print(os.path.exists(bsens), os.path.exists(clean))
            #field = fn.split("_uid")[0].split("/")[-1]

            filepath = fn.split("bsens")[0]

            bsens_fh = fits.open(bsens)
            try:
                clean_fh = fits.open(cleanest)
            except Exception as ex:
                log.error(f"Failed to open 'cleanest' image {cleanest}")
                print(ex)
                continue

            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    ax1, ax2, ax3, fig, diffstats = make_comparison_image(bsens, cleanest,
                                                                          title1='cleanest',
                                                                          title2='bsens')
            except IndexError:
                raise
            except Exception as ex:
                log.error(f"Failure for bsens={bsens} cleanest={cleanest}")
                log.error((field, band, config, ex))
                raise
                continue

            if not os.path.exists(f"{basepath}/{field}/B{band}/comparisons/"):
                os.mkdir(f"{basepath}/{field}/B{band}/comparisons/")
            pl.savefig(f"{basepath}/{field}/B{band}/comparisons/{field}_B{band}_{config}_bsens_vs_cleanest_comparison.png",
                       bbox_inches='tight', dpi=200)

            matchrow = ((tbl['region'] == field) &
                        (tbl['band'] == f'B{band}') &
                        (tbl['array'] == ('12Monly' if config == '12M' else config)) &
                        (tbl['robust'] == 'r0.0')
                       )
            tbl['contselMaxDiff'][matchrow] = diffstats['max']
            tbl['contselMinDiff'][matchrow] = diffstats['min']
            tbl['contselMADDiff'][matchrow] = diffstats['mad']
            tbl['contselMeanDiff'][matchrow] = diffstats['mean']
            tbl['contselMedianDiff'][matchrow] = diffstats['median']
            tbl['dr_bsens'][matchrow] = diffstats['dr_pre']
            tbl['dr_cleanest'][matchrow] = diffstats['dr_post']
            tbl['min_bsens'][matchrow] = diffstats['min_pre']
            tbl['min_cleanest'][matchrow] = diffstats['min_post']
            tbl['max_bsens'][matchrow] = diffstats['max_pre']
            tbl['max_cleanest'][matchrow] = diffstats['max_post']
            tbl['sum_bsens'][matchrow] = diffstats['sum_pre']
            tbl['sum_cleanest'][matchrow] = diffstats['sum_post']
            tbl['shape'][matchrow] = diffstats['shape']
            tbl['ppbeam'][matchrow] = diffstats['ppbeam']
            tbl['mad_bsens'][matchrow] = diffstats['mad_pre']
            tbl['mad_cleanest'][matchrow] = diffstats['mad_post']
            tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']
            tbl['casaversion_bsens'][matchrow] = fits.getheader(bsens)['ORIGIN']
            tbl['casaversion_cleanest'][matchrow] = fits.getheader(cleanest)['ORIGIN']

            print(fns)
            print(f"{field}_B{band}: matched {matchrow.sum()} rows")

            print()


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'contselMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_bsens_cleanest.ecsv',
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_bsens_cleanest.html',
          formats=formats,
          format='ascii.html', overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_bsens_cleanest.tex',
          formats=formats,
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_bsens_cleanest.js.html',
          #formats=formats,
          format='jsviewer')

os.chdir(cwd)
