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

from casatools import image
ia = image()

if os.getenv('NO_PROGRESSBAR') is None:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

nthreads = 1
scheduler = 'synchronous'

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
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'
os.chdir(basepath)
print(f"Changed from {cwd} to {basepath}, now running cube metadata assembly")

global then
then = time.time()
def dt():
    global then
    now = time.time()
    print(f"Elapsed: {now-then}")
    then = now


colnames_apriori = ['Field', 'Band', 'Config', 'spw', 'line', 'suffix', 'filename', 'bmaj', 'bmin', 'bpa', 'wcs_restfreq', 'minfreq', 'maxfreq']
colnames_fromheader = ['imsize', 'cell', 'threshold', 'niter', 'pblimit', 'pbmask', 'restfreq', 'nchan', 'width', 'start', 'chanchunks', 'deconvolver', 'weighting', 'robust', 'git_version', 'git_date', ]

rows = []

for field in "W43-MM2 G327.29 G338.93 W51-E G353.41 G008.67 G337.92 W43-MM3 G328.25 G351.77 W43-MM1 G010.62 W51-IRS2 G012.80 G333.60".split():
    for band in (3,6):
        for config in ('7M12M', '12M'):
            for line in default_lines:
                for suffix in (".image", ".contsub.image"):
                    globblob = f"{field}_B{band}*_{config}_*{line}{suffix}"
                    fn = glob.glob(globblob)
                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    ia.open(fn)
                    history = {x.split(":")[0]:x.split(": ")[1] for x in ia.history()}
                    ia.close()

                    cube = SpectralCube.read(fn)
                    if hasattr(cube, 'beam'):
                        beam = cube.beam
                    else:
                        beams = cube.beams
                        beam = beams.smallest_beam()

                    spw = int(fn.split('spw')[1][0])

                    minfreq = cube.spectral_axis.min()
                    maxfreq = cube.spectral_axis.max()
                    restfreq = cube.wcs.wcs.restfrq

                    row = [field, band, config, spw, line, suffix, fn, beam.major.value, beam.minor.value, beam.pa.value, restfreq, minfreq, maxfreq] + [history[key] if key in history else '' for key in colnames_fromheader]
                    rows.append(row)


            for spw in spws[band]:
                for suffix in (".image", ".contsub.image"):
                    print(f"Beginning field {field} band {band} config {config} spw {spw} suffix {suffix}")
                    globblob = f"{field}_B{band}_spw{spw}_{config}_spw{spw}{suffix}"
                    fn = glob.glob(globblob)
                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    ia.open(fn)
                    history = {x.split(":")[0]:x.split(": ")[1] for x in ia.history()}
                    ia.close()

                    line = 'none'

                    cube = SpectralCube.read(fn)
                    if hasattr(cube, 'beam'):
                        beam = cube.beam
                    else:
                        beams = cube.beams
                        beam = beams.smallest_beam()

                    minfreq = cube.spectral_axis.min()
                    maxfreq = cube.spectral_axis.max()
                    restfreq = cube.wcs.wcs.restfrq

                    row = [field, band, config, spw, line, suffix, fn, beam.major.value, beam.minor.value, beam.pa.value, restfreq, minfreq, maxfreq] + [history[key] if key in history else '' for key in colnames_fromheader]
                    rows.append(row)

from astropy.table import Table
colnames = colnames_apriori+colnames_fromheader
columns = list(map(list, zip(*rows)))
tbl = Table(columns, names=colnames)
print(tbl)
from pathlib import Path
tbldir = Path('/bio/web/secure/adamginsburg/ALMA-IMF/tables')
tbl.write(tbldir / 'cube_metadata.ecsv', overwrite=True)
tbl.write(tbldir / 'cube_metadata.ipac', format='ascii.ipac', overwrite=True)
tbl.write(tbldir / 'cube_metadata.html', format='ascii.html', overwrite=True)
tbl.write(tbldir / 'cube_metadata.tex', overwrite=True)
tbl.write(tbldir / 'cube_metadata.js.html', format='jsviewer')

os.chdir(cwd)
