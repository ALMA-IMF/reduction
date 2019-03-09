"""
Make a custom mask for each field
"""
import os
import numpy as np

# non-casa requirements
import regions
from spectral_cube import SpectralCube
from astropy import units as u

from taskinit import iatool
ia = iatool()

def make_custom_mask(fieldname, imname, almaimf_code_path, band_id):

    regs = regions.read_ds9(os.path.join(almaimf_code_path, 'clean_regions/{0}.reg'.format(fieldname)))

    cube = SpectralCube.read(imname, format='casa_image')
    image = cube[0]
    if image.unit.is_equivalent(u.Jy/u.beam):
        image = image * u.beam
    else:
        assert image.unit.is_equivalent(u.Jy)

    mask_array = np.zeros(image.shape, dtype='bool')

    for reg in regs:

        threshold = u.Quantity(reg.meta['label'])
        assert threshold.unit.is_equivalent(u.Jy)

        preg = reg.to_pixel(image.wcs)
        msk = preg.to_mask()

        mask_array[msk.bbox.slices] = msk.multiply(image) > threshold


    ia.open(imname)
    assert np.all(ia.shape() == mask_array[:,:,None,None].shape)
    cs = ia.coordsys()
    ia.close()

    maskname = ('{fieldname}_{band_id}_clean_mask.mask'
                .format(fieldname=fieldname, band_id=band_id))
    assert ia.fromarray(outfile=maskname,
                        pixels=mask_array.astype('float')[:,:,None,None],
                        csys=cs.torecord(), overwrite=True)
    ia.close()

    return maskname
