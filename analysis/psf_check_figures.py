import glob
import os
from astropy import units as u
from astropy import log

from pathlib import Path

from imstats import get_psf_secondpeak

import pylab as pl

releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/June2021Release')

if not os.path.exists(releasepath / 'figures'):
    os.mkdir(releasepath / 'figures')

pl.close('all')

for jj, band in enumerate(('B3', 'B6')):
    fig = pl.figure(jj, figsize=(15, 8))
    fig.clf()
    fig.suptitle(band)

    for ii, field in enumerate(sorted("G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split())):


        imtype,itgl = 'cleanest', 'continuum_merged_12M'

        itpath = releasepath / field / band / imtype
        suffix = 'psf.tt0'

        globstr = (f"{field}*_{band}_*{itgl}_robust0_*selfcal[0-9]*finaliter.{suffix}")

        files = glob.glob(str(itpath / globstr))
        if len(files) > 1:
            raise ValueError("Too many files")
        elif len(files) == 0:
            if field == 'W43-MM1' and band == 'B6':
                raise ValueError("W43-MM1 is still missing! (but it should exist now)")
            else:
                raise ValueError("Not enough files")

        psffn = files[0]

        ax = pl.subplot(3, 5, ii+1)
        ax.set_title(field)
        log.info(f"{field} {band}")
        (psf_secondpeak, psf_secondpeak_loc, psf_sidelobe1_fraction, (rr, cutout, view, bmfit_residual)) = \
                get_psf_secondpeak(psffn, show_image=True, min_radial_extent=2.5*u.arcsec,
                           max_radial_extent=5*u.arcsec
                          )

        if ii not in (0, 5, 10):
            ax.set_ylabel("")
        if ii < 10:
            ax.set_xlabel("")


    pl.subplots_adjust(wspace=0.32)
    pl.tight_layout()
    fig.savefig(releasepath / f'figures/{band}_psfs.png', bbox_inches='tight', dpi=300)
    fig.savefig(releasepath / f'figures/{band}_psfs.pdf', bbox_inches='tight')
