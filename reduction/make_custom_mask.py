"""
Make a custom mask for each field

Requirements installation:

    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user',
                           'cython', 'https://github.com/astropy/regions/archive/master.zip',
                           'https://github.com/radio-astro-tools/spectral-cube/archive/master.zip'])
"""
import os
import numpy as np

from tasks import imstat, makemask

# non-casa requirements
try:
    import regions
    from spectral_cube import SpectralCube
    from astropy import units as u
    from metadata_tools import logprint
except:
    print 'Non-casa requirements not available'

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
        assert image.unit.is_equivalent(u.Jy), "Image must be in Jansky/beam."

    mask_array = np.zeros(image.shape, dtype='bool')

    for reg in regs:

        threshold = u.Quantity(reg.meta['label'])
        assert threshold.unit.is_equivalent(u.Jy), "Threshold must by in mJy or Jy"

        preg = reg.to_pixel(image.wcs)
        msk = preg.to_mask()

        mask_array[msk.bbox.slices] = (msk.multiply(image) > threshold) | mask_array[msk.bbox.slices]


    # CASA transposes arrays!!!!!
    mask_array = mask_array.T

    ia.open(imname)
    assert np.all(ia.shape() == mask_array[:,:,None,None].shape), "Failure: image shape doesn't match mask shape"
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
                        csys=cs.torecord(), overwrite=True), "FAILURE in final mask creation step"
    ia.close()

    return maskname

def make_rms_mask(imname, rms_region, nrms=5.):
    # Calculate the rms inside input region
    rms = imstat(imagename=imname, region=rms_region)['rms'][0]
    rmslevel = rms * nrms
    print 'Mask for: ', imname
    print 'rms level: ', rmslevel

    # Calculate internal mask
    ia.open(imname)
    ia.calcmask('"%s" > %.1e' % (imname, rmslevel), name='selfcal_mask')
    ia.close()

    # Create mask file
    maskname = imname+".selfcal.mask"
    makemask(mode='copy', inpimage=imname,
            inpmask=imname+":selfcal_mask",
            output=maskname, overwrite=True)

    # Delete internal mask
    makemask(mode='delete', inpmask=imname+":selfcal_mask")

    return maskname
