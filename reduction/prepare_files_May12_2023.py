"""
Prepare files for dataverse

All files need headers updated
"""
import os

import glob

from astropy import units as u
from astropy.io import fits
from spectral_cube import SpectralCube

# assert this, don't change there, to minimize risk
assert os.getcwd() == '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'

multirowkeys = ('HISTORY', 'COMMENT')

failures = {}

for fn in glob.glob("*.JvM.image.pbcor.fits"):
    jvm = fits.open(fn, mode='update')
    try:
        if 'CREDIT' not in jvm[0].header:
            notjvm = SpectralCube.read(fn.replace(".JvM.", "."))
            print(fn)

            # if single-line cube, convert header to velocity
            if fn.count('spw') == 1: # line cubes, not full cubes
                print("Velocity-ifying")
                notjvm = notjvm.with_spectral_unit(u.km/u.s, velocity_convention='radio')

                # overwrite WCS
                jvm[0].header.update(notjvm.wcs.to_header())

            for key in notjvm.header:
                # don't overwrite any WCS though
                if key not in jvm[0].header and key not in multirowkeys:
                    jvm[0].header[key] = notjvm.header[key]
            for multirowkey in multirowkeys:
                if multirowkey in notjvm.header:
                    jvm[0].header[multirowkey] = ''
                    for row in notjvm.header[multirowkey]:
                        jvm[0].header[multirowkey] = row

            jvm[0].header['BUNIT'] = 'Jy/beam'
            jvm[0].header['CREDIT'] = 'Please cite Ginsburg et al 2022A&A...662A...9G when using these data, and Motte et al 2022A&A...662A...8M for the ALMA-IMF program'
            jvm[0].header['BIBCODE'] = '2022A&A...662A...9G'
            jvm[0].header['FILENAME'] = fn

            jvm.close()
    except Exception as ex:
        failures[fn] = ex
        print(ex)
