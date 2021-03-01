from spectral_cube import SpectralCube
from spectral_cube.utils import NoBeamError
from astropy import visualization
from astropy.stats import mad_std
from astropy import units as u
import pylab as pl
import numpy as np
from astropy.io import fits
from astropy import wcs
from astropy import log
from imstats import get_noise_region, parse_fn
import regions
import operator
from functools import reduce


def make_comparison_image(filename1, filename2, title1='bsens', title2='cleanest', writediff=False, allow_reproj=False):
    #fh_pre = fits.open()
    #fh_post = fits.open()
    cube_pre = SpectralCube.read(filename1, format='fits' if 'fits' in filename1 else 'casa_image').with_spectral_unit(u.GHz)
    cube_post = SpectralCube.read(filename2, format='fits' if 'fits' in filename2 else 'casa_image').with_spectral_unit(u.GHz)

    if 'pbcor' in filename1:
        assert 'pbcor' in filename2
    if 'pbcor' in filename2:
        assert 'pbcor' in filename1

    if allow_reproj:
        if cube_pre.shape != cube_post.shape or (cube_post.wcs != cube_pre.wcs and cube_post.wcs.wcs != cube_pre.wcs.wcs):
            cube_post = cube_post.reproject(cube_pre.header)


    cube_pre = cube_pre.with_mask(cube_pre != 0*cube_pre.unit)
    cube_post = cube_post.with_mask(cube_post != 0*cube_post.unit)
    slices = cube_pre.subcube_slices_from_mask(cube_pre.mask & cube_post.mask,
                                               spatial_only=True)[1:]

    # make the cubes match the data; needed for later WCS cutouts
    cube_pre = cube_pre[:, slices[0], slices[1]]
    cube_post = cube_post[:, slices[0], slices[1]]

    #cube_pre = cube_pre.minimal_subcube()
    #cube_post = cube_post.minimal_subcube()
    data_pre = cube_pre[0].value
    data_post = cube_post[0].value

    data_pre[np.abs(data_pre) < 1e-7] = np.nan
    data_post[np.abs(data_post) < 1e-7] = np.nan

    try:
        diff = (data_post - data_pre)
    except Exception as ex:
        print(filename1, filename2, cube_pre.shape, cube_post.shape)
        raise ex

    ww = cube_post.wcs
    pixscale = wcs.utils.proj_plane_pixel_area(ww)*u.deg**2
    try:
        beam = cube_post.beam
        ppbeam = (beam.sr / pixscale).decompose()
        assert ppbeam.unit.is_equivalent(u.dimensionless_unscaled)
        ppbeam = ppbeam.value
    except NoBeamError:
        beam = np.nan*u.sr
        ppbeam = np.nan

    if writediff:
        fits.PrimaryHDU(data=diff,
                        header=cube_post.header).writeto(filename2.split(".fits")[0]
                                                         + ".preselfcal-diff.fits",
                                                         overwrite=True)
    fig = pl.figure(1, figsize=(14,6))
    fig.clf()

    if fig.get_figheight() != 6:
        fig.set_figheight(6)
    if fig.get_figwidth() != 14:
        fig.set_figwidth(14)


    minv = np.nanpercentile(data_pre, 0.05)
    maxv = np.nanpercentile(data_pre, 99.5)
    if np.abs(minv) > maxv:
        minv = -maxv

    norm = visualization.simple_norm(data=diff.squeeze(), stretch='asinh',
                                     #min_percent=0.05, max_percent=99.995,)
                                     min_cut=minv, max_cut=maxv)
    if norm.vmax < 0.001:
        norm.vmax = 0.001

    #cm = pl.matplotlib.cm.gray
    #cm.set_bad('white', 0)
    cm = pl.matplotlib.cm.viridis

    ax1 = pl.subplot(1,3,1)
    ax2 = pl.subplot(1,3,2)
    ax3 = pl.subplot(1,3,3)
    for ax in (ax1,ax2,ax3):
        ax.cla()

    ax1.imshow(data_pre, norm=norm, origin='lower', interpolation='nearest', cmap=cm)
    ax1.set_title(title1)

    ax2.imshow(data_post, norm=norm, origin='lower', interpolation='nearest', cmap=cm)
    ax2.set_title(title2)

    im = ax3.imshow(diff.squeeze(), norm=norm, origin='lower', interpolation='nearest', cmap=cm)
    ax3.set_title(f"{title2} - {title1}")

    for ax in (ax1,ax2,ax3):
        ax.set_xticks([])
        ax.set_yticks([])

    pl.subplots_adjust(wspace=0.0)

    cbax = fig.add_axes([0.91,0.18,0.03,0.64])
    cb = fig.colorbar(cax=cbax, mappable=im)
    cb.set_label("S$_\\nu$ [Jy/beam]")

    meta = parse_fn(filename1)

    reg = get_noise_region(meta['region'], meta['band'])

    if reg is not None:
        reglist = regions.read_ds9(reg)
        composite_region = reduce(operator.or_, reglist)

        if hasattr(composite_region, 'to_mask'):
            msk = composite_region.to_mask()
        else:
            preg = composite_region.to_pixel(cube_pre.wcs.celestial)
            msk = preg.to_mask()

        cutout_pixels_pre = msk.cutout(data_pre, fill_value=np.nan)[msk.data.astype('bool')]

        mad_sample_pre = mad_std(cutout_pixels_pre, ignore_nan=True)
        std_sample_pre = np.nanstd(cutout_pixels_pre)

        if hasattr(composite_region, 'to_mask'):
            msk = composite_region.to_mask()
        else:
            preg = composite_region.to_pixel(cube_post.wcs.celestial)
            msk = preg.to_mask()
        cutout_pixels_post = msk.cutout(data_post, fill_value=np.nan)[msk.data.astype('bool')]

        mad_sample_post = mad_std(cutout_pixels_post, ignore_nan=True)
        std_sample_post = np.nanstd(cutout_pixels_post)


        if np.any(np.isnan(mad_sample_pre)):
            log.warning("mad_sample_pre contains some NaN values")
        if np.any(np.isnan(mad_sample_post)):
            log.warning("mad_sample_post contains some NaN values")

        if len(cutout_pixels_post) != len(cutout_pixels_pre):
            log.warning(f"cutout pixels are different size in pre vs post ({filename1} : {filename2})")
        if (cube_pre.wcs.celestial != cube_post.wcs.celestial) and (cube_pre.wcs.celestial.wcs != cube_post.wcs.celestial.wcs):
            # wcs comparisons stopped working sometime in 2019-2020 - wcs.wcs comparisons appear to work?
            log.warning(f"post and pre have different celestial WCSes ({filename1} : {filename2})")


        if not np.isfinite(mad_sample_pre):
            raise ValueError


    mad_pre = mad_std(data_pre, ignore_nan=True)
    mad_post = mad_std(data_post, ignore_nan=True)

    mad_diff = mad_std(diff, ignore_nan=True)
    diffmask = np.abs(diff) > 3*mad_diff

    history = cube_post.header['HISTORY']
    hasamp = any("'calmode': 'ap'" in x for x in history) or any("'calmode': 'a'" in x for x in history)

    diffstats = {'mean': np.nanmean(diff),
                 'max': np.nanmax(diff),
                 'shape': diff.shape[0],
                 'ppbeam': ppbeam,
                 'sum': np.nansum(diff),
                 'masksum': diff[diffmask].sum(),
                 'min': np.nanmin(diff),
                 'median': np.nanmedian(diff),
                 'mad': mad_diff,
                 'dr_pre': np.nanmax(data_pre) / mad_std(data_pre, ignore_nan=True),
                 'dr_post': np.nanmax(data_post) / mad_std(data_post, ignore_nan=True),
                 'min_pre': np.nanmin(data_pre),
                 'min_post': np.nanmin(data_post),
                 'max_pre': np.nanmax(data_pre),
                 'max_post': np.nanmax(data_post),
                 'sum_pre': np.nansum(data_pre),
                 'sum_post': np.nansum(data_post),
                 'masksum_pre': (data_pre[data_pre > mad_pre*3]).sum(),
                 'masksum_post': (data_post[data_post > mad_post*3]).sum(),
                 'mad_pre': mad_pre,
                 'mad_post':  mad_post,
                 'mad_sample_pre': np.nan,
                 'mad_sample_post': np.nan,
                 'std_sample_pre': np.nan,
                 'std_sample_post': np.nan,
                 'has_amp': hasamp,
                }
    if reg is not None:
        diffstats.update({
            'mad_sample_pre': mad_sample_pre,
            'mad_sample_post': mad_sample_post,
            'std_sample_pre': std_sample_pre,
            'std_sample_post': std_sample_post,
        })

    return ax1, ax2, ax3, fig, diffstats
