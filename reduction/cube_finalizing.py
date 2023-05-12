"""
Cube finalizing:

    1. Minimize the model, residual, and pb cubes
    2. Compute the PSF epsilon
    3. Create the JVM-corrected image and pb

"""
import numpy as np

import gzip
import bz2 as bzip
import os
from beam_volume_tools import epsilon_from_psf, conv_model, rescale
from spectral_cube import SpectralCube
from radio_beam.utils import BeamError

from astropy.io import fits
from astropy.table import Table
from astropy import log
from astropy import units as u

import contextlib
try:
    from tqdm import tqdm
except ImportError:
    # no progressbar; we could perhaps warn about this but it's not
    # functionally important
    tqdm = False

import time

def gzip_file(fn):
    with open(fn, "rb") as f_in:
        with gzip.open(fn+".gz", "wb") as f_out:
            f_out.writelines(f_in)

def bzip_file(fn):
    with open(fn, "rb") as f_in:
        with bzip.open(fn+".bz2", "wb") as f_out:
            f_out.writelines(f_in)

def beam_correct_cube(basename, minimize=True, pbcor=True, write_pbcor=True,
                      use_velocity=False,
                      pbar=False, beam_threshold=0.1, save_to_tmp_dir=False):

    if not pbar:
        pbar = contextlib.nullcontext()
        tpbar = False
    else:
        tpbar = tqdm

    t0 = time.time()

    basemodelname = basename+".model"
    baseresidualname = basename+".residual"
    imcube = SpectralCube.read(basename+".image", format='casa_image') # needed for header
    modcube = SpectralCube.read(basemodelname, format='casa_image')
    psfcube = SpectralCube.read(basename+".psf", format='casa_image')
    residcube = SpectralCube.read(baseresidualname, format='casa_image')
    if pbcor:
        pbcube = SpectralCube.read(basename+".pb", format='casa_image')
    log.info(f"Completed reading. t={time.time() - t0}")

    if use_velocity:
        imcube = imcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')
        modcube = modcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')
        residcube = residcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')
        pbcube = pbcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')
        psfcube = psfcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')

    good_beams = psfcube.identify_bad_beams(0.1)
    log.info(f"Found {good_beams.sum()} good beams out of {good_beams.size} channels")
    psf_max = psfcube.max(axis=(1,2))
    good_beams &= (psf_max > 0)
    log.info(f"Found {good_beams.sum()} good beams out of {good_beams.size} channels after excluding PSFs with zero value")

    if minimize:
        tmin = time.time()
        log.info(f"Starting minimize. t={tmin - t0}")

        print(f"pbar={pbar}, {type(pbar)}")
        with pbar:
            # apparently the residualcube can be maskless; if it is, we want to
            # instead use the image mask.  This is essential for "minimize" to
            # work, since it is cutting out the "padding" around the edges
            residmask = residcube.mask if residcube.mask is not None else imcube.mask if imcube.mask is not None else True
            cutslc = residcube.subcube_slices_from_mask(residmask & good_beams[:,None,None])

        log.info(f"Completed minimize.  cutslc={cutslc} t={time.time() - t0}.  minimizing took {time.time()-tmin}")

        modcube = modcube[cutslc]
        psfcube = psfcube[cutslc]
        residcube = residcube[cutslc]
        if pbcor:
            pbcube = pbcube[cutslc]

        if not os.path.exists(basemodelname+".minimized.fits.gz"):
            print(f"gzipping model {basemodelname}")
            modcube.write(basemodelname+".minimized.fits")
            gzip_file(basemodelname+".minimized.fits")
            print(f"bzipping model {basemodelname}")
            bzip_file(basemodelname+".minimized.fits")
        if not os.path.exists(baseresidualname+".minimized.fits.gz"):
            print(f"gzipping residual {baseresidualname}")
            modcube.write(baseresidualname+".minimized.fits")
            gzip_file(baseresidualname+".minimized.fits")
            print(f"bzipping residual {baseresidualname}")
            bzip_file(baseresidualname+".minimized.fits")

        log.info(f"Completed minslice. t={time.time() - t0}")
    else:
        modcube = modcube[good_beams]
        residcube = residcube[good_beams]
        psfcube = psfcube[good_beams]
        if pbcor:
            pbcube = pbcube[good_beams]


    teps = time.time()
    log.info(f"Epsilon beginning. t={teps - t0}")

    # there are sometimes problems with identifying a common beam
    try:
        epsdict = epsilon_from_psf(psfcube, export_clean_beam=True, beam_threshold=beam_threshold, pbar=tpbar, max_epsilon=0.01)
    except BeamError:
        print("Needed to calculate commonbeam with epsilon=0.005")
        epsdict = epsilon_from_psf(psfcube, epsilon=0.005, export_clean_beam=True, beam_threshold=beam_threshold, pbar=tpbar)
    log.info(f"Epsilon completed. t={time.time() - t0}, eps took {time.time()-teps}")


    clean_beam = epsdict['clean_beam']

    log.info(f"Convolving.  t={time.time()-t0}")
    with pbar:
        convmod = conv_model(modcube, clean_beam, save_to_tmp_dir=save_to_tmp_dir)

    log.info(f"Done convolving, now rescaling.  t={time.time()-t0}")

    merged = rescale(convmod, epsdict['epsilon'],
                     residual_image=residcube,
                     export_fits=False
                     )

    log.info(f"Done rescaling.  t={time.time()-t0}")


    merged.meta.update(imcube.meta)
    merged.header.update(imcube.header) # this was supposed to preserve header info but seems not to have
    merged.meta['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.header['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.meta['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.header['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.meta['JvM_epsilon_median'] = np.median(epsdict['epsilon'])
    merged.header['JvM_epsilon_median'] = np.median(epsdict['epsilon'])
    epsilon_table = fits.BinTableHDU(Table(data=[epsdict['epsilon']], names=['JvM_epsilon'], dtype=[np.float]))

    flatpb = pbcube.mean(axis=0)
    flatpb.hdu.writeto(basename+".flatpb.fits", overwrite=True)

    log.info(f"Beginning JvM write.  t={time.time()-t0}")
    hdul = merged.hdulist
    hdul.append(epsilon_table)
    # add any missing header keywords
    for key in imcube.header:
        # don't overwrite any WCS though
        if key not in hdul[0].header and key != 'HISTORY':
            hdul[0].header[key] = imcube.header[key]
    if 'HISTORY' in imcube.header:
        hdul[0].header['HISTORY'] = ''
        for row in imcube.header['HISTORY']:
            hdul[0].header['HISTORY'] = row
    # need to manually specify units b/c none of the model, residual, etc. have them!
    hdul[0].header['BUNIT'] = 'Jy/beam'
    hdul[0].header['CREDIT'] = 'Please cite Ginsburg et al 2022A&A...662A...9G when using these data, and Motte et al 2022A&A...662A...8M for the ALMA-IMF program'
    hdul[0].header['FILENAME'] = basename+".JvM.image.fits"
    with pbar:
        hdul.writeto(basename+".JvM.image.fits", overwrite=True)
    log.info(f"Done JvM write.  t={time.time()-t0}")
    
    header = hdul[0].header

    if pbcor:
        log.info(f"Beginning pbcor.  t={time.time()-t0}")
        pbc = merged / pbcube
        log.info(f"Done pbcor.  t={time.time()-t0}")
        if write_pbcor:
            log.info(f"Creating HDUlist.  t={time.time()-t0}")
            hdul = pbc.hdulist
            # copy header from non-pbcor
            hdul[0].header = header
            hdul[0].header['FILENAME'] = basename+".JvM.image.pbcor.fits"
            log.info(f"appending epsilon table.  t={time.time()-t0}")
            hdul.append(epsilon_table)
            log.info(f"changing dtype.  t={time.time()-t0}")
            with pbar:
                hdul[0].data = hdul[0].data.astype('float32')
                log.info(f"writing HDUL.  t={time.time()-t0}")
                hdul.writeto(basename+".JvM.image.pbcor.fits", overwrite=True)
            log.info(f"Done writing pbcor.  t={time.time()-t0}")
        return merged, pbc

    return merged
