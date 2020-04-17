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
    data_pre = cube_pre[0].value[slices_post[1:]]
    data_post = cube_post[0].value[slices_post[1:]]

    try:
        diff = (data_post - data_pre)
    except Exception as ex:
        log.error(preselfcal, postselfcal, cube_pre.shape, cube_post.shape)
        raise ex

    fits.PrimaryHDU(data=diff,
                    header=cube_post.header).writeto(postselfcal+".preselfcal-diff.fits",
                                                     overwrite=True)

    fig = pl.figure(1, figsize=(14,6))
    fig.clf()

    minv = np.nanpercentile(data_pre, 0.05)
    maxv = np.nanpercentile(data_pre, 99.5)

    norm = visualization.simple_norm(data=diff.squeeze(), stretch='asinh',
                                     #min_percent=0.05, max_percent=99.995,)
                                     min_cut=minv, max_cut=maxv)
    if norm.vmax < 0.001:
        norm.vmax = 0.001


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
