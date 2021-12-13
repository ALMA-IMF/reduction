"""
Cube finalizing:

    1. Minimize the model, residual, and pb cubes
    2. Compute the PSF epsilon
    3. Create the JVM-corrected image and pb

"""

from beam_volume_tools import epsilon_from_psf, conv_model, rescale
from spectral_cube import SpectralCube
from radio_beam.utils import BeamError

def beam_correct_cube(basename, minimize=True, pbcor=True, write_pbcor=True):
    modcube = SpectralCube.read(basename+".model", format='casa_image')
    psfcube = SpectralCube.read(basename+".psf", format='casa_image')
    residcube = SpectralCube.read(basename+".residual", format='casa_image')
    if pbcor:
        pbcube = SpectralCube.read(basename+".pb", format='casa_image') 

    if minimize:
        cutslc = residcube.subcube_slices_from_mask(residcube.mask)

        modcube = modcube[cutslc]
        psfcube = psfcube[cutslc]
        residcube = residcube[cutslc]
        if pbcor:
            pbcube = pbcube[cutslc]

    # there are sometimes problems with identifying a common beam
    try:
        epsdict = epsilon_from_psf(psfcube, export_clean_beam=True)
    except BeamError:
        epsdict = epsilon_from_psf(psfcube, epsilon=0.005, export_clean_beam=True)


    clean_beam = epsdict['clean_beam']

    convmod = conv_model(modcube, clean_beam)

    merged = rescale(convmod, epsdict['epsilon'],
                     residual_image=residcube,
                     export_fits=False
                     )
    merged.meta['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.header['JvM_epsilon_max'] = np.max(epsdict['epsilon'])
    merged.meta['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.header['JvM_epsilon_min'] = np.min(epsdict['epsilon'])
    merged.meta['JvM_epsilon_median'] = np.median(epsdict['epsilon'])
    merged.header['JvM_epsilon_median'] = np.median(epsdict['epsilon'])

    merged.write(basename+".JvM.image.fits", overwrite=True)

    if pbcor:
        pbc = merged / pbcube
        if write_pbcor:
            pbc.write(basename+".JvM.image.pbcor.fits", overwrite=True)
        return merged, pbc

    return merged
