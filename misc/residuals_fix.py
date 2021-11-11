'''
Script to fix residuals of ALMA-IMF line-cubes
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
data_path = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/'
plots_path = '/home/roberto/ALMA_IMF/residuals_fix/plots/'

#psf_file = 'G351.77_B3_spw0_7M12M_n2hp.psf.fits'
#orig_resid = 'G351.77_B3_spw0_7M12M_n2hp.residual.fits'
#model = 'G351.77_B3_spw0_7M12M_n2hp.model.fits'

max_npix_peak=100
plot_channel = 110
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

psf_file = [s for s in fits_files if ".psf.fits" in s][0]
orig_resid = [s for s in fits_files if ".residual.fits" in s][0]
model = [s for s in fits_files if ".model.fits" in s][0]

hdu = fits.open(psf_file)
data = hdu[0].data
header = hdu[0].header
beams = hdu[1]
beams_table =  beams.data
beams = Beams.from_fits_bintable(beams) #convert to radio_beam object
hdu.close()


center = np.unravel_index(np.argmax(data[0,plot_channel,:,:]), data[0,plot_channel,:,:].shape)
cy, cx = center

cutout = data[0,plot_channel,cy-max_npix_peak:cy+max_npix_peak+1, cx-max_npix_peak:cx+max_npix_peak+1]

shape = cutout.shape
sy, sx = shape
Y, X = np.mgrid[0:sy, 0:sx]

center = np.unravel_index(np.argmax(cutout), cutout.shape)
cy, cx = center

dy = (Y - cy)
dx = (X - cx)
costh = np.cos(beams_table[plot_channel][2]*(np.pi/180))
sinth = np.sin(beams_table[plot_channel][2]*(np.pi/180))
rmajmin = beams_table[plot_channel][1] / beams_table[plot_channel][0]

rr = ((dx * costh + dy * sinth)**2 / rmajmin**2 +
      (dx * sinth - dy * costh)**2 / 1**2)**0.5
rbin = (rr).astype(int)

#radial_mean = ndimage.mean(cutout**2, labels=rbin, index=np.arange(max_npix_peak))
radial_mean = ndimage.mean(np.abs(cutout), labels=rbin, index=np.arange(max_npix_peak))
first_min_ind = signal.find_peaks(-radial_mean)[0][0]

#cutout_posit = np.where(cutout > 0, cutout, 0.)
#radial_sum = ndimage.sum(cutout_posit, labels=rbin, index=np.arange(first_min_ind))
radial_sum = ndimage.sum(cutout, labels=rbin, index=np.arange(first_min_ind))
psf_sum = np.sum(radial_sum)

#Z = np.full(shape, 0)


bmaj_npix = beams_table[plot_channel][0] / (header['CDELT2']*3600.)
bmin_npix = beams_table[plot_channel][1] / (header['CDELT2']*3600.)
clean_beam_sum = (np.pi/(4*np.log(2)))*bmaj_npix*bmin_npix

scale_factor = clean_beam_sum/psf_sum
print('\nClean beam volume is {} pixels'.format(clean_beam_sum))
print('Dirty beam volume to first null is {} pixels'.format(psf_sum))
print('epsilon = V_clean/V_dirty = {}'.format(scale_factor))


hdu = fits.open(orig_resid)
resid_data = hdu[0].data
resid_header = hdu[0].header
#beams_table =  hdu[1].data
hdu.close()

scaled_resid = resid_data*scale_factor

#scaled_data = data*scale_factor
#fits.writeto(orig_resid.replace('.residual.fits','.residual.scaled.fits'), scaled_data, header)

#### RESTORING IMAGES ####

clean_beam = beams[plot_channel]
pix_scale = header['CDELT2']*u.deg
pix_scale = pix_scale.to(u.arcsec)
clean_beam_kernel = clean_beam.as_kernel(pix_scale)

hdu = fits.open(model)
model_data = hdu[0].data
model_header = hdu[0].header
hdu.close()

convl_model = model_data.copy()
convl_model[0,plot_channel,:,:] = clean_beam_sum*convolve_fft(convl_model[0,plot_channel,:,:], clean_beam_kernel)

orig_restor = convl_model[0,plot_channel,:,:] + resid_data[0,plot_channel,:,:]
scaled_restor = convl_model[0,plot_channel,:,:] + scaled_resid[0,plot_channel,:,:]

flux_orig_restor = np.nansum(orig_restor)/clean_beam_sum
flux_scaled_restor = np.nansum(scaled_restor)/clean_beam_sum


############################

plot_tag = os.path.split(os.path.split(data_path)[0])[1]

plt.clf()
fig,ax = plt.subplots(1, 2,figsize=(12,5))

ax[1].plot(radial_mean)
ax[1].axvline(first_min_ind, linestyle='--', color='red')
xmin = int(first_min_ind/2)
xmax = int(first_min_ind + first_min_ind-xmin + 1)
ymax = np.max(radial_mean[xmin:xmax])
ymin = np.min(radial_mean[xmin:xmax])
ax[1].set_xlim(xmin,xmax)
ax[1].set_ylim(ymin,ymax)
#ax.legend(loc='upper right')
ax[1].set_xlabel('Pixel', size=12)
ax[1].set_ylabel(r'Absolute value of radial mean of PSF', size=12)

zoom_ind_y = [int(cutout.shape[0]/2)-xmax, int(cutout.shape[0]/2)+xmax]
zoom_ind_x = [int(cutout.shape[1]/2)-xmax, int(cutout.shape[1]/2)+xmax]

psf_2d = ax[0].imshow(cutout[zoom_ind_y[0]:zoom_ind_y[1],zoom_ind_x[0]:zoom_ind_x[1]], cmap='viridis',\
norm=colors.SymLogNorm(linthresh=0.01, vmin=cutout.min(), vmax=cutout.max(), base=2))
fig.colorbar(psf_2d, ax=ax[0]);

min_contour = Circle((xmax,xmax), radius=first_min_ind, edgecolor='red', fill=False)
ax[0].add_patch(min_contour)
ax[0].set_title('PSF and contour of first null')
ax[0].set_xlabel('Pixel', size=12)
ax[0].set_ylabel('Pixel', size=12)

#fig.show()
fig.savefig(os.path.join(plots_path,'psf_null_{}.png'.format(plot_tag)), dpi=300)

fig,ax = plt.subplots(2, 2,figsize=(12,10))


minres = min([np.nanmin(resid_data[0,plot_channel,:,:]),np.nanmin(scaled_resid[0,plot_channel,:,:])])
maxres = max([np.nanmax(resid_data[0,plot_channel,:,:]),np.nanmax(scaled_resid[0,plot_channel,:,:])])

ymin = int(resid_data.shape[2]/2 - resid_data.shape[2]/4)
ymax = int(resid_data.shape[2]/2 + resid_data.shape[2]/4)
xmin = int(resid_data.shape[3]/2 - resid_data.shape[3]/4)
xmax = int(resid_data.shape[3]/2 + resid_data.shape[3]/4)

ax[0,0].imshow(resid_data[0,plot_channel,ymin:ymax,xmin:xmax], cmap='viridis', vmin=minres, vmax=maxres)
plt_scaled_resid = ax[0,1].imshow(scaled_resid[0,plot_channel,ymin:ymax,xmin:xmax], cmap='viridis', vmin=minres, vmax=maxres)

ax[0,0].set_title('Original residual, residuals at {}'.format(plot_tag))
ax[0,1].set_title('Rescaled residual')
ax[1,0].set_title(r'Original restored, $S_\nu = {:.4f}$ Jy'.format(flux_orig_restor))
ax[1,1].set_title(r'Rescaled restored, $S_\nu = {:.4f}$ Jy'.format(flux_scaled_restor))


#cbar_ax = fig.add_axes([0.475, 0.10, 0.02, 0.8])
#fig.colorbar(plt_scaled_resid, cax=cbar_ax);
#fig.tight_layout();

fig.colorbar(plt_scaled_resid, ax=ax[0,1]);


minrest = min([np.nanmin(orig_restor[ymin:ymax,xmin:xmax]),np.nanmin(scaled_restor[ymin:ymax,xmin:xmax])])
maxrest = max([np.nanmax(orig_restor[ymin:ymax,xmin:xmax]),np.nanmax(scaled_restor[ymin:ymax,xmin:xmax])])

ax[1,0].imshow(orig_restor[ymin:ymax,xmin:xmax], cmap='viridis', \
vmin=minrest, vmax=maxrest)
plt_scaled_restor = ax[1,1].imshow(scaled_restor[ymin:ymax,xmin:xmax], cmap='viridis', \
vmin=minrest, vmax=maxrest)

fig.colorbar(plt_scaled_restor, ax=ax[1,1]);

for j in range(len(ax[0])):
    for i in range(len(ax[1])):
        ax[j,i].set_xticklabels([])
        ax[j,i].set_xticks([])
        ax[j,i].set_yticklabels([])
        ax[j,i].set_yticks([])

fig.tight_layout();
#fig.show()
fig.savefig(os.path.join(plots_path,'rescaled_resid_comparison_{}.png'.format(plot_tag)), dpi=300)
