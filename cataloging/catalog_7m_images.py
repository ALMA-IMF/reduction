import numpy as np

from dendrocat import RadioSource, MasterCatalog
from dendrocat.utils import match
from dendrocat.aperture import Circle, Annulus


from spectral_cube import SpectralCube
from radio_beam import Beam

from astropy.io import fits
from astropy import units as u
from astropy import stats
from astropy.convolution import convolve_fft

import reproject


# for the 3mm data
beam = Beam(20*u.arcsec)

objects = {}
for spw in range(16, 23, 2):
    cube = SpectralCube.read('/Volumes/external/almaimf/member.uid___A001_X1296_X133.W43-MM3_sci.spw{0}.mfs.I.pbcor.fits'.format(spw))
    cubesm = cube.convolve_to(beam)

    source_object = RadioSource([cubesm.hdu])

    std = cubesm.mad_std().value
    source_object.to_dendrogram(min_value=std*2, min_delta=std, min_npix=cubesm.pixels_per_beam/5,)
    source_object.to_catalog()
    objects[spw] = source_object

fh = fits.open('/Users/adam/work/mgps/W43/GAL_031_precon_2_arcsec_pass_9_PlanckCombined.fits')
cutout,_ = reproject.reproject_interp(fh, cubesm[0,:,:].header)
cutout_sm = convolve_fft(cutout, Beam(20*u.arcsec).deconvolve(Beam(10*u.arcsec)).as_kernel(objects[16].pixel_scale))
cropped_mgps = fits.PrimaryHDU(data=cutout_sm, header=cubesm[0,:,:].header)
cropped_mgps.header['CRVAL3'] = fh[0].header['REFFREQ']
cropped_mgps.header['REFFREQ'] = fh[0].header['REFFREQ']
cropped_mgps.header['TELESCOP'] = 'GBT'
mgps = RadioSource([cropped_mgps])
mgps.nu = fh[0].header['REFFREQ']*u.Hz
mgps.freq_id = '91.5GHz'
mgps.beam = Beam(10*u.arcsec)
mgps.set_metadata()
std = stats.mad_std(mgps.data, ignore_nan=True)
mgps.to_dendrogram(min_value=std*4, min_delta=std, min_npix=10)
mgps.to_catalog()
objects['MGPS'] = mgps

matched = match(*list(objects.values()), verbose=True, threshold=10*u.arcsec)

fixed_circle = Circle([0, 0], 20*u.arcsec, name='fixedcirc')
matched.photometer(fixed_circle)


freqs = u.Quantity([u.Quantity(x.split("_")[0]) for x in matched.catalog.colnames if '_dend_flux' in x])
cns = [x for x in matched.catalog.colnames if '_dend_flux' in x]

fluxes = matched.catalog[cns].as_array().view('float64').reshape(len(matched.catalog), len(cns)).T

import pylab as pl
pl.figure(1).clf()
inds = np.argsort(freqs)
pl.plot(freqs[inds], fluxes[inds], 'o-')

pl.figure(2).clf()
ax1 = pl.subplot(2,3,1, projection=objects[16].wcs)
ax1.imshow(objects[16].data)

ax2 = pl.subplot(2,3,2, projection=objects[18].wcs)
ax2.imshow(objects[18].data)

ax3 = pl.subplot(2,3,4, projection=objects[20].wcs)
ax3.imshow(objects[20].data)

ax4 = pl.subplot(2,3,5, projection=objects[22].wcs)
ax4.imshow(objects[22].data)

ax5 = pl.subplot(1,3,3, projection=mgps.wcs)
ax5.imshow(mgps.data)

for ax in (ax1,ax2,ax3,ax4,ax5):
    ax.plot(mgps.catalog['x_cen'], mgps.catalog['y_cen'], 'wx', transform=ax.get_transform('world'))
