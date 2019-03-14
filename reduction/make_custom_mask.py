"""
Make a custom mask for each field

Requirements installation:

    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user',
                           'cython', 'https://github.com/astropy/regions/archive/master.zip',
                           'https://github.com/radio-astro-tools/spectral-cube/archive/master.zip'])
"""
import os
import numpy as np

# non-casa requirements
import regions
from spectral_cube import SpectralCube
from astropy import units as u
from metadata_tools import logprint

try:
    from casatools import image
    ia = image()
except ImportError:
    from taskinit import iatool
    ia = iatool()

def make_custom_mask(fieldname, imname, almaimf_code_path, band_id, rootdir="",
                     suffix=""):

    regfn = os.path.join(almaimf_code_path,
                         'clean_regions/{0}_{1}{2}.reg'.format(fieldname,
                                                               band_id,
                                                               suffix))
    regs = regions.read_ds9(regfn)

    logprint("Using region file {0} to create mask".format(regfn),
             origin='make_custom_mask')

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


    # CASA transposes arrays!!!!!
    mask_array = mask_array.T

    ia.open(imname)
    assert np.all(ia.shape() == mask_array[:,:,None,None].shape)
    cs = ia.coordsys()
    ia.close()

    maskname = ('{fieldname}_{band_id}{suffix}_mask.mask'
                .format(fieldname=fieldname, band_id=band_id,
                        suffix=suffix))
    # add a root directory if there is one
    # (if rootdir == "", this just returns maskname)
    maskname = os.path.join(rootdir, maskname)

    assert ia.fromarray(outfile=maskname,
                        pixels=mask_array.astype('float')[:,:,None,None],
                        csys=cs.torecord(), overwrite=True)
    ia.close()

    return maskname
