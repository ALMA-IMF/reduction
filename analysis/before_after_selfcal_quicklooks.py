import numpy as np
import warnings
import glob
import os
from astropy.io import fits
from astropy import visualization
from astropy.table import Table, Column
from spectral_cube import SpectralCube
from astropy.stats import mad_std
import pylab as pl


def make_comparison_image(preselfcal, postselfcal):
    #fh_pre = fits.open(preselfcal)
    #fh_post = fits.open(postselfcal)
    if 'fits' in preselfcal:
        cube_pre = SpectralCube.read(preselfcal)
    else:
        cube_pre = SpectralCube.read(preselfcal, format='casa_image')
    if 'fits' in postselfcal:
        cube_post = SpectralCube.read(postselfcal)
    else:
        cube_post = SpectralCube.read(postselfcal, format='casa_image')
    cube_pre = cube_pre.with_mask(cube_pre != 0*cube_pre.unit)
    cube_post = cube_post.with_mask(cube_post != 0*cube_post.unit)
    # these break shapes!
    #cube_pre = cube_pre.minimal_subcube()
    #cube_post = cube_post.minimal_subcube()
    slices_post = cube_post.subcube_slices_from_mask(cube_post.mask & cube_pre.mask,
                                                     spatial_only=True)
    data_pre = cube_pre[0].value[slices_post]
    data_post = cube_post[0].value[slices_post]

    try:
        diff = (data_post - data_pre)
    except Exception as ex:
        print(preselfcal, postselfcal, cube_pre.shape, cube_post.shape)
        raise ex

    fits.PrimaryHDU(data=diff,
                    header=cube_post.header).writeto(postselfcal+".preselfcal-diff.fits",
                                                     overwrite=True)

    fig = pl.figure(1, figsize=(14,6))
    fig.clf()


    norm = visualization.simple_norm(data=diff.squeeze(),
                                     stretch='asinh',
                                     min_cut=-0.001,
                                     max_percent=99)
    if norm.vmax < 0.001:
        norm.vmax = 0.001
    if norm.vmax > 0.01:
        norm.vmax = 0.01

    ax1 = pl.subplot(1,3,1)
    ax2 = pl.subplot(1,3,2)
    ax3 = pl.subplot(1,3,3)
    ax1.imshow(data_pre, norm=norm, origin='lower', interpolation='none',
               cmap='gray')
    ax1.set_title("preselfcal")
    ax2.imshow(data_post, norm=norm, origin='lower', interpolation='none',
               cmap='gray')
    ax2.set_title("postselfcal")
    ax3.imshow(diff.squeeze(), norm=norm, origin='lower', interpolation='none',
               cmap='gray')
    ax3.set_title("post-pre")

    for ax in (ax1,ax2,ax3):
        ax.set_xticks([])
        ax.set_yticks([])

    pl.subplots_adjust(wspace=0.0)

    diffstats = {'mean': np.nanmean(diff),
                 'max': np.nanmax(diff),
                 'min': np.nanmin(diff),
                 'median': np.nanmedian(diff),
                 'mad': mad_std(diff, ignore_nan=True),
                 'dr_pre': np.nanmax(data_pre) / mad_std(data_pre, ignore_nan=True),
                 'dr_post': np.nanmax(data_post) / mad_std(data_post, ignore_nan=True),
                 'max_pre': np.nanmax(data_pre),
                 'max_post': np.nanmax(data_post),
                 'mad_pre': mad_std(data_pre, ignore_nan=True),
                 'mad_post':  mad_std(data_post, ignore_nan=True),
                }

    return ax1, ax2, ax3, fig, diffstats

def get_selfcal_number(fn):
    numberstring = fn.split("selfcal")[1][0]
    try:
        return int(numberstring)
    except:
        return 0

import imstats
tbl = imstats.savestats()

#tbl = Table.read('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.ecsv')
tbl.add_column(Column(name='scMaxDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMinDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMADDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMeanDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='scMedianDiff', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='max_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_pre', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='mad_post', data=[np.nan]*len(tbl)))
tbl.add_column(Column(name='dr_improvement', data=[np.nan]*len(tbl)))

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
#for field in ("G333.60",):
    for band in (3,6):
        for config in ('7M12M', '12M'):

            # for all-in-the-same-place stuff
            fns = [x for x in glob.glob(f"{field}*_B{band}_*_{config}_*selfcal[0-9]*.image.tt0")
                   if 'robust0' in x]
            # for not all-in-the-same-place stuff
            fns = [x for x in glob.glob(f"{field}/B{band}/{field}*_B{band}_*_{config}_*selfcal[0-9]*.image.tt0*.fits")
                   if 'robust0' in x]

            if any(fns):
                selfcal_nums = [get_selfcal_number(fn) for fn in fns]

                last_selfcal = max(selfcal_nums)

                postselfcal_name = [x for x in fns if f'selfcal{last_selfcal}' in x][0]

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
                        ax1, ax2, ax3, fig, diffstats = make_comparison_image(preselfcal_name, postselfcal_name)
                    if not os.path.exists(f"{field}/B{band}/comparisons/"):
                        os.mkdir(f"{field}/B{band}/comparisons/")
                    pl.savefig(f"{field}/B{band}/comparisons/{field}_B{band}_{config}_selfcal{last_selfcal}_comparison.png", bbox_inches='tight')
                except Exception as ex:
                    print(f"Failure for pre={preselfcal_name} post={postselfcal_name}")
                    print(field, band, config, ex)
                    continue

                matchrow = ((tbl['region'] == field) &
                            (tbl['band'] == f'B{band}') &
                            (tbl['array'] == '12Monly' if config == '12M' else config) &
                            (tbl['robust'] == 'r0.0')
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
                tbl['mad_pre'][matchrow] = diffstats['mad_pre']
                tbl['mad_post'][matchrow] = diffstats['mad_post']
                tbl['dr_improvement'][matchrow] = diffstats['dr_post']/diffstats['dr_pre']

                print(fns)
                print(f"{field}_B{band}:{last_selfcal}")
            else:
                print(f"No hits for {field}_B{band}_{config}")


formats = {'dr_improvement': lambda x: '{0:0.2f}'.format(x),
           'scMaxDiff': lambda x: f'{x:0.6g}',
           'BeamVsReq': lambda x: f'{x:0.2f}',
          }

tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata_sc.ecsv',
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata_sc.html',
          formats=formats,
          format='ascii.html', overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata_sc.tex',
          formats=formats,
          overwrite=True)
tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata_sc.js.html',
          #formats=formats,
          format='jsviewer')
