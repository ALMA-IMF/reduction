"""
Compare May 2021 (post-Luke's reprocessing) to February 2021 (pre-Luke's reprocessing)
"""
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
import shutil

from compare_images import make_comparison_image

from before_after_selfcal_quicklooks import get_selfcal_number

import sys
sys.path.append(f'{os.path.dirname(__file__)}/../reduction')
import imaging_parameters

cwd = os.getcwd()
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/'
febpath = '/orange/adamginsburg/web/secure/ALMA-IMF/February2021Release'
maypath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/May2021Release'
figpath = '/orange/adamginsburg/web/secure/ALMA-IMF/Compare_February2021_to_May2021'
os.chdir(basepath)

#import imstats


# tbl = imstats.savestats(basepath=basepath)

#tbl = Table.read('/orange/adamginsburg/web/secure/ALMA-IMF/May2021/tables/metadata.ecsv')
tbl = Table.read('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/May2021Release/tables/metadata_image.tt0.ecsv')
#tbl = Table.read('/orange/adamginsburg/web/secure/ALMA-IMF/May2021Release/tables/metadata.ecsv')
tbl.add_column(Column(name='casaversion_feb', data=['                 ']*len(tbl)))
tbl.add_column(Column(name='casaversion_may', data=['                 ']*len(tbl)))
tbl.add_column(Column(name='has_amp', data=[False]*len(tbl)))
tbl.add_column(Column(name='has_amp_impars', data=[False]*len(tbl)))
tbl.add_column(Column(name='feb_fn', data=[' '*200]*len(tbl)))
tbl.add_column(Column(name='may_fn', data=[' '*200]*len(tbl)))
tbl.add_column(Column(name='scMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='shape', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='ppbeam', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='min_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='sum_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_sample_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_sample_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='std_sample_feb', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='std_sample_may', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_change', data=[np.nan]*len(tbl)))

pl.close('all')

