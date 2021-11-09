'''
Script to calculate clean/dirty beam volume ratio in
ALMA-IMF continuum images.
'''

import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.colors as colors
from scipy import ndimage, signal

from casatasks import exportfits

from astropy.io import fits
from astropy import units as u
from astropy.convolution import convolve, convolve_fft
from radio_beam import Beam, Beams


########## DEFINED BY USER ########
data_path = '/home/roberto/ALMA_IMF/residuals_fix/continuum/'
plots_path = '/home/roberto/ALMA_IMF/residuals_fix/plots/'

max_npix_peak=100
###################################


data_path = os.path.join(data_path)
files=[f for f in glob.glob(data_path+'*') if not os.path.basename(f).endswith('.fits')]

for file in files:
    if not os.path.exists(file+'.fits'):
        print('Running exportfits on file '+file)
        exportfits(imagename=file, fitsimage=file+'.fits')
    else:
        print(file+'.fits'+' already exists. Not running exportfits.')

fits_files = glob.glob(data_path+'*.fits')

for file in fits_files:
    hdu = fits.open(file)
    data = hdu[0].data
    header = hdu[0].header

    bmaj_npix = header['BMAJ'] / header['CDELT2']
    bmin_npix = header['BMIN'] / header['CDELT2']
    clean_beam_sum = (np.pi/(4*np.log(2)))*bmaj_npix*bmin_npix

    hdu.close()

    center = np.unravel_index(np.argmax(data[0,0,:,:]), data[0,0,:,:].shape)
    cy, cx = center

    cutout = data[0,0,cy-max_npix_peak:cy+max_npix_peak+1, cx-max_npix_peak:cx+max_npix_peak+1]
    shape = cutout.shape
    sy, sx = shape
    Y, X = np.mgrid[0:sy, 0:sx]

    center = np.unravel_index(np.argmax(cutout), cutout.shape)
    cy, cx = center

    dy = (Y - cy)
    dx = (X - cx)
    costh = np.cos(header['BPA']*(np.pi/180))
    sinth = np.sin(header['BPA']*(np.pi/180))
    rmajmin =  header['BMIN'] / header['BMAJ']

    rr = ((dx * costh + dy * sinth)**2 / rmajmin**2 +
          (dx * sinth - dy * costh)**2 / 1**2)**0.5
    rbin = (rr).astype(int)

    #radial_mean = ndimage.mean(cutout**2, labels=rbin, index=np.arange(max_npix_peak))
    radial_mean = ndimage.mean(np.abs(cutout), labels=rbin, index=np.arange(max_npix_peak))
    first_min_ind = signal.find_peaks(-radial_mean)[0][0]

    cutout_posit = np.where(cutout > 0, cutout, 0.)
    radial_sum = ndimage.sum(cutout_posit, labels=rbin, index=np.arange(first_min_ind))
    psf_sum = np.sum(radial_sum)

    scale_factor = clean_beam_sum/psf_sum

    print('For file {} :'.format(os.path.split(file)[-1]))
    print('epsilon = Vol_clean_beam / Vol_dirty_beam = {:.4f}'.format(scale_factor))
