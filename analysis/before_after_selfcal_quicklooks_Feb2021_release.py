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

cwd = os.getcwd()
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/February2021Release/'
os.chdir(basepath)
sharepath = '/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/February2021Release/'

#import imstats


# tbl = imstats.savestats(basepath=basepath)

#tbl = Table.read('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/February2021/tables/metadata.ecsv')
tbl = Table.read('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/February2021Release/tables/metadata_image.tt0.ecsv')
#tbl = Table.read('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/February2021Release/tables/metadata.ecsv')
tbl.add_column(Column(name='casaversion_pre', data=['                 ']*len(tbl)))
tbl.add_column(Column(name='casaversion_post', data=['                 ']*len(tbl)))
tbl.add_column(Column(name='pre_fn', data=[' '*200]*len(tbl)))
tbl.add_column(Column(name='post_fn', data=[' '*200]*len(tbl)))
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
tbl.add_column(Column(name='mad_sample_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_sample_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='std_sample_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='std_sample_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

pl.close('all')

for field in "W51-E W51-IRS2 G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W43-MM2 G333.60 G338.93 G353.41".split():
    for band in (3,6):
        for imtype in ('cleanest', 'bsens', ):#'7m12m', ):
            for suffix in ('image.tt0.fits', 'image.tt0.pbcor.fits'):

                # for not all-in-the-same-place stuff
                fns = [x for x in glob.glob(f"{field}/B{band}/{imtype}/{field}*_B{band}_*selfcal[0-9]*.{suffix}")
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

                    fig = pl.figure(1, figsize=(14,6))
                    if fig.get_figheight() != 6:
                        fig.set_figheight(6)
                    if fig.get_figwidth() != 14:
                        fig.set_figwidth(14)

                    bsens = '_bsens' if 'bsens' in postselfcal_name else ''


                    try:
                        with warnings.catch_warnings():
                            warnings.filterwarnings('ignore')
                            ax1, ax2, ax3, fig, diffstats = make_comparison_image(preselfcal_name,
                                                                                  postselfcal_name,
                                                                                  title1='Preselfcal',
                                                                                  title2='Postselfcal',
                                                                                  writediff=True)
                        if not os.path.exists(f"{basepath}/{field}/B{band}/comparisons/"):
                            os.mkdir(f"{basepath}/{field}/B{band}/comparisons/")
                        if not os.path.exists(f"{sharepath}/comparison_images/"):
                            os.mkdir(f"{sharepath}/comparison_images/")
                        fig.savefig(f"{basepath}/{field}/B{band}/comparisons/{field}_B{band}_{config}{bsens}_selfcal{last_selfcal}_comparison.png", bbox_inches='tight')
                        shutil.copy(f"{basepath}/{field}/B{band}/comparisons/{field}_B{band}_{config}{bsens}_selfcal{last_selfcal}_comparison.png",
                                    f"{sharepath}/comparison_images/")
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
                    tbl['pre_fn'][matchrow] = os.path.basename(preselfcal_name)
                    tbl['post_fn'][matchrow] = os.path.basename(postselfcal_name)
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
                    tbl['mad_sample_pre'][matchrow] = diffstats['mad_sample_pre']
                    tbl['mad_sample_post'][matchrow] = diffstats['mad_sample_post']
                    tbl['std_sample_pre'][matchrow] = diffstats['std_sample_pre']
                    tbl['std_sample_post'][matchrow] = diffstats['std_sample_post']
                    tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']
                    tbl['casaversion_pre'][matchrow] = fits.getheader(preselfcal_name)['ORIGIN']
                    tbl['casaversion_post'][matchrow] = fits.getheader(postselfcal_name)['ORIGIN']

                    print(fns)
                    print(f"{field}_B{band}:{last_selfcal}: matched {matchrow.sum()} rows")
                else:
                    print(f"No hits for {field}_B{band}_{config} imtype={imtype}")

                print()


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'scMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

if not os.path.exists(f'{sharepath}/tables/'):
    os.mkdir(sharepath)
    os.mkdir(f'{sharepath}/tables/')

for bp in ('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/',
           '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/'):

    tbl.write('{bp}/February2021Release/tables/metadata_sc.ecsv'.format(bp=bp),
              overwrite=True)
    tbl.write('{bp}/February2021Release/tables/metadata_sc.html'.format(bp=bp),
              formats=formats,
              format='ascii.html', overwrite=True)
    tbl.write('{bp}/February2021Release/tables/metadata_sc.tex'.format(bp=bp),
              formats=formats,
              overwrite=True)
    tbl.write('{bp}/February2021Release/tables/metadata_sc.js.html'.format(bp=bp),
              #formats=formats,
              format='jsviewer')

os.chdir(cwd)