for field in "W51-E W51-IRS2 G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W43-MM2 G333.60 G338.93 G353.41".split():
    for band in (3,6):
        for imtype in ('cleanest', 'bsens', ):#'7m12m', ):
            for suffix in ('image.tt0.fits', 'image.tt0.pbcor.fits'):

                # for not all-in-the-same-place stuff
                fns = [x for x in glob.glob(f"{maypath}/{field}/B{band}/{imtype}/{field}*_B{band}_*selfcal[0-9]*.{suffix}")
                       if 'robust0_' in x]

                config = '7M12M' if '7m' in imtype else '12M'


                if any(fns):
                    print("Found hits for ",field, band, imtype, suffix)
                    selfcal_nums = [get_selfcal_number(fn) for fn in fns]

                    last_selfcal = max(selfcal_nums)

                    postselfcal_name = [x for x in fns if f'selfcal{last_selfcal}' in x if 'diff' not in x][0]

                    preselfcal_name = postselfcal_name.replace(f"_selfcal{last_selfcal}","_preselfcal_finalmodel")
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

                    feb_postselfcal = [x for x in glob.glob(f"{febpath}/{field}/B{band}/{imtype}/{preselfcal_name}")[0]
                                        if 'robust0_' in x]
                    feb_preselfcal = [x for x in glob.glob(f"{febpath}/{field}/B{band}/{imtype}/{preselfcal_name}")[0]
                                        if 'robust0_' in x]

                    fig = pl.figure(1, figsize=(14,6))
                    if fig.get_figheight() != 6:
                        fig.set_figheight(6)
                    if fig.get_figwidth() != 14:
                        fig.set_figwidth(14)

                    bsens = '_bsens' if 'bsens' in postselfcal_name else ''


                    try:
                        with warnings.catch_warnings():
                            warnings.filterwarnings('ignore')
                            ax1, ax2, ax3, fig, diffstats = make_comparison_image(feb_postselfcal,
                                                                                  may_postselfcal,
                                                                                  title1='February2021',
                                                                                  title2='May2021',
                                                                                  writediff=False)
                        fig.savefig(f"{figpath}/{field}_B{band}_{config}{bsens}_selfcal{last_selfcal}_MayVsFeb2021_comparison.png", bbox_inches='tight')
                    except IndexError:
                        raise
                    except Exception as ex:
                        log.error(f"Failure for pre={preselfcal_name} post={postselfcal_name}")
                        log.error((field, band, config, imtype, ex))
                        raise ex
                        #continue

                    matchrow = ((tbl['region'] == field) &
                                (tbl['band'] == f'B{band}') &
                                (tbl['array'] == ('12Monly' if config == '12M' else config)) &
                                (tbl['robust'] == 'r0.0') &
                                (tbl['bsens'] if 'bsens' in imtype else ~tbl['bsens']) &
                                (tbl['pbcor'] if 'pbcor' in suffix else ~tbl['pbcor'])
                               )
                    if matchrow.sum() == 0:
                        raise ValueError(f"No matches for field={field} band={band} config={config} imtype={imtype} suffix={suffix}")
                    tbl['scMaxDiff'][matchrow] = diffstats['max']
                    tbl['scMinDiff'][matchrow] = diffstats['min']
                    tbl['scMADDiff'][matchrow] = diffstats['mad']
                    tbl['scMeanDiff'][matchrow] = diffstats['mean']
                    tbl['scMedianDiff'][matchrow] = diffstats['median']
                    tbl['feb_fn'][matchrow] = os.path.basename(preselfcal_name)
                    tbl['may_fn'][matchrow] = os.path.basename(postselfcal_name)
                    tbl['dr_feb'][matchrow] = diffstats['dr_pre']
                    tbl['dr_may'][matchrow] = diffstats['dr_post']
                    tbl['min_feb'][matchrow] = diffstats['min_pre']
                    tbl['min_may'][matchrow] = diffstats['min_post']
                    tbl['max_feb'][matchrow] = diffstats['max_pre']
                    tbl['max_may'][matchrow] = diffstats['max_post']
                    tbl['sum_feb'][matchrow] = diffstats['sum_pre']
                    tbl['sum_may'][matchrow] = diffstats['sum_post']
                    tbl['shape'][matchrow] = diffstats['shape']
                    tbl['ppbeam'][matchrow] = diffstats['ppbeam']
                    tbl['mad_feb'][matchrow] = diffstats['mad_pre']
                    tbl['mad_may'][matchrow] = diffstats['mad_post']
                    tbl['mad_sample_feb'][matchrow] = diffstats['mad_sample_pre']
                    tbl['mad_sample_may'][matchrow] = diffstats['mad_sample_post']
                    tbl['std_sample_feb'][matchrow] = diffstats['std_sample_pre']
                    tbl['std_sample_may'][matchrow] = diffstats['std_sample_post']
                    tbl['dr_change'][matchrow] = diffstats['dr_may']/diffstats['dr_feb']
                    tbl['casaversion_feb'][matchrow] = fits.getheader(preselfcal_name)['ORIGIN']
                    tbl['casaversion_may'][matchrow] = fits.getheader(postselfcal_name)['ORIGIN']

                    scpars = imaging_parameters.selfcal_pars[f'{field}_B{band}_{config}_robust0']
                    tbl['has_amp_impars'][matchrow] = any('a' in scpars[key]['calmode'] for key in scpars)
                    tbl['has_amp'][matchrow] = diffstats['has_amp']

                    print(fns)
                    print(f"{field}_B{band}:{last_selfcal}: matched {matchrow.sum()} rows")
                else:
                    print(f"No hits for {field}_B{band}_{config} imtype={imtype}")

                print()


formats = {'dr_change': lambda x: '{0:0.2f}'.format(x),
           'scMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }


tbl.write(f'{figpath}/may_feb_2021_comparison.ecsv',
            overwrite=True)
tbl.write(f'{figpath}/may_feb_2021_comparison.html',
            formats=formats,
            format='ascii.html', overwrite=True)
tbl.write(f'{figpath}/may_feb_2021_comparison.tex',
            formats=formats,
            overwrite=True)
tbl.write(f'{figpath}/may_feb_2021_comparison.js.html',
            #formats=formats,
            format='jsviewer')

os.chdir(cwd)

