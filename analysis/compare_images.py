from spectral_cube import SpectralCube
from spectral_cube.utils import NoBeamError
from astropy import visualization
from astropy.stats import mad_std
from astropy import units as u
import pylab as pl
import matplotlib
import numpy as np
from astropy.io import fits
from astropy import wcs
from astropy import log
from imstats import get_noise_region, parse_fn
import regions
import operator
from functools import reduce

from zoom_figures import determine_asinh_ticklocs


def make_comparison_image(filename1, filename2, title1='bsens', title2='cleanest', writediff=False, allow_reproj=False, nticks=9,
                          asinh_scaling_factor=10, scalebarlength=15, diff_suffix='.preselfcal-diff',
                          sigma_scale=15, cm='gray_r', inset_cm='inferno', allow_zero_diff=False):
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
    data_pre = cube_pre[0].value * 1e3
    data_post = cube_post[0].value * 1e3

    #data_pre[np.abs(data_pre) < 1e-7] = np.nan
    #data_post[np.abs(data_post) < 1e-7] = np.nan

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
                                                         + diff_suffix + ".fits",
                                                         overwrite=True)
    fig = pl.figure(1, figsize=(14,6))
    fig.clf()

    if fig.get_figheight() != 6:
        fig.set_figheight(6)
    if fig.get_figwidth() != 14:
        fig.set_figwidth(14)

    #data_pre_display = np.arcsinh(data_pre*asinh_scaling_factor)
    #data_post_display = np.arcsinh(data_post*asinh_scaling_factor)
    #diff_display = np.arcsinh(diff*asinh_scaling_factor)
    data_pre_display = data_pre
    data_post_display = data_post
    diff_display = diff

    minv = np.nanpercentile(data_pre_display, 0.05)
    maxv = np.nanpercentile(data_pre_display, 99.995)
    #if maxv > np.arcsinh(1000):
    #    maxv = np.arcsinh(1000)
    #if np.abs(minv) > maxv:
    #    minv = -maxv

    if allow_zero_diff:
        stddev = mad_std(data_pre)
    else:
        stddev = mad_std(diff, ignore_nan=True)
        assert stddev > 0

    linear_norm = visualization.simple_norm(data=diff_display.squeeze(), stretch='linear',
                                            #min_percent=0.05, max_percent=99.995,)
                                            min_cut=-sigma_scale*stddev, max_cut=sigma_scale*stddev)
    asinh_norm =  visualization.simple_norm(data=diff_display.squeeze(), stretch='asinh',
                                            #min_percent=0.05, max_percent=99.995,)
                                            min_cut=sigma_scale*stddev, max_cut=maxv)
    asinh_norm.vmin = sigma_scale*stddev


    
    inset_cm = pl.cm.get_cmap(inset_cm)
    inset_cm.set_under((0,0,0,0))


    #cm = pl.matplotlib.cm.gray
    #cm.set_bad('white', 0)
    #cm = pl.matplotlib.cm.viridis

    ax1 = pl.subplot(1,3,1)
    ax2 = pl.subplot(1,3,2)
    ax3 = pl.subplot(1,3,3)
    for ax in (ax1,ax2,ax3):
        ax.cla()

    ax1.imshow(data_pre_display, norm=linear_norm, origin='lower', interpolation='nearest', cmap=cm)
    ax1.imshow(np.ma.masked_where(data_pre_display < asinh_norm.vmin, data_pre_display),
               norm=asinh_norm, origin='lower', interpolation='nearest', cmap=inset_cm, vmin=asinh_norm.vmin)
    ax1.set_title(title1)

    # scalebar
    ww = cube_pre.wcs.celestial
    cd = (ww.pixel_scale_matrix[1,1] * 3600)
    blc = np.array(diff.shape)*0.1
    ax1.add_patch(matplotlib.patches.Rectangle([blc[1]*0.8, blc[0]*0.9],
                                               width=scalebarlength/cd*1.4,
                                               height=blc[0]*0.6,
                                               edgecolor='k', facecolor='w',
                                               alpha=0.5))
    ax1.plot([blc[1], blc[1]+scalebarlength/cd], [blc[0], blc[0]], color='k')
    tx = ax1.annotate(f'{scalebarlength}"', (blc[1]+scalebarlength/2/cd, blc[0]*1.1))
    tx.set_horizontalalignment('center')

    ax2.imshow(data_post_display, norm=linear_norm, origin='lower', interpolation='nearest', cmap=cm)
    ax2.imshow(data_post_display, norm=asinh_norm, origin='lower', interpolation='nearest', cmap=inset_cm, vmin=asinh_norm.vmin)
    ax2.set_title(title2)

    im_lin = ax3.imshow(diff_display.squeeze(), norm=linear_norm, origin='lower', interpolation='nearest', cmap=cm)
    im_in = ax3.imshow(diff_display.squeeze(), norm=asinh_norm, origin='lower', interpolation='nearest', cmap=inset_cm, vmin=asinh_norm.vmin)
    ax3.set_title(f"{title2} - {title1}")

    for ax in (ax1,ax2,ax3):
        ax.set_xticks([])
        ax.set_yticks([])

    pl.subplots_adjust(wspace=0.0)

    cbax = fig.add_axes([0.91,0.18,0.015,0.62])
    cb1 = fig.colorbar(cax=cbax, mappable=im_lin)
    cbax2 = fig.add_axes([0.97,0.18,0.015,0.62])
    cb2 = fig.colorbar(cax=cbax2, mappable=im_in)
    cb2.set_label("S$_\\nu$ [mJy/beam]")
    # mn,mx = cb.get_ticks().min(), cb.get_ticks().max()
    # ticklocs = np.concatenate([np.linspace(-linear_norm.vmax, 0, nticks//2)[:-1], np.linspace(0, linear_norm.vmax, nticks//2)])
    # ticks = np.sinh(ticklocs)
    # cb.update_normal(im_lin)
    # cb.set_ticks(ticks)
    # ticklocs = cb.get_ticks()
    # ticklabels = [f"{np.sinh(x/asinh_scaling_factor):0.2f}" for x in ticklocs]
    # cb.set_ticklabels(ticklabels)

    cb1.ax.tick_params(labelsize=14)
    cb2.ax.tick_params(labelsize=14)

    ticklabels = cb2.ax.get_ymajorticklabels()
    ticks = list(cb2.get_ticks())

    rounded_loc, rounded = determine_asinh_ticklocs(asinh_norm.vmin, asinh_norm.vmax, nticks=nticks, stretch='asinh')
    cb2.set_ticks(rounded_loc)
    cb2.set_ticklabels(rounded)
    

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

    if 'HISTORY' in cube_post.header:
        history = cube_post.header['HISTORY']
        hasamp = any("'calmode': 'ap'" in x for x in history) or any("'calmode': 'a'" in x for x in history)
    else:
        hasamp = False

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
