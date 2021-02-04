import os
import glob
import numpy as np
import reproject
from astropy.io import fits
from astropy.wcs import WCS

from astropy.visualization import simple_norm
import pylab as pl
pl.rcParams['font.size'] = 14

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults'

cutoutinfo = {'W51-IRS2': {'norm_kwargs': {'min_percent': 0.1, 'max_percent': 99.9, 'stretch': 'asinh'}, 'cutout_lims': [slice(1000,2800), slice(1000,2800)]},
              'G327.29': {'norm_kwargs': {},
                          'norm_b6': {'clip': True, 'min_percent': 50, 'max_percent': 99.95, 'stretch': 'log'},
                          'norm_combo': {'clip': True, 'min_percent': 50, 'max_percent': 99.95, 'stretch': 'log'},
                          'norm_b3': {'clip': True, 'min_percent': 50, 'max_percent': 99.95, 'stretch': 'log'},
                          'cutout_lims': [slice(1200,2200), slice(900,1900)]},
             }


#for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
for field in ("G327.29",):
    #for imtype in ('cleanest', 'bsens', '7m12m', ):
    for imtype in ('cleanest',):

        #pl.close('all')
        pl.figure(1).clf()

        b3path = glob.glob(f'{basepath}/{field}/B3/{imtype}/*robust0_*finaliter.image.tt0.fits')
        b6path = glob.glob(f'{basepath}/{field}/B6/{imtype}/*robust0_*finaliter.image.tt0.fits')
        if len(b3path) == 1:
            b3path = b3path[0]
        else:
            continue
        if len(b6path) == 1:
            b6path = b6path[0]
        else:
            continue

        try:
            fh_b3 = fits.open(b3path)
            fh_b6 = fits.open(b6path)
        except Exception as ex:
            print(ex)

        b3wcs = WCS(fh_b3[0].header).celestial
        b6_proj_to_b3,covg = reproject.reproject_interp((fh_b6[0].data.squeeze(),
                                                         WCS(fh_b6[0].header).celestial),
                                                        b3wcs,
                                                        shape_out=fh_b3[0].data.squeeze().shape)

        b3_plus_b6 = (fh_b3[0].data+b6_proj_to_b3)

        norm_b6 = {}
        norm_combo = {}
        norm_b3 = {}

        if field in cutoutinfo and 'norm_b3' in cutoutinfo[field]:
            norm_b3.update(cutoutinfo[field]['norm_b3'])
        if field in cutoutinfo and 'norm_b6' in cutoutinfo[field]:
            norm_b6.update(cutoutinfo[field]['norm_b6'])
        if field in cutoutinfo and 'norm_combo' in cutoutinfo[field]:
            norm_combo.update(cutoutinfo[field]['norm_combo'])

        imgc = (np.array([simple_norm(b6_proj_to_b3, **norm_b6)(b6_proj_to_b3),
                          simple_norm(b3_plus_b6.squeeze(), **norm_combo)(b3_plus_b6.squeeze()),
                          simple_norm(fh_b3[0].data.squeeze(), **norm_b3)(fh_b3[0].data.squeeze())
                         ]))

        if field in cutoutinfo and 'cutout_lims' in cutoutinfo[field]:
            slicex, slicey = cutoutinfo[field]['cutout_lims']
            imgcc = imgc[:, slicey, slicex]

        else:
            zrx = imgc.shape[2] // 5
            zry = imgc.shape[1] // 5

            imgcc = imgc[:, zry:-zry, zrx:-zrx]

        if field in cutoutinfo and 'norm_kwargs' in cutoutinfo[field]:
            img = simple_norm(imgcc, **cutoutinfo[field]['norm_kwargs'])(imgcc.T.swapaxes(0,1))
        else:
            img = simple_norm(imgcc, min_percent=0.1, max_percent=99.9, stretch='asinh')(imgcc.T.swapaxes(0,1))
        img[~np.isfinite(img)] = 0

        pl.imshow(1-img, origin='lower')
        pl.xticks([])
        pl.yticks([])

        if not os.path.exists(f'{basepath}/{field}/continuum_colorcomposites'):
            os.mkdir(f'{basepath}/{field}/continuum_colorcomposites')
        pl.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_colorcomposite.pdf', bbox_inches='tight')
        pl.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_colorcomposite.png', bbox_inches='tight', dpi=300)

        if field == 'G327.29':

            fig2 = pl.figure(2)
            fig2.clf()
            ax = fig2.add_subplot(projection=b3wcs[slicey, slicex])
            im = ax.imshow(fh_b3[0].data.squeeze()[slicey, slicex]*1e3,
                           cmap='gray_r',
                           norm=simple_norm(fh_b3[0].data.squeeze()[slicey,
                                                                    slicex]*1e3,
                                            max_percent=99.95, stretch='asinh',
                                            min_percent=20),)
            cb = fig2.colorbar(mappable=im)
            cb.set_label("$S_\\nu$ [mJy/beam]")
            ax.contour(b6_proj_to_b3[slicey, slicex], levels=[3.e-3, 2.e-2],
                       colors=['orange', 'red'],
                       linewidths=0.65,
                      )
            ax.set_xlabel('Right Ascension')
            ax.set_ylabel('Declination')

            fig2.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_contourcomposite.pdf', bbox_inches='tight')
            fig2.savefig(f'{basepath}/{field}/continuum_colorcomposites/{field}_{imtype}_B3_B6_contourcomposite.png', bbox_inches='tight', dpi=300)
