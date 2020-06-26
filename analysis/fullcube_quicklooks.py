print("Beginning imports")
import glob
from astropy.io import fits
from astropy import visualization


import os
import time
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.stats import mad_std
import pylab as pl
import radio_beam
import tempfile
import dask.array as da
import dask
from spectral_cube import SpectralCube,DaskSpectralCube
from spectral_cube.lower_dimensional_structures import Projection
print("Completed imports")

import pylab as pl
print("Imported pylab")

if os.getenv('NO_PROGRESSBAR') is None:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

    print(f"pbar is {pbar}")

nthreads = 1
scheduler = 'synchronous'

use_temp_dir = os.getenv('USE_TEMP_ZARR')

cores = os.getenv('SLURM_CPUS_ON_NODE')
if cores is not None:
    cores = int(cores)
    nthreads = cores
if cores > 1:
    from dask.distributed import Client
    #scheduler = 'threads'
    nnodes = os.getenv('SLURM_JOB_NUM_NODES')
    nnodes = int(nnodes) if nnodes is not None else 1
    mem = os.getenv('SLURM_MEM_PER_NODE')
    if mem is not None:
        mem = f'{int(mem) // 1024}GB'
    client = Client(memory_limit=mem, processes=False,
                    n_workers=nnodes, threads_per_worker=cores)
    scheduler = client
    

print(f"Using {nthreads} threads with the {scheduler} scheduler")

spws = {3: range(4),
        6: range(7),}

suffix = '.image'

global then
then = time.time()
def dt():
    global then
    now = time.time()
    print(f"Elapsed: {now-then}")
    then = now

print("starting loops")

for band in (6,3):
    for config in ('12M', '7M12M'):
        for field in "G012.80 G328.25 G351.77 G327.29 G338.93 W51-E G353.41 G008.67 W43-MM2 G333.60 G337.92 W43-MM3 W43-MM1 G010.62 W51-IRS2".split():
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

                    if os.path.exists('collapse/stdspec/{0}'.format(fn.replace(suffix,"_std_spec.fits"))):
                        print(f"Found completed quicklooks for {fn}, skipping.")
                        continue

                    modfile = fn.replace(suffix, ".model")
                    if os.path.exists(modfile):
                        modcube = SpectralCube.read(modfile, format='casa_image', use_dask=True)
                        if nthreads > 1:
                            modcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        modcube.beam_threshold=100000

                    cube = SpectralCube.read(fn, format='casa_image', use_dask=True)
                    if nthreads > 1:
                        cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    cube.beam_threshold = 1
                    #cube.allow_huge_operations = True
                    mcube = cube.mask_out_bad_beams(0.1)
                    if nthreads > 1:
                        mcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    mcube.beam_threshold = 1

                    if use_temp_dir:
                        # create ZARRs of all the cubes

                        if 'modcube' in locals():
                            cubes = (cube, mcube, modcube)
                            tfs = [tempfile.mktemp(dir=use_temp_dir),
                                   tempfile.mktemp(dir=use_temp_dir),
                                   tempfile.mktemp(dir=use_temp_dir)]
                        else:
                            cubes = (cube, mcube, )
                            tfs = [tempfile.mktemp(dir=use_temp_dir),
                                   tempfile.mktemp(dir=use_temp_dir)]

                        print("Using temporary zarrs to store cubes: ")
                        for cb,tf in zip(cubes, tfs):
                            with dask.config.set(**cb._scheduler_kwargs):
                                cb._data.to_zarr(tf)
                            cb._data = da.from_zarr(tf)

                    print(mcube)
                    beam = mcube.beam if hasattr(mcube, 'beam') else mcube.average_beams(1)
                    cfrq = mcube.with_spectral_unit(u.GHz).spectral_axis.mean()
                    print(f"average beam={beam}")


                    dt()
                    print("Peak intensity")
                    mx = mcube.max(axis=0)#, how='slice')
                    mx_K = (mx*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mx_K.write('collapse/max/{0}'.format(fn.replace(suffix,"_max_K.fits")),
                               overwrite=True)
                    mx_K.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max_K.png")))
                    mx.write('collapse/max/{0}'.format(fn.replace(suffix,"_max.fits")),
                             overwrite=True)
                    mx.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max.png")))

                    dt()
                    print("Min intensity")
                    mn = mcube.min(axis=0)#, how='slice')
                    mn_K = (mn*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mn_K.write('collapse/min/{0}'.format(fn.replace(suffix,"_min_K.fits")),
                               overwrite=True)
                    mn_K.quicklook('collapse/min/pngs/{0}'.format(fn.replace(suffix,"_min_K.png")))


                    pl.clf()
                    dt()
                    print("Spatial max (peak spectrum)")
                    mxspec = mcube.max(axis=(1,2))#, how='slice')
                    mxspec.write("collapse/maxspec/{0}".format(fn.replace(suffix, "_max_spec.fits")), overwrite=True)
                    mxspec.quicklook("collapse/maxspec/pngs/{0}".format(fn.replace(suffix, "_max_spec.png")))
                    if os.path.exists(modfile):
                        mxmodspec = modcube.max(axis=(1,2))#, how='slice')
                        mxmodspec.write("collapse/maxspec/{0}".format(fn.replace(suffix, "_max_model_spec.fits")), overwrite=True)
                        mxmodspec.quicklook("collapse/maxspec/pngs/{0}".format(fn.replace(suffix, "_max_model_spec.png")))

                    dt(); print("Spatial mad_std")
                    pl.close('all')
                    pl.clf()
                    stdspec = mcube.mad_std(axis=(1,2))#, how='slice')
                    stdspec.write("collapse/stdspec/{0}".format(fn.replace(suffix, "_std_spec.fits")), overwrite=True)
                    stdspec.quicklook("collapse/stdspec/pngs/{0}".format(fn.replace(suffix, "_std_spec.png")))



                    for pct in (25,50,75):
                        dt()
                        print(f"{pct}th Percentile")
                        #pctmap = mcube.percentile(pct, axis=0, iterate_rays=True)
                        pctmap = mcube.percentile(pct, axis=0)
                        pctmap_K = (pctmap*u.beam).to(u.K,
                                                      u.brightness_temperature(beam_area=beam,
                                                                               frequency=cfrq))
                        pctmap_K.write('collapse/percentile/{0}'.format(fn.replace(suffix,"_{0}pct_K.fits".format(pct))),
                                       overwrite=True)
                        pctmap_K.quicklook('collapse/percentile/pngs/{0}'.format(fn.replace(suffix,"_{0}pct_K.png".format(pct))))

                    pl.close('all')
