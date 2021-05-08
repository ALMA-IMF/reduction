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

from spectralindex import prefixes

import warnings
warnings.filterwarnings('ignore', category=spectral_cube.utils.StokesWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=pl.matplotlib.cbook.MatplotlibDeprecationWarning)
np.seterr('ignore')

def bsens_cleanest_diff(finaliter_prefix_b3, finaliter_prefix_b6,
                        cutoutregion, fignum=1,
                        finaliter_prefix_b3_bsens=None,
                        finaliter_prefix_b6_bsens=None,
                        normpars_b3=None,
                        normpars_b6=None,
                        noco="",
                        non2hp="",
                        basepath='/home/adam/work/alma-imf/reduction/', ):
    image_b3 = SpectralCube.read(f'{finaliter_prefix_b3}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    if finaliter_prefix_b3_bsens is None:
        finaliter_prefix_b3_bsens = finaliter_prefix_b3.replace("cleanest","bsens").replace("merged_12M", f"merged_bsens{non2hp}_12M")
    bsens_b3 = SpectralCube.read(f'{finaliter_prefix_b3_bsens}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    image_b6 = SpectralCube.read(f'{finaliter_prefix_b6}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    if finaliter_prefix_b6_bsens is None:
        finaliter_prefix_b6_bsens = finaliter_prefix_b6.replace("cleanest","bsens").replace("merged_12M", f"merged_bsens{noco}_12M")
    bsens_b6 = SpectralCube.read(f'{finaliter_prefix_b6_bsens}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)

    # image_b3 = image_b3 * u.beam / image_b3.beam.sr
    # image_b6 = image_b6 * u.beam / image_b6.beam.sr
    # bsens_b3 = bsens_b3 * u.beam / bsens_b3.beam.sr
    # bsens_b6 = bsens_b6 * u.beam / bsens_b6.beam.sr

    fieldname = os.path.basename(finaliter_prefix_b6).split("_")[0]
    print(fieldname)

    diff_b3 = bsens_b3 - image_b3
    diff_b6 = bsens_b6 - image_b6

    normpars_b3_default = dict(min_percent=0.1, max_percent=99.9, stretch='linear')
    normpars_b6_default = dict(min_percent=0.1, max_percent=99.9, stretch='linear')

    if normpars_b3 is not None:
        normpars_b3_default.update(normpars_b3)
    normpars_b3 = normpars_b3_default

    if normpars_b6 is not None:
        normpars_b6_default.update(normpars_b6)
    normpars_b6 = normpars_b6_default


    fig = pl.figure(num=fignum, figsize=(6,6))
    fig.clf()
    ax = pl.subplot(1,1,1,label='B3', projection=diff_b3[0].wcs)
    im = ax.imshow(diff_b3.to(u.mJy)[0].value, norm=simple_norm(diff_b3.to(u.mJy)[0].value, **normpars_b3), cmap='gray')
    ax.set_xlabel('Right Ascension')
    ax.set_ylabel('Declination')
    cb = pl.colorbar(mappable=im)
    cb.set_label("$S_\\nu$ [mJy beam$^{-1}$]")

    fig2 = pl.figure(num=fignum+1, figsize=(6,6))
    ax2 = pl.subplot(1,1,1,label='B6', projection=diff_b6[0].wcs)
    im = ax2.imshow(diff_b6.to(u.mJy)[0].value, norm=simple_norm(diff_b6.to(u.mJy)[0].value, **normpars_b6), cmap='gray')
    ax2.set_xlabel('Right Ascension')
    ax2.set_ylabel('Declination')
    cb = pl.colorbar(mappable=im)
    cb.set_label("$S_\\nu$ [mJy beam$^{-1}$]")

    # ax2.set_yticklabels([])
    # ax2.set_ylabel("")
    # lat = ax2.coords['dec']
    # lat.set_ticklabel_position('r')
    # lat.set_axislabel_position('r')
    # lat.set_axislabel('Declination')

    return fig,fig2


normpars = {'W51IRS2': {
    'normpars_b3': {'max_percent': None, "min_percent": None, "min_cut":-0.5, "max_cut":0.5, 'stretch':'linear'},
    'normpars_b6': {'max_percent':99.99, "min_percent": 1, 'stretch':'linear'}
},
    'W43MM2': {'normpars_b6': {'max_percent': 99.5}},
    "G333": {'normpars_b6': {'max_percent': None, "min_percent": None, "min_cut":-7, "max_cut":7, 'stretch':'linear'},},
}
cutoutregions = {
    "G008": ("fk5; box(271.579, -21.6255, 30\",30\")",),
    "G10": (
        "fk5; box(272.620167, -19.93008, 30\",30\")",
    ),
    "G12": (
        "fk5; box(273.5575, -17.92900, 70\", 70\")",
    ),
    "G328": (
        "fk5; box(239.499, -53.9668, 30\", 30\")",
    ),
    "G327": (
        "fk5; box(15:53:07,-54:37:10, 45\",45\")",
    ),
    "G333": (
        "fk5; box(245.539, -50.1002, 60\",60\")",
    ),
    "G337": (
        "fk5; box(250.294, -47.135, 20\", 20\")",
    ),
    "G338": (
        "fk5; box(250.142, -45.694, 30\", 30\")",
    ),
    "G351": (
        "fk5; box(261.6787, -36.1545, 30\", 30\")",
    ),
    "G353": (
        "fk5; box(262.6120, -34.696, 60\", 60\")",
    ),
    "W43MM3": (
        "fk5; box(281.9241, -2.007, 20\", 20\")",
    ),
    "W43MM2": (
        "fk5; box(281.9025, -2.0152, 25\", 25\")",
    ),
    "W51IRS2": (
        'fk5; box(19:23:39.9340,+14:31:09.099,11.912",11.502",6.5033172e-06)',
        "fk5; box(19:23:39.975,+14:31:08.2,25\",25\")",
    ),
    "W51-E": (
        "fk5; box(19:23:43.90,+14:30:30.0,20\",20\")",
    ),
}

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

    # why did I add this override?  It's wrong (I had 4 instead of 6)
    #prefixes['G338']['finaliter_prefix_b6_bsens'] = 'G338.93/B6/bsens/G338.93_B6_uid___A001_X1296_X14f_continuum_merged_bsens_12M_robust0_selfcal6_finaliter'

    for fieldid, pfxs in prefixes.items():
        fig1,fig2 = bsens_cleanest_diff(**pfxs, cutoutregion=cutoutregions[fieldid][0], **normpars.get(fieldid, {}))
        fig1.savefig(f'bsens_diff_zooms/{fieldid}_bsens_diff_zoom_B3.png', bbox_inches='tight', dpi=300)
        fig2.savefig(f'bsens_diff_zooms/{fieldid}_bsens_diff_zoom_B6.png', bbox_inches='tight', dpi=300)

        fig1,fig2 = bsens_cleanest_diff(**pfxs, cutoutregion=cutoutregions[fieldid][0], **normpars.get(fieldid, {}),
                                        noco='_noco', non2hp='_non2hp')
        fig1.savefig(f'bsens_diff_zooms/{fieldid}_bsens_non2hp_diff_zoom_B3.png', bbox_inches='tight', dpi=300)
        fig2.savefig(f'bsens_diff_zooms/{fieldid}_bsens_noco_diff_zoom_B6.png', bbox_inches='tight', dpi=300)