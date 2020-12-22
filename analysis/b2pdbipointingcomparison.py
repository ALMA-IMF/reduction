"""
Script to measure the positional offset between the PDBI 2mm data from Timea
and the ALMA-IMF observations.  Uses W51-IRS2 because it has the most overlap
w/the PDBI data.  PDBI data have 2.4x1.8" beam.  Measured offset is <1 pixel,
pixel scale is 0.48".  ALMA beam size is ~0.24", so it's less than an ALMA beam,
but hard to determine more accurately than that.


[-0.0, -1.0, 0.7, 0.75]
[-0.0, -1.0, 0.7, 0.75]
[0.451171875, -0.185546875, 0.61328125, 0.78125]
[0.451171875, -0.185546875, 0.61328125, 0.78125]
[-0.158203125, -0.626953125, 0.703125, 0.4453125]
[-0.154296875, -0.634765625, 0.703125, 0.451171875]
"""
from astropy.io import fits
from astropy import units as u
from spectral_cube import SpectralCube
from reproject import reproject_interp
import image_registration

pdbi_b4 = SpectralCube.read('W51M_2mm_PDBI.fits')
almaimf_b3 = SpectralCube.read('dirty_images/W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0.image.tt0.fits')
almaimf_b6 = SpectralCube.read('dirty_images/W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal7_finaliter.image.tt0.fits')

smb3 = almaimf_b3.minimal_subcube().convolve_to(pdbi_b4.beam)

crpb3 = reproject_interp(smb3[0].value, smb3[0].header, pdbi_b4[0].header)

fits.writeto('ALMAIMF_B3_IRS2_proj_to_PBDI.fits', data=crpb3, header=pdbi_b4[0].header, overwrite=True)

sm_b6 = almaimf_b6.minimal_subcube().convolve_to(pdbi_b4.beam)
crpb6, _ = reproject_interp((sm_b6[0].value, sm_b6[0].header), pdbi_b4[0].header)

fits.writeto('ALMAIMF_B6_IRS2_proj_to_PBDI.fits', data=crpb6, header=pdbi_b4[0].header, overwrite=True)

pixb4 = pdbi_b4.wcs.pixel_scale_matrix[1,1]
pixb3 = almaimf_b3.wcs.pixel_scale_matrix[1,1]
pixb6 = almaimf_b6.wcs.pixel_scale_matrix[1,1]

def interp_almaimf(nu):
    m = (crpb3*(pixb4/pixb3)**2 - crpb6*(pixb4/pixb6)**2) / (almaimf_b3.spectral_axis - almaimf_b6.spectral_axis)
    b = crpb3*(pixb4/pixb3)**2 - (almaimf_b3.spectral_axis * m)
    return (m * nu + b).decompose().value

alma_b4_interp = interp_almaimf(pdbi_b4.with_spectral_unit(u.GHz).spectral_axis[0])

fits.writeto('ALMAIMF_B4interp_IRS2_proj_to_PBDI.fits', data=alma_b4_interp.decompose().value, header=pdbi_b4[0].header, overwrite=True)


slc = (slice(310,329), slice(528,553))

im1 = alma_b4_interp[slc]
im2 = pdbi_b4[0].value[slc]

print(image_registration.chi2_shift_iterzoom(im1, im2))
print(image_registration.chi2_shift_iterzoom(im1, im2, verbose=True, zeromean=True))
print(image_registration.chi2_shift(im1, im2))
print(image_registration.chi2_shift(im1, im2, zeromean=True))
print(image_registration.chi2_shift(alma_b4_interp, pdbi_b4[0].value))
print(image_registration.chi2_shift(alma_b4_interp, pdbi_b4[0].value, zeromean=True))
