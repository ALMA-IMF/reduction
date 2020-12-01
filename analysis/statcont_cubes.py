"""
This script is a work in progress as of Nov 26

It is intended to be run in `imaging_results/` and will produce statcont contfiles

It is partly a performance test - for the bigger cubes, there were sometimes memory problems

The noise estimation region and num_workers are both hard-coded and should be
customized.

We should eventually allow multi-cube combination using full statcont abilities
"""
import time
from spectral_cube import SpectralCube
from astropy.io import fits
from dask.diagnostics import ProgressBar
pbar = ProgressBar()
pbar.register()

from statcont.cont_finding import c_sigmaclip_scube

import glob

import os

# for zarr storage
os.environ['TEMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

sizes = {fn: get_size(fn) for fn in glob.glob("*_12M_spw[0-9].image")}


for fn in sorted(sizes, key=lambda x: sizes[x]):
    outfn = fn+'.statcont.cont.fits'
    if not os.path.exists(outfn):
        t0 = time.time()

        print(fn, sizes[fn]/1024**3)

        cube = SpectralCube.read(fn)
        print(cube)

        noise = cube[50:100,50:-50,50:-50].mad_std()
        if noise == 0:
            noise = 0.001 * cube.unit

        with cube.use_dask_scheduler('threads', num_workers=32):
            result = c_sigmaclip_scube(cube, noise, save_to_tmp_dir=True)

        fits.PrimaryHDU(data=result[1], header=cube[0].header).writeto(fn+'.statcont.cont.fits', overwrite=True)
        print(f"{fn} -> {outfn} in {time.time()-t0}s")
