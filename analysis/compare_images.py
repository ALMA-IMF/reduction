from spectral_cube import SpectralCube
from astropy import visualization
from astropy.stats import mad_std
from astropy import units as u
import pylab as pl
import numpy as np
import radio_beam
from astropy import wcs


def make_comparison_image(filename1, filename2, title1='bsens', title2='cleanest', writediff=False):
    #fh_pre = fits.open()
    #fh_post = fits.open()
    cube_pre = SpectralCube.read(filename1, format='fits' if 'fits' in filename1 else 'casa_image')
    cube_post = SpectralCube.read(filename2, format='fits' if 'fits' in filename2 else 'casa_image')
    cube_pre = cube_pre.with_mask(cube_pre != 0*cube_pre.unit)
    cube_post = cube_post.with_mask(cube_post != 0*cube_post.unit)
    slices = cube_pre.subcube_slices_from_mask(cube_pre.mask & cube_post.mask,
                                               spatial_only=True)[1:]
    #cube_pre = cube_pre.minimal_subcube()
    #cube_post = cube_post.minimal_subcube()
    data_pre = cube_pre[0].value[slices]
    data_post = cube_post[0].value[slices]

    data_pre[np.abs(data_pre) < 1e-7] = np.nan
    data_post[np.abs(data_post) < 1e-7] = np.nan

    try:
        diff = (data_post - data_pre)
    except Exception as ex:
        print(filename1, filename2, cube_pre.shape, cube_post.shape)
        raise ex

    ww = cube_post.wcs
    beam = cube_post.beam
    pixscale = wcs.utils.proj_plane_pixel_area(ww)*u.deg**2
    ppbeam = (beam.sr / pixscale).decompose()
    assert ppbeam.unit.is_equivalent(u.dimensionless_unscaled)
    ppbeam = ppbeam.value

    if writediff:
        fits.PrimaryHDU(data=diff,
                        header=cube_post.header).writeto(postselfcal+".preselfcal-diff.fits",
                                                         overwrite=True)
    fig = pl.figure(1, figsize=(14,6))
    fig.clf()

    minv = np.nanpercentile(data_pre, 0.05)
    maxv = np.nanpercentile(data_pre, 99.5)
    if np.abs(minv) > maxv:
        minv = -maxv

    norm = visualization.simple_norm(data=diff.squeeze(), stretch='asinh',
                                     #min_percent=0.05, max_percent=99.995,)
                                     min_cut=minv, max_cut=maxv)
    if norm.vmax < 0.001:
        norm.vmax = 0.001

    cm = pl.matplotlib.cm.gray
    cm.set_bad('white', 0)

    ax1 = pl.subplot(1,3,1)
    ax2 = pl.subplot(1,3,2)
    ax3 = pl.subplot(1,3,3)
    for ax in (ax1,ax2,ax3):
        ax.cla()
    ax1.imshow(data_pre, norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax1.set_title(title1)
    ax2.imshow(data_post, norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax2.set_title(title2)
    im = ax3.imshow(diff.squeeze(), norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax3.set_title(f"{title2} - {title1}")

    for ax in (ax1,ax2,ax3):
        ax.set_xticks([])
        ax.set_yticks([])

    pl.subplots_adjust(wspace=0.0)

    cbax = fig.add_axes([0.91,0.18,0.03,0.64])
    fig.colorbar(cax=cbax, mappable=im)

    diffstats = {'mean': np.nanmean(diff),
                 'max': np.nanmax(diff),
                 'shape': diff.shape[0],
                 'ppbeam': ppbeam,
                 'sum': np.nansum(diff),
                 'min': np.nanmin(diff),
                 'median': np.nanmedian(diff),
                 'mad': mad_std(diff, ignore_nan=True),
                 'dr_pre': np.nanmax(data_pre) / mad_std(data_pre, ignore_nan=True),
                 'dr_post': np.nanmax(data_post) / mad_std(data_post, ignore_nan=True),
                 'min_pre': np.nanmin(data_pre),
                 'min_post': np.nanmin(data_post),
                 'max_pre': np.nanmax(data_pre),
                 'max_post': np.nanmax(data_post),
                 'sum_pre': np.nansum(data_pre),
                 'sum_post': np.nansum(data_post),
                 'mad_pre': mad_std(data_pre, ignore_nan=True),
                 'mad_post':  mad_std(data_post, ignore_nan=True),
                }

    return ax1, ax2, ax3, fig, diffstats
