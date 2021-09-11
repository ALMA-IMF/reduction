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
    print(modelcube)

    filt = modelcube.spectral_smooth_median(median_npix)
    print("Filtered cube: ", filt)

    ia.open(basename+".model")

    # iterate over channels under the expectation that dask is only evaluating as needed
    for ii in range(filt.shape[0]):

        filtslc = filt.filled_data[ii, :, :]
        assert filtslc.ndim == 2

        modslc = modelcube.filled_data[ii, :, :]
        assert modslc.ndim == 2
        deviation = (modslc - filtslc) / filtslc

        reject = np.abs(deviation) > threshold_factor

        if np.any(reject):
            print(ii, end=' ')
            modslc[reject] = filtslc.value[reject]
            modslc = modslc[None,None,:,:]

            ia.putchunk(pixels=modslc.T.astype('float64'), blc=[-1,-1,-1,ii])

    ia.close()
