"""
Cube finalizing:

    1. Minimize the model, residual, and pb cubes
    2. Compute the PSF epsilon
    3. Create the JVM-corrected image and pb

"""
import numpy as np

from beam_volume_tools import epsilon_from_psf, conv_model, rescale
from spectral_cube import SpectralCube
from radio_beam.utils import BeamError

from astropy.io import fits
from astropy.table import Table
from astropy import log

import time

def beam_correct_cube(basename, minimize=True, pbcor=True, write_pbcor=True):

    t0 = time.time()

    modcube = SpectralCube.read(basename+".model", format='casa_image')
    psfcube = SpectralCube.read(basename+".psf", format='casa_image')
    residcube = SpectralCube.read(basename+".residual", format='casa_image')
    if pbcor:
        pbcube = SpectralCube.read(basename+".pb", format='casa_image') 
    log.info(f"Completed reading. t={time.time() - t0}")

    if minimize:
        tmin = time.time()
        log.info(f"Starting minimize. t={tmin - t0}")

        cutslc = residcube.subcube_slices_from_mask(residcube.mask)

        log.info(f"Completed minimize. t={time.time() - t0}.  minimizing took {time.time()-tmin}")

        modcube = modcube[cutslc]
        psfcube = psfcube[cutslc]
        residcube = residcube[cutslc]
        if pbcor:
            pbcube = pbcube[cutslc]

        log.info(f"Completed minslice. t={time.time() - t0}")

    teps = time.time()
    log.info(f"Epsilon beginning. t={teps - t0}")
    # there are sometimes problems with identifying a common beam
    try:
        epsdict = epsilon_from_psf(psfcube, export_clean_beam=True)
    except BeamError:
        epsdict = epsilon_from_psf(psfcube, epsilon=0.005, export_clean_beam=True)
    log.info(f"Epsilon completed. t={time.time() - t0}, eps took {time.time()-teps}")


    clean_beam = epsdict['clean_beam']

    log.info(f"Convolving.  t={time.time()-t0}")
    convmod = conv_model(modcube, clean_beam)

    log.info(f"Done convolving, now rescaling.  t={time.time()-t0}")

    merged = rescale(convmod, epsdict['epsilon'],
                     residual_image=residcube,
                     export_fits=False
                     )

    log.info(f"Done rescaling.  t={time.time()-t0}")

    merged.meta['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.header['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.meta['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.header['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.meta['JvM_epsilon_median'] = np.median(epsdict['epsilon'])
    merged.header['JvM_epsilon_median'] = np.median(epsdict['epsilon'])
    epsilon_table = fits.BinTableHDU(Table(data=[epsdict['epsilon']], names=['JvM_epsilon'], dtype=[np.float]))

    log.info(f"Beginning JvM write.  t={time.time()-t0}")
    hdul = merged.hdulist
    hdul.append(epsilon_table)
    hdul.writeto(basename+".JvM.image.fits", overwrite=True)
    log.info(f"Done JvM write.  t={time.time()-t0}")

    if pbcor:
        log.info(f"Beginning pbcor.  t={time.time()-t0}")
        pbc = merged / pbcube
        log.info(f"Done pbcor.  t={time.time()-t0}")
        if write_pbcor:
            log.info(f"Creating HDUlist.  t={time.time()-t0}")
            hdul = pbc.hdulist
            log.info(f"appending epsilon table.  t={time.time()-t0}")
            hdul.append(epsilon_table)
            log.info(f"changing dtype.  t={time.time()-t0}")
            hdul[0].data = hdul[0].data.astype('float32')
            log.info(f"writing HDUL.  t={time.time()-t0}")
            hdul.writeto(basename+".JvM.image.pbcor.fits", overwrite=True)
            log.info(f"Done writing pbcor.  t={time.time()-t0}")
        return merged, pbc

    return merged
