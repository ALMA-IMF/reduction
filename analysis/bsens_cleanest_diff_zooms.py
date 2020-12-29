import requests
import re
import numpy as np
from astropy import table
import io
import time
from astropy import units as u
import radio_beam
import regions
from astropy.io import fits
from astropy.visualization import simple_norm
from astropy import stats, convolution, wcs, coordinates
from spectral_cube import SpectralCube
import pylab as pl
import spectral_cube

from spectralindex import prefixes, cutoutregions

import warnings
warnings.filterwarnings('ignore', category=spectral_cube.utils.StokesWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=pl.matplotlib.cbook.MatplotlibDeprecationWarning)
np.seterr('ignore')

def bsens_cleanest_diff(finaliter_prefix_b3, finaliter_prefix_b6,
                        cutoutregion, fignum=1,
                        finaliter_prefix_b3_bsens=None,
                        finaliter_prefix_b6_bsens=None,
                        basepath='/home/adam/work/alma-imf/reduction/', ):
    image_b3 = SpectralCube.read(f'{finaliter_prefix_b3}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    if finaliter_prefix_b3_bsens is None:
        finaliter_prefix_b3_bsens = finaliter_prefix_b3.replace("cleanest","bsens").replace("merged_12M","merged_bsens_12M")
    bsens_b3 = SpectralCube.read(f'{finaliter_prefix_b3_bsens}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    image_b6 = SpectralCube.read(f'{finaliter_prefix_b6}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    if finaliter_prefix_b6_bsens is None:
        finaliter_prefix_b6_bsens = finaliter_prefix_b6.replace("cleanest","bsens").replace("merged_12M","merged_bsens_12M")
    bsens_b6 = SpectralCube.read(f'{finaliter_prefix_b6_bsens}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)

    image_b3 = image_b3 * u.beam / image_b3.beam.sr
    image_b6 = image_b6 * u.beam / image_b6.beam.sr
    bsens_b3 = bsens_b3 * u.beam / bsens_b3.beam.sr
    bsens_b6 = bsens_b6 * u.beam / bsens_b6.beam.sr

    #fieldname = os.path.basename(finaliter_prefix_b6).split("_")[0]

    diff_b3 = bsens_b3 - image_b3
    diff_b6 = bsens_b6 - image_b6

    fig = pl.figure(num=fignum, figsize=(12,6))
    fig.clf()
    ax = pl.subplot(1,2,1,label='B3', projection=diff_b3[0].wcs)
    ax.imshow(diff_b3[0].value, norm=simple_norm(diff_b3[0].value, min_percent=0.1, max_percent=99.9, stretch='asinh'), cmap='gray')
    ax.set_xlabel('Galactic Longitude')
    ax.set_ylabel('Galactic Latitude')
    ax2 = pl.subplot(1,2,2,label='B6', projection=diff_b6[0].wcs)
    ax2.imshow(diff_b6[0].value, norm=simple_norm(diff_b6[0].value, min_percent=0.1, max_percent=99.9, stretch='asinh'), cmap='gray')
    ax2.set_xlabel('Galactic Longitude')
    ax2.set_ylabel('Galactic Latitude')

    return fig


if __name__ == "__main__":
    import os
    try:
        os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults')
    except FileNotFoundError:
        os.chdir('/home/adam/Dropbox_UFL/ALMA-IMF/December2020Release/')

    if not os.path.exists('bsens_diff_zooms'):
        os.mkdir('bsens_diff_zooms')

    pl.rcParams['font.size'] = 14
    pl.rcParams['image.origin'] = 'lower'
    pl.rcParams['image.interpolation'] = 'none'
    pl.rcParams['figure.facecolor'] = 'w'
    prefixes['G338']['finaliter_prefix_b6_bsens'] = 'G338.93/B6/bsens/G338.93_B6_uid___A001_X1296_X14f_continuum_merged_bsens_12M_robust0_selfcal4_finaliter'

    for fieldid, pfxs in prefixes.items():
        fig = bsens_cleanest_diff(**pfxs, cutoutregion=cutoutregions[fieldid][0])
        fig.savefig(f'bsens_diff_zooms/{fieldid}_bsens_diff_zoom.png', bbox_inches='tight')
