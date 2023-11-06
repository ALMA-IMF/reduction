import numpy as np
import sys

from astropy import log
log.setLevel('INFO')

from radio_beam.utils import BeamError

from spectral_cube import SpectralCube
import glob, os
os.chdir("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/")

import dask

# https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp
# If dir is not None, the file will be created in that directory; otherwise, a
# default directory is used. The default directory is chosen from a
# platform-dependent list, but the user of the application can control the
# directory location by setting the TMPDIR, TEMP or TMP environment variables.
# There is thus no guarantee that the generated filename will have any nice
# properties, such as not requiring quoting when passed to external commands
# via os.popen().
# https://stackoverflow.com/questions/37229398/python-tempfile-gettempdir-does-not-respect-tmpdir
# tempfile._candidate_tempdir_list() can be used to verify the list
# if the directory exists but is not writeable or does not exist, it will not be used
os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

print("Checking environment")
if os.getenv('ENVIRONMENT') == 'BATCH':
    pbar = False
else:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()

print("Checking for images.")
imlist = glob.glob("*spw[0-7].image")
imlist += glob.glob("*spw1_12M_sio.image")
imlist += glob.glob("*spw1_7M12M_sio.image")
has_model_minimized = [os.path.exists(x.replace(".image",
                                                ".model.minimized.fits.gz"))
                       for x in imlist]
print(f"Found {len(imlist)} images.  Of these, {sum(has_model_minimized)} have minimized models.")

import spectral_cube
from spectral_cube import SpectralCube

import random
#random.shuffle(imlist)
imlist = imlist[::-1] # July 2023: do SiO first
#imlist.insert(0, 'W51-IRS2_B6_spw1_12M_sio.image')

nthreads = os.getenv('SLURM_NTASKS')
print(f"Setting nthreads={nthreads}")
if nthreads is not None:
    nthreads = int(nthreads)
    dask.config.set(scheduler='threads')
else:
    dask.config.set(scheduler='synchronous')

print("Appended reduction/ path to path")
sys.path.append("/orange/adamginsburg/ALMA_IMF/reduction/reduction/")
from cube_finalizing import beam_correct_cube

import warnings
warnings.filterwarnings(action='ignore', category=spectral_cube.utils.BeamWarning)
warnings.filterwarnings(action='ignore', category=spectral_cube.utils.StokesWarning)

for fn in imlist:
    jvmfn = fn.replace(".image", ".JvM.image.pbcor.fits")
    print(f"Filename={fn} JvM filename={jvmfn}")
    cube = SpectralCube.read(fn)
    print(cube)
    sys.stdout.flush()
    sys.stderr.flush()
    good_beams = cube.identify_bad_beams(0.1)

    if os.path.exists(jvmfn):
        if os.path.getsize(jvmfn) == 0:
            print(f"{jvmfn} had size {os.path.getsize(jvmfn)}")
            os.remove(jvmfn)

    if fn.count('spw') == 1: # line cubes, not full cubes
        use_velocity = True
    elif fn.count('spw') == 2:
        use_velocity = False
    else:
        raise ValueError(f'{fn} is not a recognized filename type')

    if not os.path.exists(fn.replace(".image", ".model.minimized.fits.gz")):
        print(f"{fn} didn't have gzipped")
        sys.stdout.flush()
        sys.stderr.flush()
        beam_correct_cube(fn.replace(".image",""), pbcor=True,
                          use_velocity=use_velocity,
                          write_pbcor=True, pbar=pbar, save_to_tmp_dir=True)
    elif not os.path.exists(jvmfn):
        print(f"{fn} didn't have JvM")
        sys.stdout.flush()
        sys.stderr.flush()
        beam_correct_cube(fn.replace(".image",""), pbcor=True,
                          use_velocity=use_velocity,
                          write_pbcor=True, pbar=pbar, save_to_tmp_dir=True)

    elif os.path.exists(jvmfn) and good_beams.sum() < good_beams.size:
        print(f"{fn} had {(~good_beams).sum()} bad beams")
        sys.stdout.flush()
        sys.stderr.flush()

        try:
            commonbeam = cube.beams[good_beams].common_beam()
        except BeamError:
            print("Needed to calculate commonbeam with epsilon=0.005")
            commonbeam = cube.beams[good_beams].common_beam(epsilon=0.005)
        jvcube = SpectralCube.read(jvmfn)

        if np.abs(jvcube.beam.sr - commonbeam.sr)/commonbeam.sr < 1e-5:
            print(f"Beams are equal: common={commonbeam}, jvbeam={jvcube.beam}")
            print(f"No actions taken: {fn} was skipped")
        else:
            print(f"Cube needed beam correction.  Creating common beam cube for {fn}.")
            beam_correct_cube(fn.replace(".image",""), pbcor=True,
                              use_velocity=use_velocity,
                              write_pbcor=True, pbar=pbar, save_to_tmp_dir=True)
    else:
        print(f"{fn} was all done - no actions taken!")

