from spectral_cube import SpectralCube
import numpy as np
import os
import astropy.units as u
from astropy import constants
try:
    from casac import casac
    synthesisutils = casac.synthesisutils
    from taskinit import msmdtool, casalog, qatool, tbtool, mstool, iatool
    from tasks import tclean, flagdata
except ImportError:
    from casatools import (quanta as qatool, table as tbtool, msmetadata as
                           msmdtool, synthesisutils, ms as mstool,
                           image as iatool)
    from casatasks import casalog, tclean, flagdata
ia = iatool()


def despeckle_model_image(basename, threshold_factor=2.0, median_npix=3):

    modelcube = SpectralCube.read(basename+".model", format='casa_image')

    filt = modelcube.spectral_smooth_median(median_npix)

    deviation = (modelcube - filt) / filt

    reject = np.abs(deviation) > threshold_factor

    ia.open(basename+".model")

    for ii, slc in enumerate(modelcube.filled_data[:]):
        reject_slc = reject[ii,:,:]
        slc[reject] = filt[ii][reject_slc]
        slc = slc[None,None,:,:]

        ia.putchunk(pixels=slc.T.astype('float64'), blc=[-1,-1,-1,ii])

    ia.close()
