"""
This script is a work in progress as of Nov 26

It is intended to be run in `imaging_results/` and will produce statcont contfiles

It is partly a performance test - for the bigger cubes, there were sometimes memory problems

The noise estimation region and num_workers are both hard-coded and should be
customized.

We should eventually allow multi-cube combination using full statcont abilities
"""
import time
from astropy.table import Table
from spectral_cube import SpectralCube
from astropy.io import fits
from dask.diagnostics import ProgressBar

from statcont.cont_finding import c_sigmaclip_scube

import glob

import tempfile

import os

# for zarr storage
os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp'

pbar = ProgressBar()
pbar.register()

assert tempfile.gettempdir() == '/blue/adamginsburg/adamginsburg/tmp'

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'

tbl = Table.read('/bio/web/secure/adamginsburg/ALMA-IMF/tables/cube_stats.ecsv')

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

# simpler approach
#sizes = {fn: get_size(fn) for fn in glob.glob(f"{basepath}/*_12M_spw[0-9].image")}
filenames = list(tbl['filename']) + list(glob.glob(f"{basepath}/*_12M_spw[0-9].image")))

# use tbl, ignore 7m12m
sizes = {ii: get_size(f"{basepath}/{fn}")
         for ii, fn in enumerate(filenames)
         if '_12M_' in fn
         and os.path.exists(f"{basepath}/{fn}")
        } # ignore 7m12m


for ii in sorted(sizes, key=lambda x: sizes[x]):

    fn = f"{basepath}/{filenames[ii]}"

    outfn = fn+'.statcont.cont.fits'

    if not os.path.exists(outfn):
        t0 = time.time()

        # touch the file to allow parallel runs
        with open(outfn, 'w') as fh:
            fh.write("")

        print(fn, sizes[ii]/1024**3)

        cube = SpectralCube.read(fn)
        print(cube)

        with cube.use_dask_scheduler('threads', num_workers=32):
            if ii < len(tbl):
                noise = tbl['std'].quantity[ii]
            else:
                noise = cube.std()

            result = c_sigmaclip_scube(cube, noise, save_to_tmp_dir=True)

        fits.PrimaryHDU(data=result[1], header=cube[0].header).writeto(outfn,
                                                                       overwrite=True)
        print(f"{fn} -> {outfn} in {time.time()-t0}s")
