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

from before_after_selfcal_quicklooks import get_selfcal_number

cwd = os.getcwd()
basepath = '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020'
os.chdir(basepath)

import imstats


tbl = imstats.savestats(basepath=basepath)

#tbl = Table.read('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata.ecsv')
tbl.add_column(Column(name='casaversion_pre', data=['             ']*len(tbl)))
tbl.add_column(Column(name='casaversion_post', data=['             ']*len(tbl)))
tbl.add_column(Column(name='scMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='shape', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='ppbeam', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
#for field in ("G333.60",):
    for band in (3,6):
        for imtype in ('cleanest', 'bsens', '7m12m', ):

            # for not all-in-the-same-place stuff
            fns = [x for x in glob.glob(f"{field}/B{band}/{imtype}/{field}*_B{band}_*selfcal[0-9]*.image.tt0*.fits")
                   if 'robust0_' in x]

            config = '7M12M' if '7m' in imtype else '12M'


            if any(fns):
                selfcal_nums = [get_selfcal_number(fn) for fn in fns]

                last_selfcal = max(selfcal_nums)

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

                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore')
                        ax1, ax2, ax3, fig, diffstats =
                        make_comparison_image(preselfcal_name,
                                              postselfcal_name,
                                              title1='Preselfcal',
                                              title2='Postselfcal',
                                              writediff=True)
                    if not os.path.exists(f"{basepath}/{field}/B{band}/comparisons/"):
                        os.mkdir(f"{basepath}/{field}/B{band}/comparisons/")
                    pl.savefig(f"{basepath}/{field}/B{band}/comparisons/{field}_B{band}_{config}_selfcal{last_selfcal}_comparison.png", bbox_inches='tight')
                except IndexError:
                    raise
                except Exception as ex:
                    log.error(f"Failure for pre={preselfcal_name} post={postselfcal_name}")
                    log.error((field, band, config, imtype, ex))
                    continue

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
                tbl['min_pre'][matchrow] = diffstats['min_pre']
                tbl['min_post'][matchrow] = diffstats['min_post']
                tbl['max_pre'][matchrow] = diffstats['max_pre']
                tbl['max_post'][matchrow] = diffstats['max_post']
                tbl['sum_pre'][matchrow] = diffstats['sum_pre']
                tbl['sum_post'][matchrow] = diffstats['sum_post']
                tbl['shape'][matchrow] = diffstats['shape']
                tbl['ppbeam'][matchrow] = diffstats['ppbeam']
                tbl['mad_pre'][matchrow] = diffstats['mad_pre']
                tbl['mad_post'][matchrow] = diffstats['mad_post']
                tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']
                tbl['casaversion_pre'][matchrow] = fits.getheader(preselfcal_name)['ORIGIN']
                tbl['casaversion_post'][matchrow] = fits.getheader(postselfcal_name)['ORIGIN']

                print(fns)
                print(f"{field}_B{band}:{last_selfcal}: matched {matchrow.sum()} rows")
            else:
                print(f"No hits for {field}_B{band}_{config}")

            print()


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'scMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_sc.ecsv',
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_sc.html',
          formats=formats,
          format='ascii.html', overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_sc.tex',
          formats=formats,
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_sc.js.html',
          #formats=formats,
          format='jsviewer')

os.chdir(cwd)
