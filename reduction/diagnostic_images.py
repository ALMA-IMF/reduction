import os
from spectral_cube import SpectralCube
import numpy as np
from functools import reduce
import pylab as pl
from astropy import visualization
from astropy import units as u

imnames = ['image', 'model', 'residual']

def load_images(basename, suffix=None, crop=True):
    import warnings

    sfx = '.fits' if '.fits' in suffix else ''

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cubes = {imn: SpectralCube.read('{basename}.{imn}.tt0{suffix}'.format(**locals()),
                                        format='fits' if 'fits' in sfx else 'casa_image')
                 for imn in imnames
                 if os.path.exists('{basename}.{imn}.tt0{suffix}'.format(**locals()))
                }


    assert hasattr(cubes['image'], 'beam'), "No beam found in cube!"
    assert hasattr(cubes['image'], 'pixels_per_beam'), "No beam found in cube!"

    # catch some whack errors...
    for key in cubes:
        if cubes[key].spectral_axis.unit != cubes['image'].spectral_axis.unit:
            cubes[key] = cubes[key].with_spectral_unit(cubes['image'].spectral_axis.unit)

    if os.path.exists('{basename}.pb.tt0{suffix}'.format(**locals())):
        pb = SpectralCube.read('{basename}.pb.tt0{suffix}'.format(**locals()),
                               format='fits' if 'fits' in suffix else 'casa_image')

        # pb can have a bad CD in its wcs, but that CD is totally
        # irrelevant in most cases
        # this is unfortunately a hack
        if pb.shape == cubes['image'].shape:
            if pb.wcs.wcs.cdelt[-1] != cubes['image'].wcs.wcs.cdelt[-1]:
                pb._wcs.wcs.cdelt[-1] = cubes['image'].wcs.wcs.cdelt[-1]
                pb._wcs.wcs.crval[-1] = cubes['image'].wcs.wcs.crval[-1]
                pb._wcs.wcs.cunit[-1] = cubes['image'].wcs.wcs.cunit[-1]
                pb._wcs.wcs.ctype[-1] = cubes['image'].wcs.wcs.ctype[-1]


        #masks = [cube != 0 * cube.unit for cube in cubes.values()]
        #include_mask = reduce(lambda x,y: x or y, masks)
        #include_mask = cubes['residual'] != 0*cubes['residual'].unit
        include_mask = pb > 0.05*pb.unit

        cubes['pb'] = pb
    else:
        include_mask = None

    if include_mask is not None:
        mcubes = {imn: (cubes[imn]
                        .with_mask(include_mask)
                        .with_mask(cubes[imn] != 0*cubes[imn].unit))
                  for imn in cubes}
    else:
        mcubes = cubes

    # base the cropping off of the image
    if crop:
        view = mcubes['image'].subcube_slices_from_mask(mcubes['image'].mask)
    else:
        view = (slice(None),)*3

    imgs = {imn:
            mcubes[imn][view][0]
            if crop else
            mcubes[imn][0]
            for imn in imnames
            if imn in mcubes}


    try:
        casamask = SpectralCube.read('{basename}.mask{suffix}'.format(**locals()),
                                     format='fits' if 'fits' in suffix else 'casa_image')
        cubes['mask'] = casamask
        if include_mask is not None:
            imgs['mask'] = (cubes['mask'].with_mask(include_mask).minimal_subcube()[0]
                            if crop else
                            cubes['mask'].with_mask(include_mask)[0])
        else:
            imgs['mask'] = cubes['mask'][0]
    except (AssertionError,OSError,IOError):
        # this implies there is no mask
        pass

    imgs['includemask'] = include_mask # the mask applied to the cube

    if 'model' in imgs:
        # give up on the 'Slice' nature so we can change units
        imgs['model'] = imgs['model'].quantity * cubes['image'].pixels_per_beam * u.pix / u.beam

    return imgs, cubes

asinhn = visualization.ImageNormalize(stretch=visualization.AsinhStretch())

def show(imgs, zoom=None, clear=True, norm=asinhn,
         imnames_toplot=('mask', 'model', 'image', 'residual'),
         **kwargs):

    if clear:
        pl.clf()

    if 'mask' not in imgs:
        imnames_toplot = list(imnames_toplot)
        imnames_toplot.remove('mask')

    # filter out things that weren't found in images
    # (this makes the code below robust, as in it won't fail, but it can defeat
    # the purpose of this code if that goal is to make plots of multiple
    # images)
    imnames_toplot = [x for x in imnames_toplot
                      if x in imgs]

    for ii,imn in enumerate(imnames_toplot):
        ax = pl.subplot(1, len(imnames_toplot), ii+1)

        if np.isscalar(zoom):
            shp = imgs[imn].shape
            view = [slice(int((-ss*zoom + ss)/2),
                          int((ss*zoom + ss)/2))
                    for ss in shp]
        elif zoom is None:
            view = [slice(None), slice(None)]
        else:
            view = zoom

        # matplotlib futurewarning doesn't like lists of slices?
        view = tuple(view)

        ax.imshow(imgs[imn].value[view], origin='lower', interpolation='none',
                  norm=norm, **kwargs)

        if imn == 'model' and 'mask' in imgs:
            ax.contour(imgs['mask'].value[view], levels=[0.5], colors=['w'],
                       linewidths=[0.5])

        pl.title(imn)

        ax.set_xticklabels([])
        ax.set_yticklabels([])
