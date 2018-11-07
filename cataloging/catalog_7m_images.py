"""
This script runs a cataloging tool on the ALMA-IMF 7m array 3mm data for
comparison to MGPS data
"""
import numpy as np

from dendrocat import RadioSource, MasterCatalog
from dendrocat.utils import match
from dendrocat.aperture import Circle, Annulus


from spectral_cube import SpectralCube
from radio_beam import Beam

from astropy.io import fits
from astropy import units as u
from astropy import stats
from astropy.convolution import convolve_fft

import reproject

data_map = {'W43': {'MGPS': 'GAL031_5pass_1_.0.2_10mJy_10mJy_final.fits',
                    'ALMA': ['member.uid___A001_X1296_X133.W43-MM3_sci.spw{0}.mfs.I.pbcor.fits',
                             'member.uid___A001_X1296_X1b1.W43-MM1_sci.spw{0}.mfs.I.pbcor.fits',
                             'member.uid___A001_X1296_X11f.W43-MM2_sci.spw{0}.mfs.I.pbcor.fits',]
                   },
            'W51': {'MGPS': 'W51_5pass_1_.0.2_10mJy_10mJy_final.fits',
                    'ALMA': ['member.uid___A001_X1296_X193.W51-IRS2_sci.spw{0}.mfs.I.pbcor.fits',
                             'member.uid___A001_X1296_X10b.W51-E_sci.spw{0}.mfs.I.pbcor.fits',
                            ],
                   },
            'W33': {'MGPS': 'W33_5pass_1_.0.2_10mJy_10mJy_final.fits',
                    'ALMA': ['member.uid___A001_X1296_X1fb._G012.80__sci.spw{0}.mfs.I.pbcor.fits'],
                   },
           }

basedir = {'ALMA': '/Volumes/external/almaimf/',
           'MGPS': '/Volumes/external/mgps/nov6_2018',
          }

# for the 3mm data
beam = Beam(20*u.arcsec)

for field in data_map:

    objects = {}
    data_map[field]['objects'] = objects
    for almafield in data_map[field]['ALMA']:
        name = almafield.split("_")[5]
        for spw in range(16, 23, 2):
            cube = SpectralCube.read('{0}/{1}'.format(basedir['ALMA'],
                                                      almafield.format(spw),
                                                     ))
            cubesm = cube.convolve_to(beam)

            source_object = RadioSource([cubesm.hdu])

            std = cubesm.mad_std().value
            source_object.to_dendrogram(min_value=std*2, min_delta=std, min_npix=cubesm.pixels_per_beam/5,)
            source_object.to_catalog()
            objects[(name,spw)] = source_object


        fh = fits.open('{0}/{1}'.format(basedir['MGPS'], data_map[field]['MGPS']))
        cutout,_ = reproject.reproject_interp(fh, cubesm[0,:,:].header)
        cutout_sm = convolve_fft(cutout, Beam(20*u.arcsec).deconvolve(Beam(10*u.arcsec)).as_kernel(source_object.pixel_scale))
        cropped_mgps = fits.PrimaryHDU(data=cutout_sm, header=cubesm[0,:,:].header)
        cropped_mgps.header['CRVAL3'] = fh[0].header['REFFREQ']
        cropped_mgps.header['REFFREQ'] = fh[0].header['REFFREQ']
        cropped_mgps.header['TELESCOP'] = 'GBT'
        mgps = RadioSource([cropped_mgps])
        mgps.nu = fh[0].header['REFFREQ']*u.Hz
        mgps.freq_id = '91.5GHz'
        mgps.beam = Beam(20*u.arcsec)
        mgps.set_metadata()
        std = stats.mad_std(mgps.data, ignore_nan=True)
        mgps.to_dendrogram(min_value=std*4, min_delta=std, min_npix=10)
        mgps.to_catalog()
        objects[(name,'MGPS')] = mgps

    matched = match(*list(objects.values()), verbose=True, threshold=10*u.arcsec)

    fixed_circle = Circle([0, 0], 20*u.arcsec, name='fixedcirc')
    matched.photometer(fixed_circle)

    data_map[field]['matched'] = matched

    freqs = u.Quantity([u.Quantity(x.split("_")[0]) for x in matched.catalog.colnames if '_dend_flux' in x])
    cns = [x for x in matched.catalog.colnames if '_dend_flux' in x]
    cns = [x for x in matched.catalog.colnames if '_fixedcirc_sum' in x]
    cns = [x for x in matched.catalog.colnames if '_fixedcirc_peak' in x]
    rmscns = [x for x in matched.catalog.colnames if '_fixedcirc_rms' in x]

    fluxes = matched.catalog[cns].as_array().view('float64').reshape(len(matched.catalog), len(cns)).T
    errors = matched.catalog[rmscns].as_array().view('float64').reshape(len(matched.catalog), len(cns)).T

    import pylab as pl
    pl.figure(1).clf()
    inds = np.argsort(freqs)
    for ii in range(fluxes.shape[1]):
        pl.errorbar(freqs[inds].value, fluxes[inds,ii], yerr=errors[inds,ii], marker='o', linestyle='-')
    pl.xlabel("Frequency (GHz)")
    pl.ylabel("Flux Density (Jy/beam)")
    pl.title(field)
    pl.savefig('/Users/adam/work/mgps/almaimf_comparison/{0}_fluxcompare.pdf'.format(field))

    names = set([k[0] for k in objects if 'MGPS' not in k])
    for ii, name in enumerate(names):
        pl.figure(2+ii).clf()
        ax1 = pl.subplot(2,3,1, projection=objects[(name, 16)].wcs)
        ax1.imshow(objects[(name, 16)].data)

        ax2 = pl.subplot(2,3,2, projection=objects[(name, 18)].wcs)
        ax2.imshow(objects[(name, 18)].data)

        ax3 = pl.subplot(2,3,4, projection=objects[(name, 20)].wcs)
        ax3.imshow(objects[(name, 20)].data)

        ax4 = pl.subplot(2,3,5, projection=objects[(name, 22)].wcs)
        ax4.imshow(objects[(name, 22)].data)

        ax5 = pl.subplot(1,3,3, projection=objects[(name, 'MGPS')].wcs)
        ax5.imshow(objects[(name, 'MGPS')].data)

        for ax in (ax1,ax2,ax3,ax4,ax5):
            ax.plot(objects[(name, 'MGPS')].catalog['x_cen'], objects[(name, 'MGPS')].catalog['y_cen'], 'wx', transform=ax.get_transform('world'))

        pl.suptitle(name)
        pl.savefig('/Users/adam/work/mgps/almaimf_comparison/{0}_{1}_catalog_overlay.pdf'.format(field, name))
