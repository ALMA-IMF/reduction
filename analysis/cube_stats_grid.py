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

from pathlib import Path
tbldir = Path('/bio/web/secure/adamginsburg/ALMA-IMF/tables')

if os.getenv('NO_PROGRESSBAR') is None:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

nthreads = 1
scheduler = 'synchronous'

os.environ['TEMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

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
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'
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

cache_stats_file = open(tbldir / "cube_stats.txt", 'w')

rows = []

for field in "G010.62 W51-IRS2 G012.80 G333.60 W43-MM2 G327.29 G338.93 W51-E G353.41 G008.67 G337.92 W43-MM3 G328.25 G351.77 W43-MM1".split():
    for band in (3,6):
        for config in ('7M12M', '12M'):
            for line in list(default_lines.keys()) + spws[band]:
                for suffix in (".image", ".contsub.image"):

                    if line not in default_lines:
                        line = 'none'
                        spw = line
                        globblob = f"{field}_B{band}_spw{spw}_{config}_spw{spw}{suffix}"
                    else:
                        globblob = f"{field}_B{band}*_{config}_*{line}{suffix}"


                    fn = glob.glob(globblob)

                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    if line in default_lines:
                        spw = int(fn.split('spw')[1][0])

                    print(f"Beginning field {field} band {band} config {config} line {line} spw {spw} suffix {suffix}")

                    ia.open(fn)
                    history = {x.split(":")[0]:x.split(": ")[1] for x in ia.history()}
                    ia.close()

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", format='fits', use_dask=True)
                        cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    else:
                        cube = SpectralCube.read(fn, format='casa_image')
                        cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        cube = cube.rechunk(save_to_tmp_dir=True)

                    if hasattr(cube, 'beam'):
                        beam = cube.beam
                    else:
                        beams = cube.beams
                        # use the middle-ish beam
                        beam = beams[len(beams)//2]

                    print(cube)

                    minfreq = cube.spectral_axis.min()
                    maxfreq = cube.spectral_axis.max()
                    restfreq = cube.wcs.wcs.restfrq

                    stats = cube.statistics()
                    min = stats['min']
                    max = stats['max']
                    std = stats['sigma']
                    sum = stats['sum']
                    mean = stats['mean']


                    #min = cube.min()
                    #max = cube.max()
                    ##mad = cube.mad_std()
                    #std = cube.std()
                    #sum = cube.sum()
                    #mean = cube.mean()

                    del cube

                    if os.path.exists(fn.replace(".image", ".model")+".fits"):
                        modcube = SpectralCube.read(fn.replace(".image", ".model")+".fits", format='fits', use_dask=True)
                    else:
                        modcube = SpectralCube.read(fn.replace(".image", ".model"), format='casa_image')
                        modcube = modcube.rechunk(save_to_tmp_dir=True)

                    modstats = modcube.statistics()
                    modmin = modstats['min']
                    modmax = modstats['max']
                    modstd = modstats['sigma']
                    modsum = modstats['sum']
                    modmean = modstats['mean']

                    del modcube

                    row = ([field, band, config, spw, line, suffix, fn, beam.major.value, beam.minor.value, beam.pa.value, restfreq, minfreq, maxfreq] +
                           [history[key] if key in history else '' for key in colnames_fromheader] +
                           [min, max, std, sum, mean] +
                           [modmin, modmax, modstd, modsum, modmean])
                    rows.append(row)

                    cache_stats_file.write(" ".join(map(str, row)) + "\n")
                    cache_stats_file.flush()

cache_stats_file.close()

from astropy.table import Table
colnames = colnames_apriori+colnames_fromheader+colnames_stats

def try_qty(x):
    try:
        return u.Quantity(x)
    except:
        return list(x)

columns = list(map(try_qty, zip(*rows)))
tbl = Table(columns, names=colnames)
print(tbl)
tbl.write(tbldir / 'cube_stats.ecsv', overwrite=True)
tbl.write(tbldir / 'cube_stats.ipac', format='ascii.ipac', overwrite=True)
tbl.write(tbldir / 'cube_stats.html', format='ascii.html', overwrite=True)
tbl.write(tbldir / 'cube_stats.tex', overwrite=True)
tbl.write(tbldir / 'cube_stats.js.html', format='jsviewer')

os.chdir(cwd)
