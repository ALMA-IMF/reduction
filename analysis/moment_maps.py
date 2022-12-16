"""
Moment maps!
"""
import numpy as np
import time
import warnings
from astropy.table import Table
from spectral_cube import SpectralCube
from astropy.io import fits
import dask
from astropy import units as u
from astropy import constants

import matplotlib
matplotlib.use('agg')

from statcont.cont_finding import c_sigmaclip_scube

import sys
sys.path.append('/orange/adamginsburg/ALMA_IMF/reduction/reduction')
import imaging_parameters

import glob

import tempfile

import os

# for zarr storage (we can just use local - it's faster)
#os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp'

default_lines = imaging_parameters.default_lines
default_lines['ch3cn_k3'] = 91.97146500*u.GHz

global
then = time.time()
def dt(message=""):
    global then
    now = time.time()
    dt(f"Elapsed: {now-then:0.1g}.  {message}", flush=True)
    then = now


def force_str(x):
    try:
        return x.decode()
    except AttributeError as ex:
        # numpy arrays are byte arrays.
        return str(x)

def get_size(start_path='.'):
    if start_path.endswith('fits'):
        return os.path.getsize(start_path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(force_str(start_path)):
        for f in filenames:
            f = force_str(f)
            dirpath = force_str(dirpath)
            fp = os.path.join(dirpath, f)
            assert type(fp) == str
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


if __name__ == "__main__":
    # need to be in main block for dask to work
    #from dask.distributed import Client
    #if os.getenv('SLURM_MEM_PER_NODE'):
    #    memlim_total = int(os.getenv('SLURM_MEM_PER_NODE')) / 1024 # GB
    #    ntasks = int(os.getenv('SLURM_NTASKS'))
    #    memlim = memlim_total / ntasks
    #    print(f"Memory limit is {memlim} GB")
    #else:
    #    memlim = 1
    #    ntasks = 8
    #client = Client(memory_limit=f'{memlim}GB', n_workers=ntasks)
    #nworkers = len(client.scheduler_info()['workers'])
    #print(f"Client scheduler info: {client.scheduler_info()['services']}")
    #print(f"Number of workers: {nworkers}  (should be equal to ntasks={ntasks})")
    #print(f"Client scheduler info: {client.scheduler_info()}")
    #print(f"Client vers: {client.get_versions(check=True)}")
    if os.getenv('ENVIRONMENT') == 'BATCH':
        pass
    else:
        from dask.diagnostics import ProgressBar
        pbar = ProgressBar()
        pbar.register()

    nthreads = os.getenv('SLURM_NTASKS')
    if nthreads is not None:
        nthreads = int(nthreads)
        dask.config.set(scheduler='threads')
    else:
        dask.config.set(scheduler='synchronous')

    scheduler = dask.config.get('scheduler')
    dt(f"Using {nthreads} threads with the {scheduler} scheduler", flush=True)

    #assert tempfile.gettempdir() == '/blue/adamginsburg/adamginsburg/tmp'

    redo = False

    basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'
    if not os.path.exists(f'{basepath}/moments'):
        os.mkdir(f'{basepath}/moments')
    if not os.path.exists(f'{basepath}/pvs'):
        os.mkdir(f'{basepath}/pvs')

    tbl = Table.read('/orange/adamginsburg/web/secure/ALMA-IMF/tables/cube_stats.ecsv')

    # simpler approach
    #sizes = {fn: get_size(fn) for fn in glob.glob(f"{basepath}/*_12M_spw[0-9].image")}
    #filenames = [f'{fn}.pbcor.fits'.replace('.image', '.JvM.image') for fn in tbl['filename']]
    filenames = [force_str(fn) for fn in tbl['filename']]

    # use tbl, ignore 7m12m
    sizes = {ii: get_size(force_str(fn))
             for ii, fn in enumerate(filenames)
             if '_12M_spw' in fn and os.path.exists(force_str(fn))
            } # ignore 7m12m


    target_chunk_size = int(1e8)
    for ii in sorted(sizes, key=lambda x: sizes[x]):

        fn = filenames[ii]
        basefn = os.path.basename(fn)

        outfn = fn.replace(".fits","")+'.statcont.cont.fits'
        assert outfn.count('.fits') == 1

        if not os.path.exists(outfn) or redo:
            t0 = time.time()

            # touch the file to allow parallel runs
            with open(outfn, 'w') as fh:
                fh.write("")

            dt(f"{fn}->{outfn}, size={sizes[ii]/1024**3} GB", flush=True)

            dt(f"Target chunk size is {target_chunk_size}", flush=True)
            cube = SpectralCube.read(fn, target_chunk_size=target_chunk_size, use_dask=True)


            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with cube.use_dask_scheduler('threads', num_workers=nthreads):
                    dt("Calculating noise", flush=True)
                    if ii < len(tbl):
                        noise = tbl['std'].quantity[ii]
                    else:
                        noise = cube.std()

                    dt("Sigma clipping", flush=True)
                    result = c_sigmaclip_scube(cube, noise,
                                               verbose=True,
                                               save_to_tmp_dir=True)
                    dt("Running the compute step", flush=True)
                    data_to_write = result[1].compute()

                    dt(f"Writing to FITS {outfn}", flush=True)
                    fits.PrimaryHDU(data=data_to_write.value,
                                    header=cube[0].header).writeto(outfn,
                                                                   overwrite=True)
                    cont = data_to_write.value
            dt(f"{fn} -> {outfn} in {time.time()-t0}s", flush=True)

        else:
            try:
                cont = fits.getdata(outfn)
            except Exception as ex:
                dt(ex, flush=True)
                continue
            dt(f"{fn} is done, loaded {outfn}", flush=True)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # do moments
            cube = SpectralCube.read(fn, target_chunk_size=target_chunk_size, use_dask=True)
            cube.allow_huge_operations=True
            with cube.use_dask_scheduler('threads', num_workers=nthreads):
                scube = cube - cont*cube.unit

                for field,restvel in imaging_parameters.field_vlsr.items():
                    if field in fn:
                        restvel = u.Quantity(restvel)
                        break

                for line,frq in default_lines.items():
                    frq = u.Quantity(frq)
                    zz = (restvel / constants.c).decompose().value

                    if frq * (1-zz) > cube.spectral_axis.min() and frq * (1-zz) < cube.spectral_axis.max():
                        dt(f"Moment mapping {line} at {frq}", flush=True)
                        outmoment = f'{basepath}/moments/{field}/{basefn}.{line}.m0.fits'
                        if (not os.path.exists(outmoment)) or redo:

                            vcube = scube.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=frq)
                            cutout = vcube.spectral_slab(restvel-10*u.km/u.s, restvel+10*u.km/u.s)
                            assert cutout.shape[0] > 1
                            mom0 = cutout.moment0()
                            assert not np.all(mom0[np.isfinite(mom0)] == 0)
                            if not os.path.exists(f'{basepath}/moments/{field}'):
                                os.mkdir(f'{basepath}/moments/{field}')
                            mom0.write(outmoment, overwrite=True)

                        # PNGs are made in PVDiagramPNGs.ipynb
                        dt(f"PV mapping {line} at {frq}", flush=True)
                        outpv = f'{basepath}/pvs/{field}/{basefn}.{line}.pv_ra.fits'
                        if (not os.path.exists(outpv)) or redo:

                            vcube = scube.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=frq)
                            cutout = vcube.spectral_slab(restvel-50*u.km/u.s, restvel+50*u.km/u.s)
                            assert cutout.shape[0] > 1
                            pvra = cutout.mean(axis=1)
                            assert not np.all(pvra[np.isfinite(pvra)] == 0)
                            if not os.path.exists(f'{basepath}/pvs/{field}'):
                                os.mkdir(f'{basepath}/pvs/{field}')
                            pvra.write(outpv, overwrite=True)
                        outpv = f'{basepath}/pvs/{field}/{basefn}.{line}.pv_dec.fits'
                        if (not os.path.exists(outpv)) or redo:

                            vcube = scube.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=frq)
                            cutout = vcube.spectral_slab(restvel-50*u.km/u.s, restvel+50*u.km/u.s)
                            assert cutout.shape[0] > 1
                            pvdec = cutout.mean(axis=2)
                            assert not np.all(pvdec[np.isfinite(pvdec)] == 0)
                            if not os.path.exists(f'{basepath}/pvs/{field}'):
                                os.mkdir(f'{basepath}/pvs/{field}')
                            pvdec.write(outpv, overwrite=True)
