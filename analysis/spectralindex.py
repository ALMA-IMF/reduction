import numpy as np
from astropy import units as u
import radio_beam
from astropy import stats
from spectral_cube import SpectralCube
import pylab as pl
import spectral_cube

import warnings
warnings.filterwarnings('ignore', category=spectral_cube.utils.StokesWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=pl.matplotlib.cbook.MatplotlibDeprecationWarning)
np.seterr('ignore')

cutoutregions = {
    "G008": ("fk5; box(271.579, -21.6255, 30\",30\")",),
    "G10": (
        "fk5; box(272.620167, -19.93008, 30\",30\")",
    ),
    "G12": (
        "fk5; box(273.5575, -17.92900, 70\", 70\")",
    ),
    "G328": (
        "fk5; box(239.499, -53.9668, 15\", 15\")",
    ),
    "G327": (
        "fk5; box(15:53:07,-54:37:10,25\",25\")",
    ),
    "G333": (
        "fk5; box(245.539, -50.1002, 60\",60\")",
    ),
    "G337": (
        "fk5; box(250.294, -47.135, 20\", 20\")",
    ),
    "G338": (
        "fk5; box(250.142, -45.694, 20\", 20\")",
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
        "fk5; box(19:23:39.975,+14:31:08.2,12\",12\")",
    ),
    "W51E": (
        "fk5; box(19:23:43.93,+14:30:34.8,5\",5\")",
        "fk5; box(19:23:43.90,+14:30:26.0,7\",7\")",
        "fk5; box(19:23:42.00,+14:30:36.0,15\",20\")",
    ),
}

