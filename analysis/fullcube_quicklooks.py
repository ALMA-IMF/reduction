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
from pathlib import Path
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
os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

nnodes = int(os.getenv('SLURM_JOB_NUM_NODES') or os.getenv('SLURM_NNODES') or 1)
nthreads = int(os.getenv('SLURM_STEP_NUM_TASKS') or os.getenv('SLURM_NTASKS') or 1)

if nnodes > 2:
    from dask.distributed import Client, LocalCluster
    from dask_jobqueue import SLURMCluster

    ntasks_per_node = int(os.getenv('SLURM_TASKS_PER_NODE').split("(")[0])

    mem = os.getenv('SLURM_MEM_PER_NODE')
    if mem is not None:
        mem = f'{int(mem) // 1024}GB'

    cluster = LocalCluster(n_workers=nnodes,
                           threads_per_worker=ntasks_per_node,
                           memory_limit=mem)
    client = Client(cluster)
    client.start_workers(8)
    scheduler = dask.config.get('scheduler')
    print(f"Using scheduler {scheduler} with {nnodes} nodes and {ntasks_per_node} cores per node")
elif nthreads is not None:
    dask.config.set(scheduler='threads')
    scheduler = dask.config.get('scheduler')
    print(f"Using {nthreads} threads with the {scheduler} scheduler")
else:
    scheduler = dask.config.get('scheduler')
    print(f"Using {nthreads} threads with the {scheduler} scheduler")

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

print("starting loops")

redo = True
redo = False

for band in (3,6):
    for config in ('12M',):# '7M12M'):
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

                    if not redo and os.path.exists('collapse/argmaxspec/{0}'.format(fn.replace(suffix,"_argmaxspec_spec.fits"))):
                        print(f"Found completed quicklooks for {fn}, skipping.")
                        continue

                    modfile = fn.replace(suffix, ".model")
                    if os.path.exists(modfile):
                        if os.path.exists(modfile+".fits"):
                            modcube = SpectralCube.read(modfile+".fits", format='fits', use_dask=True)
                        else:
                            modcube = SpectralCube.read(modfile, format='casa_image', use_dask=True)
                            modcube = modcube.rechunk()

                        if nthreads > 1:
                            modcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        modcube.beam_threshold=100000

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", format='fits', use_dask=True)
                    else:
                        cube = SpectralCube.read(fn, format='casa_image', use_dask=True)
                        cube = cube.rechunk()
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
                            print(f"Dumping cube {cb}\n to tempfile {tf}\n"
                                  f" with scheduler args {cb._scheduler_kwargs}\n"
                                  f" and data {cb._data}")
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
                    mx_K =  (mx*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mx_K.write('collapse/max/{0}'.format(fn.replace(suffix,"_max_K.fits")),
                               overwrite=True)
                    mx_K.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max_K.png")))
                    mx.write('collapse/max/{0}'.format(fn.replace(suffix,"_max.fits")),
                             overwrite=True)
                    mx.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max.png")))

                    max_loc = np.unravel_index(np.nanargmax(mx_K), mx_K.shape)
                    print(f"max_loc={max_loc}")

                    dt()
                    print("Min intensity")
                    mn = mcube.min(axis=0)#, how='slice')
                    mn_K = (mn*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mn_K.write('collapse/min/{0}'.format(fn.replace(suffix,"_min_K.fits")),
                               overwrite=True)
                    mn_K.quicklook('collapse/min/pngs/{0}'.format(fn.replace(suffix,"_min_K.png")))


                    if hasattr(cube, 'beams'):
                        print("Beams")
                        pl.clf()
                        dt()
                        beams = mcube.beams
                        pl.plot(cube.spectral_axis, beams.major.value, label='major')
                        pl.plot(cube.spectral_axis, beams.minor.value, label='minor')
                        pl.savefig("collapse/beams/pngs/{0}".format(fn.replace(suffix, "_beams.png")), bbox_inches='tight')

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

                    pl.clf()
                    dt()
                    print("Spectrum at max loc")
                    mxspec = mcube[:,max_loc[0], max_loc[1]]
                    mxspec.write("collapse/argmaxspec/{0}".format(fn.replace(suffix, "_argmax_spec.fits")), overwrite=True)
                    mxspec.quicklook("collapse/argmaxspec/pngs/{0}".format(fn.replace(suffix, "_argmax_spec.png")))
                    if os.path.exists(modfile):
                        mxmodspec = modcube[:,max_loc[0], max_loc[1]]
                        mxmodspec.write("collapse/argmaxspec/{0}".format(fn.replace(suffix, "_argmax_model_spec.fits")), overwrite=True)
                        mxmodspec.quicklook("collapse/argmaxspec/pngs/{0}".format(fn.replace(suffix, "_argmax_model_spec.png")))


                    dt(); print("Spatial mad_std")
                    pl.close('all')
                    pl.clf()
                    rcmcube = mcube.rechunk([16,'auto','auto'])
                    print(rcmcube)
                    stdspec = rcmcube.mad_std(axis=(1,2))#, how='slice')
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

os.chdir(cwd)
