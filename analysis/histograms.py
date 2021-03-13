import numpy as np
import time
from astropy import units as u
import radio_beam
import regions
from astropy import stats, convolution
from spectral_cube import SpectralCube
import pylab as pl
import spectral_cube

import warnings
warnings.filterwarnings('ignore', category=spectral_cube.utils.StokesWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=pl.matplotlib.cbook.MatplotlibDeprecationWarning)
np.seterr('ignore')


from spectralindex import prefixes


def flux_hist(finaliter_prefix_b3, finaliter_prefix_b6,
              basepath='/home/adam/work/alma-imf/reduction/', las=None):
    image_b3 = SpectralCube.read(f'{finaliter_prefix_b3}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube()
    image_b6 = SpectralCube.read(f'{finaliter_prefix_b6}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube()
    image_b3 = image_b3 * u.beam / image_b3.beam.sr
    image_b6 = image_b6 * u.beam / image_b6.beam.sr

    fieldname = os.path.basename(finaliter_prefix_b6).split("_")[0]

    if las:
        smb3 = image_b3[0].convolve_to(radio_beam.Beam(las), allow_huge=True)
        image_b3 = image_b3 - smb3
        smb6 = image_b6[0].convolve_to(radio_beam.Beam(las), allow_huge=True)
        image_b6 = image_b6 - smb6

    noise_region_b3 = regions.read_ds9(f"{basepath}/reduction/noise_estimation_regions/{fieldname}_B3_noise_sampling.reg")
    noise_region_b6 = regions.read_ds9(f"{basepath}/reduction/noise_estimation_regions/{fieldname}_B6_noise_sampling.reg")

    noiseim_b3 = image_b3.subcube_from_regions(noise_region_b3)[0]
    noiseim_b6 = image_b6.subcube_from_regions(noise_region_b6)[0]

    b3_std = stats.mad_std(noiseim_b3, ignore_nan=True)
    b6_std = stats.mad_std(noiseim_b6, ignore_nan=True)
    print(fieldname, b3_std, b6_std)

    fig = pl.figure(2, figsize=(12,7))
    fig.clf()
    ax = pl.subplot(1,2,1)
    b3data = image_b3[0].value
    bins_b3 = np.linspace(np.nanmin(b3data), np.nanmax(b3data), 100)
    bins_b3b = np.linspace(np.nanmin(b3data), np.nanmax(b3data), 10000)
    H,L,P = ax.hist(b3data[np.isfinite(b3data)], bins=bins_b3, density=False)
    #ax.hist(noiseim_b3.value.ravel(), bins=bins_b3)
    ax.set_yscale('log')
    ax.set_ylim(0.5, ax.get_ylim()[1])
    ax.plot(bins_b3b, H.max() * np.exp(-bins_b3b**2/(2*b3_std.value**2)), 'k')
    ax.set_xlabel("$S_{3mm}$ [Jy/sr]")
    ax.set_ylabel("Number of Pixels")

    axin = fig.add_axes([0.25, 0.6, 0.20, 0.25])
    bins = np.linspace(-5*b3_std.value, 5*b3_std.value, 100)
    H,L,P = axin.hist(b3data[(b3data < 5*b3_std.value) & (b3data > -5*b3_std.value)], bins=bins, density=False)
    #axin.hist(noiseim_b3.value.ravel(), bins=bins)
    gauss = H.max() * np.exp(-bins**2/(2*b3_std.value**2))
    axin.plot(bins, gauss, 'k')
    axin.set_xticklabels([])
    axin.set_yticks(axin.get_yticks()[1:])
    axin2 = fig.add_axes([0.25, 0.5, 0.2, 0.1])
    loc = (L[1:] + L[:-1])/2
    axin2.plot(loc, H-H.max() * np.exp(-loc**2/(2*b3_std.value**2)), drawstyle='steps', color='k')
    axin2.set_xlim(axin.get_xlim())

    ax = pl.subplot(1,2,2)
    b6data = image_b6[0].value
    bins_b6 = np.linspace(np.nanmin(b6data), np.nanmax(b6data), 100)
    bins_b6b = np.linspace(np.nanmin(b6data), np.nanmax(b6data), 10000)
    H,L,P = ax.hist(b6data[np.isfinite(b6data)], bins=bins_b6, density=False)
    ax.plot(bins_b6b, H.max() * np.exp(-bins_b6b**2/(2*b6_std.value**2)), 'k')
    #ax.hist(noiseim_b6.value.ravel(), bins=bins_b6)
    ax.set_ylim(0.5, ax.get_ylim()[1])
    ax.set_yscale('log')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set_xlabel("$S_{1mm}$ [Jy/sr]")
    ax.set_ylabel("Number of Pixels")

    axin = fig.add_axes([0.65, 0.6, 0.20, 0.25])
    bins = np.linspace(-5*b6_std.value, 5*b6_std.value, 100)
    H,L,P = axin.hist(b6data[(b6data < 5*b6_std.value) & (b6data > -5*b6_std.value)], bins=bins, density=False)
    #axin.hist(noiseim_b6.value.ravel(), bins=bins)
    axin.plot(bins, H.max() * np.exp(-bins**2/(2*b6_std.value**2)), 'k')
    axin.set_xticklabels([])
    axin.set_yticks(axin.get_yticks()[1:])
    axin2 = fig.add_axes([0.65, 0.5, 0.2, 0.1])
    loc = (L[1:] + L[:-1])/2
    axin2.plot(loc, H-H.max() * np.exp(-loc**2/(2*b6_std.value**2)), drawstyle='steps', color='k')
    axin2.set_xlim(axin.get_xlim())




if __name__ == "__main__":
    import os
    try:
        basepath = '/orange/adamginsburg/ALMA_IMF/reduction/'
        os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults')
    except FileNotFoundError:
        basepath = '/home/adam/work/alma-imf/reduction/'
        os.chdir('/home/adam/Dropbox_UFL/ALMA-IMF/December2020Release/')

    pl.rcParams['font.size'] = 14
    pl.rcParams['image.origin'] = 'lower'
    pl.rcParams['image.interpolation'] = 'none'
    pl.rcParams['figure.facecolor'] = 'w'

    data = {}
    for fieldid, pfxs in prefixes.items():
        flux_hist(basepath=basepath, **pfxs)
        pl.savefig(f"../paper_figures/flux_histograms/{fieldid}_B3B6_flux_histogram.pdf", bbox_inches='tight')

    """
    pl.figure(3, figsize=(16,10)).clf()
    xs = np.arange(-3,6)
    for ii,fieldid in enumerate(sorted(data)):
        mask, alph = data[fieldid]
        ax = pl.subplot(3,5,ii+2)
        ax.hist(alph[mask], bins=xs, stacked=True, density=True, label=fieldid, histtype='step')
        ax.axvline(0, color='k', linestyle='--', zorder=-5)
        ax.axvline(2, color='k', linestyle='--', zorder=-5)
        ax.set_ylim(0,1.0)
        ax.set_xlim(-3,5)
        if ii >= 9:
            ax.set_xlabel("Spectral Index $\\alpha$")
            ax.set_xticks([-2,-1,0,1,2,3,4,5])
        else:
            ax.set_xticks([])
        if (ii+1) % 5 == 0:
            ax.set_ylabel("Fraction of Pixels")
        else:
            ax.set_yticks([])
        ax.set_title(fieldid)
    pl.savefig(f"../paper_figures/alpha_histograms/all_B3B6_alpha_histograms.pdf", bbox_inches='tight')

    pl.figure(4, figsize=(8,8)).clf()
    fracs = {key: ((data[key][1] > 2).sum()/np.isfinite(data[key][1]).sum(),
                   (data[key][1] < 2).sum()/np.isfinite(data[key][1]).sum(),
                   np.isfinite(data[key][1]).sum()/data[key][1].size
                  )
             for key in data}
    ff = [fracs[key][1] for key in fracs]
    dust = [fracs[key][0] for key in fracs]
    ttl = [fracs[key][2] for key in fracs]
    pl.scatter(ttl, dust)
    for key in fracs:
        tx = pl.annotate(key, (fracs[key][2], fracs[key][0]), fontsize=12)
        tx.set_horizontalalignment('center')
    pl.ylabel("Fraction of pixels with $\\alpha>2$")
    pl.xlabel("Fraction of pixels with $S_\\nu > 5 \sigma$")
    pl.savefig("../paper_figures/alpha_histograms/spindx_classification_summary.pdf")
    """
