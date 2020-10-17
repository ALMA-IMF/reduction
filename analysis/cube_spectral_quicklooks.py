import glob
from astropy.io import fits
from astropy import visualization
import pylab as pl


import os
import time
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.stats import mad_std
import pylab as pl
import radio_beam
import glob
from spectral_cube import SpectralCube,DaskSpectralCube
from spectral_cube.lower_dimensional_structures import Projection


from pathlib import Path

if os.getenv('NO_PROGRESSBAR') is None:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

nthreads = 1
scheduler = 'synchronous'
nthreads = 8
scheduler = 'threads'

if os.getenv('DASK_THREADS') is not None:
    try:
        nthreads = int(os.getenv('DASK_THREADS'))
        if nthreads > 1:
            scheduler = 'threads'
        else:
            scheduler = 'synchronous'
    except (TypeError,ValueError):
        nthreads = 1
        scheduler = 'synchronous'

print(f"Using scheduler {scheduler} with {nthreads} threads")

default_lines = {'n2hp': '93.173700GHz',
                 'sio': '217.104984GHz',
                 'h2co303': '218.222195GHz',
                 '12co': '230.538GHz',
                 'h30a': '231.900928GHz',
                 'h41a': '92.034434GHz',
                 "c18o": "219.560358GHz",
                }
spws = {3: list(range(4)),
        6: list(range(7)),}

suffix = '.image'

cwd = os.getcwd()
basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results')
os.chdir(basepath)
print(f"Changed from {cwd} to {basepath}, now running cube stats assembly")

global then
then = time.time()
def dt():
    global then
    now = time.time()
    print(f"Elapsed: {now-then}")
    then = now


colnames_apriori = ['Field', 'Band', 'Config', 'spw', 'line', 'suffix', 'filename', 'bmaj', 'bmin', 'bpa', 'wcs_restfreq', 'minfreq', 'maxfreq']
colnames_fromheader = ['imsize', 'cell', 'threshold', 'niter', 'pblimit', 'pbmask', 'restfreq', 'nchan', 'width', 'start', 'chanchunks', 'deconvolver', 'weighting', 'robust', 'git_version', 'git_date', ]
colnames_stats = 'min max std sum mean'.split() + ['mod'+x for x in 'min max std sum mean'.split()]

rows = []

spectra_dir = basepath / "spectra"
os.environ['TEMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

for field in "W43-MM2 G327.29 G338.93 W51-E G353.41 G008.67 G337.92 W43-MM3 G328.25 G351.77 W43-MM1 G010.62 W51-IRS2 G012.80 G333.60".split():
    for band in (3,6):
        for config in ('12M',):
            for line in spws[band]: #list(default_lines.keys()):
                for suffix in (".image", ".contsub.image"):

                    if line not in default_lines:
                        spw = line
                        linename = ''
                        globblob = f"{field}_B{band}_spw{spw}_{config}_spw{spw}{suffix}"
                    else:
                        linename = line
                        globblob = f"{field}_B{band}*_{config}_*{linename}{suffix}"


                    fn = glob.glob(globblob)

                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    if line in default_lines:
                        spw = int(fn.split('spw')[1][0])

                    print(f"Beginning field {field} band {band} config {config} line {linename} spw {spw} suffix {suffix}")

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", format='fits')
                    else:
                        cube = SpectralCube.read(fn, format='casa_image')
                    #print('Saving to tmpdir')
                    #cube = cube.rechunk(save_to_tmp_dir=True)

                    print('computing max(axis=(1,2))')
                    mxspecfn = spectra_dir / f"{field}_B{band}_spw{spw}_{config}_{linename}{suffix}_max.fits"
                    if not os.path.exists(mxspecfn):
                        maxspec = cube.max(axis=(1,2))
                        maxspec.write(mxspecfn)

                    print('computing mean(axis=(1,2))')
                    mnspecfn = spectra_dir / f"{field}_B{band}_spw{spw}_{config}_{linename}{suffix}_mean.fits"
                    if not os.path.exists(mnspecfn):
                        meanspec = cube.mean(axis=(1,2))
                        meanspec.write(mnspecfn)

                    del cube
