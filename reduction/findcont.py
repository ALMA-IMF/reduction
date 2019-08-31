from astropy.io import fits
from astropy import stats
from spectral_cube import SpectralCube, OneDSpectrum
from scipy.ndimage import find_objects
import pylab as pl

def find_and_plot_cont(basename, background='mean'):

    spec = OneDSpectrum.from_hdu(fits.open(basename+'.maxspec.fits'))
    clipped = stats.sigma_clip(spec.value, sigma=1.8, stdfunc=stats.mad_std)
    maxsel = clipped.mask

    spec = OneDSpectrum.from_hdu(fits.open(basename+'.medianspec.fits'))
    clipped = stats.sigma_clip(spec.value, sigma=1.8, stdfunc=stats.mad_std)
    medsel = clipped.mask

    spec = OneDSpectrum.from_hdu(fits.open(basename+'.meanspec.fits'))
    clipped = stats.sigma_clip(spec.value, sigma=1.8, stdfunc=stats.mad_std)
    meansel = clipped.mask

    spec = OneDSpectrum.from_hdu(fits.open(basename+'.{0}spec.fits'.format(background)))
    
    spec.quicklook()
    pl.plot(spec.spectral_axis, clipped, linewidth=4, alpha=0.75, zorder=10, color='r')
    clipped.mask = medsel
    pl.plot(spec.spectral_axis, clipped, linewidth=3.5, alpha=0.75, zorder=-1)
    clipped.mask = maxsel
    pl.plot(spec.spectral_axis, clipped, linewidth=3, alpha=0.75, zorder=11)

    return find_objects(meansel)
