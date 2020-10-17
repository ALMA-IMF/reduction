import numpy as np
import json
import os
import radio_beam
import reproject
from astropy import constants, units as u, table, stats, coordinates, wcs, log
from astropy.io import fits
from spectral_cube import SpectralCube, wcs_utils, tests, Projection, OneDSpectrum
from astropy.nddata import Cutout2D

import pylab as pl
pl.ioff()

array = '12M'

with open('../metadata.json', 'r') as fh:
    metadata = json.load(fh)

def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)



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
                    cube = SpectralCube.read(filename)
                else:
                    log.exception("File {0} does not exist".format(filename))
                    if os.path.exists(filename[:-5]):
                        log.exception("But {0} does!!!!".format(filename[:-5]))
                    continue

                for operation in ('mean', 'max', 'median'):
                    out_fn = f'spectra/{field}_{array}_{band}_spw{spw}_robust{robust}{suffix}.{operation}spec.fits'
                    if not os.path.exists(out_fn):
                        spec = cube.apply_numpy_function(getattr(np, 'nan'+operation),
                                                         axis=(1,2),
                                                         progressbar=True,
                                                         projection=True,
                                                         how='slice',
                                                         unit=cube.unit,
                                                        )
                        spec.write(out_fn)

                    spec = OneDSpectrum.from_hdu(fits.open(out_fn))


                    fig_fn = f'spectra/pngs/{field}_{array}_{band}_spw{spw}_robust{robust}{suffix}.{operation}spec.png'
                    pl.clf()
                    spec.quicklook(filename=fig_fn)
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
                    if set(usel) == {0,1}:
                        sel = sel.astype('bool')

                        dat_to_plot = spec.value.copy()
                        dat_to_plot[~sel] = np.nan
                        pl.plot(spec.spectral_axis, dat_to_plot, linewidth=4,
                                zorder=-5, alpha=0.75)
                    else:
                        dat_to_plot = np.empty(spec.value.shape)
                        dat_to_plot[:] = np.nan
                        # skip zero
                        for selval in usel[1:]:
                            dat_to_plot[sel == selval] = spec.value[sel == selval]
                        pl.plot(spec.spectral_axis, dat_to_plot, linewidth=4,
                                zorder=selval-10, alpha=0.75, color='orange')
                    print(f"{field}_{array}_{band}_spw{spw}_robust{robust}.{operation}: {sel.sum()} {usel}")
                    pl.title(f"{field}_{array}_{band}_spw{spw}_robust{robust}{suffix}.{operation}")
                    pl.savefig(fig_fn)
