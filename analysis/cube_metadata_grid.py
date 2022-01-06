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

# tempdir is irrelevant; should be TMPDIR
os.environ['TEMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'
os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

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

default_lines = {
    "h41a": "92.034434GHz",
    "ch3cnv8=1": "92.26144GHz",
    "ch3cn": "91.97GHz",  # range from 91.987 to 91.567
    "13cs_2-1": "92.49430800GHz",
    "n2hp": "93.173700GHz",
    "ch3cch_62-52": "102.547983GHz",
    "h2cs_322-221": "103.039927GHz",
    "h2cs_312-211": "104.617040GHz",
    "oc33s_18-17": "216.14735900GHz",
    "sio": "217.104984GHz",
    "h2co_303-202": "218.222195GHz",
    "c18o": "219.560358GHz",
    "so_6-5": "219.94944200GHz",
    "12co": "230.538GHz",
    "ocs_19-18": "231.06099340GHz",
    "13cs_5-4": "231.22068520GHz",
    "h30a": "231.900928GHz",
}
spws = {3: list(range(4)),
        6: list(range(8)),}

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


colnames_apriori = ['Field', 'Band', 'Config', 'spw', 'line', 'suffix', 'filename', 'bmaj', 'bmin', 'bpa', 'mod_date', 'wcs_restfreq', 'minfreq', 'maxfreq', 'biggest_bmaj', 'smallest_bmaj']
colnames_fromheader = ['imsize', 'cell', 'threshold', 'niter', 'pblimit', 'pbmask', 'restfreq', 'nchan', 'width', 'start', 'chanchunks', 'deconvolver', 'weighting', 'robust', 'git_version', 'git_date',]

rows = []

for field in "G337.92 W43-MM3 G328.25 G351.77 W43-MM2 G327.29 G338.93 W51-E G353.41 G008.67 W43-MM1 G010.62 W51-IRS2 G012.80 G333.60".split():
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

                    mod_date = time.ctime(os.path.getmtime(fn))

                    ia.open(fn)
                    hist = ia.history(list=False)
                    history = {x.split(":")[0]:x.split(": ")[1] for x in hist if ':' in x}
                    history.update({x.split("=")[0]:x.split("=")[1].lstrip() for x in hist if '=' in x})
                    ia.close()

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", use_dask=True)
                        cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    else:
                        cube = SpectralCube.read(fn)
                        cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        cube = cube.rechunk()
                    if hasattr(cube, 'beam'):
                        beam = cube.beam
                        biggest_beam = beam
                        smallest_beam = beam
                    else:
                        beams = cube.beams
                        # use the middle-ish beam
                        beam = beams[len(beams)//2]
                        biggest_beam = beams[np.argmax(beams.sr)]
                        smallest_beam = beams[np.argmin(beams.sr)]

                    print(cube)

                    spw = int(fn.split('spw')[1][0])

                    minfreq = cube.spectral_axis.min()
                    maxfreq = cube.spectral_axis.max()
                    restfreq = cube.wcs.wcs.restfrq

                    row = [field, band, config, spw, line, suffix, fn, beam.major.value, beam.minor.value, beam.pa.value, mod_date, restfreq, minfreq, maxfreq, biggest_beam.major, smallest_beam.minor] + [history[key] if key in history else '' for key in colnames_fromheader]
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

                    mod_date = time.ctime(os.path.getmtime(fn))

                    ia.open(fn)
                    hist = ia.history(list=False)
                    history = {x.split(":")[0]:x.split(": ")[1] for x in hist if ':' in x}
                    history.update({x.split("=")[0]:x.split("=")[1].lstrip() for x in hist if '=' in x})
                    ia.close()

                    line = 'none'

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", use_dask=True)
                    else:
                        cube = SpectralCube.read(fn)
                    if hasattr(cube, 'beam'):
                        beam = cube.beam
                        biggest_beam = beam
                        smallest_beam = beam
                    else:
                        beams = cube.beams
                        beam = beams[len(beams)//2]
                        biggest_beam = beams[np.argmax(beams.sr)]
                        smallest_beam = beams[np.argmin(beams.sr)]

                    minfreq = cube.spectral_axis.min()
                    maxfreq = cube.spectral_axis.max()
                    restfreq = cube.wcs.wcs.restfrq

                    row = [field, band, config, spw, line, suffix, fn, beam.major.value, beam.minor.value, beam.pa.value, mod_date, restfreq, minfreq, maxfreq, biggest_beam.major, smallest_beam.minor] + [history[key] if key in history else '' for key in colnames_fromheader]
                    rows.append(row)

from astropy.table import Table
colnames = colnames_apriori+colnames_fromheader
columns = list(map(list, zip(*rows)))
tbl = Table(columns, names=colnames)
print(tbl)
from pathlib import Path
tbldir = Path('/orange/adamginsburg/web/secure/ALMA-IMF/tables')
tbl.write(tbldir / 'cube_metadata.ecsv', overwrite=True)
tbl.write(tbldir / 'cube_metadata.ipac', format='ascii.ipac', overwrite=True)
tbl.write(tbldir / 'cube_metadata.html', format='ascii.html', overwrite=True)
tbl.write(tbldir / 'cube_metadata.tex', overwrite=True)
tbl.write(tbldir / 'cube_metadata.js.html', format='jsviewer')

conttbl = Table.read('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/June2021Release/tables/metadata_image.tt0.ecsv')

for cont_col in ('bmaj', 'bmin', 'bpa', 'cellsize'):
    # Add new column
    tbl[f'cont_{cont_col}'] = np.nan

for row in tbl:
    if row['Config'] == '12M':
        match = ((conttbl['region'] == row['Field']) &
                 (conttbl['band'] == f"B{row['Band']}") &
                 (conttbl['robust'] == 'r0.0') &
                 (conttbl['pbcor']) & ~(conttbl['bsens']) &
                 (conttbl['suffix'] == 'finaliter')
                 )
        assert match.sum() == 1
        for cont_col in ('bmaj', 'bmin', 'bpa', 'cellsize'):
            # Add new column
            row[f'cont_{cont_col}'] = conttbl[cont_col][match][0]

tbl.write(tbldir / 'cube_metadata_withcont.ecsv', overwrite=True)
tbl.write(tbldir / 'cube_metadata_withcont.ipac', format='ascii.ipac', overwrite=True)

os.chdir(cwd)
