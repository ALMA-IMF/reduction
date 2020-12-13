import numpy as np
import json
import os
import radio_beam
import reproject
from astropy import constants, units as u, table, stats, coordinates, wcs, log
from astropy.io import fits
from spectral_cube import SpectralCube, wcs_utils, tests, Projection, OneDSpectrum
from astropy.nddata import Cutout2D
from parse_contdotdat import parse_contdotdat

import tempfile

import pylab as pl
pl.ioff()

overwrite=False



# for zarr storage
os.environ['TMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp'

if __name__ == "__main__":
    # need to be in main block for dask to work
    from dask.distributed import Client
    if os.getenv('SLURM_MEM_PER_NODE'):
        memlim_total = int(os.getenv('SLURM_MEM_PER_NODE')) / 1024 # GB
        ntasks = int(os.getenv('SLURM_NTASKS'))
        memlim = memlim_total / ntasks
    else:
        memlim = 1
        ntasks = 8
    client = Client(memory_limit=f'{memlim}GB', n_workers=ntasks)
    nworkers = len(client.scheduler_info()['workers'])
    print(f"Client schedular info: {client.scheduler_info()['services']}")
    print(f"Number of workers: {nworkers}")
    print(f"Client schedular info: {client.scheduler_info()}")
    print(f"Client vers: {client.get_versions(check=True)}")
    if os.getenv('ENVIRONMENT') == 'BATCH':
        pass
    else:
        from dask.diagnostics import ProgressBar
        pbar = ProgressBar()
        pbar.register()

    assert tempfile.gettempdir() == '/blue/adamginsburg/adamginsburg/tmp'


    array = '12M'

    basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'
    os.chdir(f'{basepath}/imaging_results')

    with open(f'{basepath}/metadata.json', 'r') as fh:
        metadata = json.load(fh)



    for robust in (0,):
        ftemplate = '{field}_{band}_spw{spw}_{array}{suffix}_spw{spw}.image.fits'

        for band,suffix in (
                            ('B3', '',),
                            ('B6', '',),
                            ('B3', '_lines',),
                            ('B6', '_lines',),
                            ('B3', '_lines.contsub',),
                            ('B6', '_lines.contsub',),
                           ):
            for field in "G353.41 G008.67 G337.92 W51-E W43-MM3 G328.25 G351.77 W43-MM1 G010.62 W51-IRS2 G012.80 G333.60 W43-MM2 G327.29 G338.93".split():


                for spw in (0,1,2,3,4,5,6,7):
                    filename = ftemplate.format(spw=spw, field=field, band=band,
                                                array=array,
                                                suffix=suffix, robust=robust,
                                                )

                    if os.path.exists(filename):
                        cube = SpectralCube.read(filename,
                                                 use_dask=True).with_spectral_unit(u.GHz)
                    elif os.path.exists(filename[:-5]):
                        cube = SpectralCube.read(filename[:-5], format='casa_image',
                                                 use_dask=True).with_spectral_unit(u.GHz)
                    else:
                        log.exception("File {0} does not exist".format(filename))
                        if os.path.exists(filename[:-5]):
                            log.exception("But {0} does!!!!".format(filename[:-5]))
                        continue

                    for operation in ('mean', 'max', 'median'):
                        out_fn = f'spectra/{field}_{array}_{band}_spw{spw}_robust{robust}{suffix}.{operation}spec.fits'
                        if overwrite or not os.path.exists(out_fn):
                            spec = getattr(cube, operation)(axis=(1,2))
                            spec.write(out_fn, overwrite=overwrite)

                        spec_jy = OneDSpectrum.from_hdu(fits.open(out_fn)).with_spectral_unit(u.GHz)
                        if cube.shape[0] != spec_jy.size:
                            spec_jy = getattr(cube, operation)(axis=(1,2))
                            spec_jy.write(out_fn, overwrite=True)

                        jtok = cube.jtok_factors()
                        spec_K = spec_jy * jtok*u.K / (u.Jy/u.beam)

                        for spec, unit in zip((spec_jy, spec_K), ("", "K")):
                            fig_fn = f'spectra/pngs/{field}_{array}_{band}_spw{spw}_robust{robust}{suffix}{unit}.{operation}spec.png'
                            pl.clf()
                            spec.quicklook(filename=fig_fn, color='k',
                                           linewidth=0.9, drawstyle='steps-mid')
                            sel = np.zeros(spec.size, dtype='int')


                            muid = metadata[band][field]['muid_configs']['12Mshort']
                            cdatfile = metadata[band][field]['cont.dat'][muid]
                            contfreqs = parse_contdotdat(cdatfile)

                            for freqrange in contfreqs.split(";"):
                                low,high = freqrange.split("~")
                                high = u.Quantity(high)
                                low = u.Quantity(low, unit=high.unit)
                                sel += (spec.spectral_axis > low) & (spec.spectral_axis < high)
                                #print(f"{field}_{spw}: {low}-{high} count={sel.sum()}")

                            usel = np.unique(sel)
                            # 0 means 'not included in any windows', 1 means 'included in 1 window'
                            # 2 or more means included in 2 or more.
                            # The cases addressed here are:
                            # {0,1}: some continuum, some not
                            # {1}: all continuum
                            # {0,1,2,...} or {1,2,...}: some or all continuum, at least one pixel twice or more
                            if set(usel) in ({0, 1}, {1}):
                                sel = sel.astype('bool')

                                dat_to_plot = spec.value.copy()
                                dat_to_plot[~sel] = np.nan
                                pl.plot(spec.spectral_axis, dat_to_plot, linewidth=4,
                                        zorder=-5, alpha=0.75, color='orange')
                            elif len(usel) > 1:
                                dat_to_plot = np.empty(spec.value.shape)
                                dat_to_plot[:] = np.nan
                                # skip zero
                                for selval in usel[1:]:
                                    dat_to_plot[sel == selval] = spec.value[sel == selval]
                                pl.plot(spec.spectral_axis, dat_to_plot, linewidth=4,
                                        zorder=selval-10, alpha=0.75, color='orange')
                            else:
                                log.error(f"No selected continuum for {field}_{array}_{band}_spw{spw}_robust{robust}.{operation}: {sel.sum()} {usel}")
                                continue
                            print(f"{field}_{array}_{band}_spw{spw}_robust{robust}.{operation}: {sel.sum()} {usel}")
                            pl.title(f"{field} {array} {band} spw{spw} robust{robust}{suffix} {operation}")
                            pl.savefig(fig_fn, bbox_inches='tight')
