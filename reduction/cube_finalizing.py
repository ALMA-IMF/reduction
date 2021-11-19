"""
Cube finalizing:

    1. Minimize the model, residual, and pb cubes
    2. Compute the PSF epsilon
    3. Create the JVM-corrected image and pb

"""

from beam_volume_tools import epsilon_from_psf, conv_model, rescale
from spectral_cube import SpectralCube
from radio_beam import BeamError

def beam_correct_cube(basename, minimize=True):
    modcube = SpectralCube.read(basename+".model")
    psfcube = SpectralCube.read(basename+".psf")
    residcube = SpectralCube.read(basename+".residual")

    if minimize:
        cutslc = residcube.subcube_slices_from_mask(residcube.mask)

        modcube = modcube[cutslc]
        psfcube = psfcube[cutslc]
        residcube = residcube[cutslc]

    # there are sometimes problems with identifying a common beam
    try:
        epsdict = epsilon_from_psf(psfcube, export_clean_beam=True)
    except BeamError:
        epsdict = epsilon_from_psf(psfcube, epsilon=0.005, export_clean_beam=True)


    clean_beam = epsdict['clean_beam']

    convmod = conv_model(modcube, clean_beam)

    merged = rescale(convmod, epsdict['epsilon'],
                     residual_image=residcube,
                     clean_beam=clean_beam)

    merged.write(basename+".JvM.image.fits")

    return merged