def compare_spectral_indices(finaliter_prefix_b3, finaliter_prefix_b6, cutoutregion, fignum=1, stdthresh=2, scalebarlength=5):
    image_b3 = SpectralCube.read(f'{finaliter_prefix_b3}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    image_tt1_b3 = SpectralCube.read(f'{finaliter_prefix_b3}.image.tt1', format='casa_image').subcube_from_ds9region(cutoutregion)
    image_b6 = SpectralCube.read(f'{finaliter_prefix_b6}.image.tt0', format='casa_image').subcube_from_ds9region(cutoutregion)
    image_tt1_b6 = SpectralCube.read(f'{finaliter_prefix_b6}.image.tt1', format='casa_image').subcube_from_ds9region(cutoutregion)

    beams = radio_beam.Beams(major=u.Quantity([image_b3.beam.major, image_b6.beam.major]),
                             minor=u.Quantity([image_b3.beam.minor, image_b6.beam.minor]),
                             pa=u.Quantity([image_b3.beam.pa, image_b6.beam.pa]))
    commonbeam = radio_beam.commonbeam.commonbeam(beams)

    if image_b3.beam.sr < image_b6.beam.sr:
        header = image_b6[0].header
        ww = image_b6.wcs
    else:
        header = image_b3[0].header
        ww = image_b3.wcs

    image_b3_repr = image_b3.convolve_to(commonbeam)[0].reproject(header)
    image_tt1_b3_repr = image_tt1_b3.convolve_to(commonbeam)[0].reproject(header)
    image_b6_repr = image_b6.convolve_to(commonbeam)[0].reproject(header)
    image_tt1_b6_repr = image_tt1_b6.convolve_to(commonbeam)[0].reproject(header)

    alpha_b3 = image_tt1_b3_repr / image_b3_repr
    alpha_b6 = image_tt1_b6_repr / image_b6_repr

    b3_std = stats.mad_std(image_b3_repr.value, ignore_nan=True)
    b6_std = stats.mad_std(image_b6_repr.value, ignore_nan=True)

    mask = (image_b3_repr.value > stdthresh*b3_std) & (image_b6_repr.value > stdthresh*b6_std)
    alpha_b3_b6 = (np.log(image_b3_repr / image_b6_repr) / np.log(image_b3.wcs.wcs.crval[2] / image_b6.wcs.wcs.crval[2])).value
    alpha_b3_b6[~mask] = np.nan
    alpha_b3[~mask] = np.nan
    alpha_b6[~mask] = np.nan


    fig = pl.figure(num=fignum, figsize=(12,4))
    fig.clf()
    ax = pl.subplot(1,3,1,label='B3')
    ax.imshow(alpha_b3.value, vmax=4, vmin=-2)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title("B3")
    cb=pl.colorbar(mappable=pl.gca().images[0], cax=fig.add_axes([0.91,0.1,0.02,0.8]))
    cb.set_label(r"Spectral Index $\alpha$")

    ax = pl.subplot(1,3,2,label='B6')
    ax.imshow(alpha_b6.value, vmax=4, vmin=-2)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title("B6")
    cb=pl.colorbar(mappable=pl.gca().images[0], cax=fig.add_axes([0.91,0.1,0.02,0.8]))
    cb.set_label(r"Spectral Index $\alpha$")

    # scalebar
    cd = (ww.pixel_scale_matrix[1,1] * 3600)
    ax.plot([10*scalebarlength, 10*scalebarlength+scalebarlength/cd], [5,5], color='k')
    tx = ax.annotate(f'{scalebarlength}"', (10*scalebarlength+scalebarlength/2/cd, 9))
    tx.set_horizontalalignment('center')

    ax = pl.subplot(1,3,3,label='B3/B6')
    ax.imshow(alpha_b3_b6, vmax=4, vmin=-2)
    ax.set_xticks([])
    ax.set_yticks([])

    cb=pl.colorbar(mappable=pl.gca().images[0], cax=fig.add_axes([0.91,0.1,0.02,0.8]))
    cb.set_label(r"Spectral Index $\alpha$")
    ax.set_title("B6/B3")
    pl.subplots_adjust(wspace=0.05)

if __name__ == "__main__":
    import os
    try:
        os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults')
    except FileNotFoundError:
        os.chdir('/home/adam/Dropbox_UFL/ALMA-IMF/December2020Release/')

    pl.rcParams['font.size'] = 14
    pl.rcParams['image.origin'] = 'lower'
    pl.rcParams['image.interpolation'] = 'none'
    pl.rcParams['figure.facecolor'] = 'w'

    compare_spectral_indices(
        finaliter_prefix_b3="G328.25/B3/cleanest/G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
        finaliter_prefix_b6="G328.25/B6/cleanest/G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
        cutoutregion=cutoutregions['G328'][0])
    pl.savefig("../paper_figures/G328_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(finaliter_prefix_b6="G333.60/B6/cleanest/G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal5_finaliter",
                             finaliter_prefix_b3="G333.60/B3/cleanest/G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal5_finaliter",
                             cutoutregion=cutoutregions['G333'][0])
    pl.savefig("../paper_figures/G333_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G012.80/B3/cleanest/G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal5_finaliter",
        finaliter_prefix_b6="G012.80/B6/cleanest/G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['G12'][0])
    pl.savefig("../paper_figures/G12_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(finaliter_prefix_b3="W51-IRS2/B3/cleanest/W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
                             finaliter_prefix_b6="W51-IRS2/B6/cleanest/W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal8_finaliter",
                             cutoutregion=cutoutregions['W51IRS2'][0])
    pl.savefig("../paper_figures/W51IRS2_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G008.67/B3/cleanest/G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
        finaliter_prefix_b6="G008.67/B6/cleanest/G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['G008'][0])
    pl.savefig("../paper_figures/G008_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G327.29/B3/cleanest/G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
        finaliter_prefix_b6="G327.29/B6/cleanest/G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['G327'][0])
    pl.savefig("../paper_figures/G327_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G010.62/B3/cleanest/G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal7_finaliter",
        finaliter_prefix_b6="G010.62/B6/cleanest/G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['G10'][0])
    pl.savefig("../paper_figures/G10_B3B6_spectral_index.pdf", bbox_inches='tight')



    compare_spectral_indices(
        finaliter_prefix_b3="G337.92/B3/cleanest/G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
        finaliter_prefix_b6="G337.92/B6/cleanest/G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
        cutoutregion=cutoutregions['G337'][0])
    pl.savefig("../paper_figures/G337_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G338.93/B3/cleanest/G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
        finaliter_prefix_b6="G338.93/B6/cleanest/G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
        cutoutregion=cutoutregions['G338'][0])
    pl.savefig("../paper_figures/G338_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G351.77/B3/cleanest/G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
        finaliter_prefix_b6="G351.77/B6/cleanest/G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
        cutoutregion=cutoutregions['G351'][0])
    pl.savefig("../paper_figures/G351_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="G353.41/B3/cleanest/G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
        finaliter_prefix_b6="G353.41/B6/cleanest/G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
        cutoutregion=cutoutregions['G353'][0])
    pl.savefig("../paper_figures/G353_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="W43-MM3/B3/cleanest/W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
        finaliter_prefix_b6="W43-MM3/B6/cleanest/W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['W43MM3'][0])
    pl.savefig("../paper_figures/W43MM3_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="W43-MM2/B3/cleanest/W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
        finaliter_prefix_b6="W43-MM2/B6/cleanest/W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        cutoutregion=cutoutregions['W43MM2'][0])
    pl.savefig("../paper_figures/W43MM2_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="W51-E/B3/cleanest/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
        finaliter_prefix_b6="W51-E/B6/cleanest/W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
        cutoutregion=cutoutregions['W51E'][0],
        scalebarlength=1)
    pl.savefig("../paper_figures/W51Ee2_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="W51-E/B3/cleanest/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
        finaliter_prefix_b6="W51-E/B6/cleanest/W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
        cutoutregion=cutoutregions['W51E'][1],
        scalebarlength=1)
    pl.savefig("../paper_figures/W51Ee8_B3B6_spectral_index.pdf", bbox_inches='tight')

    compare_spectral_indices(
        finaliter_prefix_b3="W51-E/B3/cleanest/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
        finaliter_prefix_b6="W51-E/B6/cleanest/W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
        cutoutregion=cutoutregions['W51E'][2])
    pl.savefig("../paper_figures/W51EIRS1_B3B6_spectral_index.pdf", bbox_inches='tight')
