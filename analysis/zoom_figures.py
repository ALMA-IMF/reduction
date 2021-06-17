import numpy as np

from astropy.visualization import simple_norm
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector
import astropy.visualization.wcsaxes
from spectral_cube import SpectralCube
from spectral_cube.utils import NoBeamError
from astropy import units as u

from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy import coordinates

from astropy.visualization import AsinhStretch
from astropy.stats import mad_std

import warnings
warnings.filterwarnings('ignore')

import pylab as pl

import sys
sys.path.append('/orange/adamginsburg/ALMA_IMF/reduction/analysis')
from spectralindex import prefixes
import field_data


def make_scalebar(ax, left_side, length, color='w', linestyle='-', label='',
                  fontsize=12, text_offset=0.1*u.arcsec):
    axlims = ax.axis()
    lines = ax.plot(u.Quantity([left_side.ra, left_side.ra-length]),
                    u.Quantity([left_side.dec]*2),
                    color=color, linestyle=linestyle, marker=None,
                    transform=ax.get_transform('fk5'),
                   )
    txt = ax.text((left_side.ra-length/2).to(u.deg).value,
                  (left_side.dec+text_offset).to(u.deg).value,
                  label,
                  verticalalignment='bottom',
                  horizontalalignment='center',
                  transform=ax.get_transform('fk5'),
                  color=color,
                  fontsize=fontsize,
                 )
    ax.axis(axlims)
    return lines,txt


def make_zoom(fieldid, zoom_parameters,
              overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'linear'},
              overview_cmap='gray_r',
              inset_cmap='inferno',
              band='B6',
              main_zoombox=None,
              scalebar_loc=(0.1,0.1),
              scalebar_length=0.1*u.pc,
              beam_loc=(0.05, 0.05),
              nsigma_asinh=5,
              nsigma_max=10,
              nticks_inset=7,
             ):

    pfxs = prefixes[fieldid]
    wl = r'\mathrm{3mm}' if band.lower() == 'b3' else r'\mathrm{1mm}'

    finaliter_prefix = pfxs[f'finaliter_prefix_{band}'.lower()]
    image = SpectralCube.read(f'{finaliter_prefix}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube()
    try:
        image = image.to(u.mJy)
    except u.UnitConversionError:
        image = image.to(u.mJy/u.beam)
    print(image)

    radesys = image.wcs.wcs.radesys.upper()

    fig = pl.figure(1, figsize=(10,10))
    fig.clf()
    ax = fig.add_subplot(projection=image.wcs.celestial)

    img = image[0].value
    norm = simple_norm(img, **overview_vis_pars)

    img[img==0] = np.nan
    mad = mad_std(img, ignore_nan=True)

    if hasattr(norm.stretch, 'a') and nsigma_asinh is not None:
        norm.vmax = (np.nanmedian(img) + nsigma_max*mad)
        a_point = (np.nanmedian(img) + nsigma_asinh*mad) / norm.vmax
        norm.stretch.a = a_point
        print(f"numbers for norm: {np.nanmedian(img), nsigma_asinh, mad, nsigma_asinh*mad, norm.vmax, a_point}")

    im = ax.imshow(img, cmap=overview_cmap, norm=norm)

    tick_fontsize=16
    ra = ax.coords['ra']
    ra.set_major_formatter('hh:mm:ss.s')
    dec = ax.coords['dec']
    ra.set_axislabel(f"RA ({radesys})", fontsize=20)
    dec.set_axislabel(f"Dec ({radesys})", fontsize=20, minpad=0.0)
    ra.ticklabels.set_fontsize(tick_fontsize)
    ra.set_ticks(exclude_overlapping=True)
    dec.ticklabels.set_fontsize(tick_fontsize)
    dec.set_ticks(exclude_overlapping=True)


    for zp in zoom_parameters:

        xl,xr = zp['xl'], zp['xr']
        yl,yu = zp['yl'], zp['yu']
        slc = [slice(yl,yu), slice(xl,xr)]
        axins = inset_axes(ax, **zp['inset_pars'],
                           axes_class=astropy.visualization.wcsaxes.core.WCSAxes,
                           axes_kwargs=dict(wcs=image[0][slc].wcs.celestial))

        norm2 = simple_norm(img, **zp['vis_pars'])

        inset_cm = pl.cm.get_cmap(inset_cmap)
        inset_cm.set_bad(inset_cm(0))

        im_ins = axins.imshow(img[slc], extent=[xl,xr,yl,yu], cmap=inset_cm, norm=norm2)
        mark_inset(parent_axes=ax, inset_axes=axins,
                   fc="none", ec="b", **zp['mark_inset_pars'])
        ra = axins.coords['ra']
        dec = axins.coords['dec']
        axins.set_xticklabels([])
        axins.set_yticklabels([])
        axins.xaxis.set_visible(False)
        axins.yaxis.set_visible(False)
        ra.set_ticks_visible(False)
        dec.set_ticks_visible(False)
        ra.set_axislabel('')
        dec.set_axislabel('')
        ra.ticklabels.set_visible(False)
        dec.ticklabels.set_visible(False)

        caxins = inset_axes(axins,
                 width="5%",  # width = 10% of parent_bbox width
                 height="100%",  # height : 50%
                 loc='lower left',
                 bbox_to_anchor=(1.05, 0., 1, 1),
                 bbox_transform=axins.transAxes,
                 borderpad=0,
                 )

        cbins = pl.colorbar(mappable=im_ins, cax=caxins)
        cbins.ax.tick_params(labelsize=14)
        cbins.set_label(f"S$_{wl}$ [mJy beam$^{-1}$]", fontsize=14)

        if 'tick_locs' in zp:
            cbins.set_ticks(zp['tick_locs'])
            if 'tick_labels' in zp:
                cbins.set_ticklabels(zp['tick_labels'])
        elif 'asinh' in str(norm2.stretch).lower():
            rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=nticks_inset)
            cbins.set_ticks(rounded_loc)
            cbins.set_ticklabels(rounded)
        elif'log' in str(norm2.stretch).lower():
            if norm2.vmin > 0:
                rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=nticks_inset, rms=mad, stretch='log')
                cbins.set_ticks(rounded_loc)
                cbins.set_ticklabels(rounded)
            else:
                ticks = cbins.get_ticks()
                newticks = [norm2.vmin] + list(ticks)
                newticks = [norm2.vmin, 0,] + list(np.geomspace(mad, norm2.vmax, 4))
                print(f"ticks={ticks}, newticks={newticks}, mad={mad}, vmin={norm2.vmin}")
                cbins.set_ticks(newticks)


    #print(ax.axis())
    if main_zoombox:
        ax.axis(main_zoombox)

    divider = make_axes_locatable(ax)
    cax1 = fig.add_axes([ax.get_position().x1+0.01,
                         ax.get_position().y0,
                         0.02,
                         ax.get_position().height])
    cb1 = pl.colorbar(mappable=im, cax=cax1)
    cb1.ax.tick_params(labelsize=14)
    cb1.set_label(f"S$_{wl}$ [mJy beam$^{-1}$]", fontsize=14)
    pl.setp(cb1.ax.yaxis.get_label(), backgroundcolor="white")

    left_side = coordinates.SkyCoord(*image.wcs.celestial.wcs_pix2world(scalebar_loc[1]*img.shape[1],
                                                                        scalebar_loc[0]*img.shape[0], 0)*u.deg, frame='fk5')
    length = (scalebar_length / field_data.distances[fieldid]).to(u.arcsec, u.dimensionless_angles())
    make_scalebar(ax, left_side, length, color='k', linestyle='-', label=f'{scalebar_length:0.1f}',
                  fontsize=16, text_offset=0.5*u.arcsec)

    ell = image.beam.ellipse_to_plot(beam_loc[1]*img.shape[1], beam_loc[0]*img.shape[0], pixscale=image.wcs.celestial.pixel_scale_matrix[1,1]*u.deg)
    ax.add_patch(ell)


    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_inset_zooms_{band}.png', bbox_inches='tight')
    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_inset_zooms_{band}.pdf', bbox_inches='tight')


def make_multifig(fieldid,
                  #overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'linear'},
                  overview_cmap='gray_r',
                  inner_stretch='log',
                  inner_maxpct=100,
                  inset_cmap='inferno',
                  band='B3',
                  nsigma_linear_max=15,
                  nsigma_linear_min=5,
                  nsigma_asinh=15,
                  pfxs=None,
                  finaliter_prefix=None,
                  region=None,
                  fig=None,
                  ax=None,
                  title=None,
                  ):

    if pfxs is None:
        pfxs = prefixes[fieldid]
    wl = r'\mathrm{3mm}' if band.lower() == 'b3' else r'\mathrm{1mm}'

    if finaliter_prefix is None:
        finaliter_prefix = pfxs[f'finaliter_prefix_{band}'.lower()]
    image = SpectralCube.read(f'{finaliter_prefix}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube()
    try:
        image = image.to(u.mJy)
    except u.UnitConversionError:
        image = image.to(u.mJy/u.beam)

    radesys = image.wcs.wcs.radesys.upper()

    if fig is None:
        fig = pl.figure(1, figsize=(12,10))
        fig.clf()
    if ax is None:
        ax = fig.add_subplot(projection=image.wcs.celestial)

    img = image[0].value

    img[img==0] = np.nan
    mad = mad_std(img, ignore_nan=True)

    norm = simple_norm(img, stretch='linear', min_cut=-nsigma_linear_min*mad, max_cut=nsigma_linear_max*mad,)

    overview_cmap = pl.cm.get_cmap(overview_cmap)
    overview_cmap.set_bad('white')

    im1 = ax.imshow(img, cmap=overview_cmap, norm=norm)

    cm = pl.cm.get_cmap(inset_cmap)
    cm.set_under((0,0,0,0))

    vmin = norm.vmax*0.99
    norm2 = simple_norm(img, min_cut=vmin, stretch=inner_stretch, max_percent=inner_maxpct)
    norm2.vmin = vmin

    if hasattr(norm2.stretch, 'a') and nsigma_asinh is not None:
        #norm2.vmax = (np.nanmedian(img) + nsigma_max*mad)
        a_point = (vmin + nsigma_asinh*mad) / (norm2.vmax - vmin)
        #print(f"a point before: {norm2.stretch.a}, after: {a_point}")
        norm2.stretch.a = a_point


    im2 = ax.imshow(img, cmap=cm, norm=norm2, vmin=norm2.vmin)

    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    #cax1 = divider.append_axes("right", size="5%", pad=0.05)
    #cax2 = divider.append_axes("right", size="5%", pad=0.1)
    cax1 = fig.add_axes([ax.get_position().x1+0.01,
                         ax.get_position().y0,
                         0.02,
                         ax.get_position().height])
    cax2 = fig.add_axes([ax.get_position().x1+0.08,
                         ax.get_position().y0,
                         0.02,
                         ax.get_position().height])

    cb2 = pl.colorbar(mappable=im2, cax=cax2)
    cb1 = pl.colorbar(mappable=im1, cax=cax1)
    cb1.ax.tick_params(labelsize=14)
    cb2.ax.tick_params(labelsize=14)

    ticklabels = cb2.ax.get_ymajorticklabels()
    ticks = list(cb2.get_ticks())

    # max_tick_fig1 = cb1.get_ticks()[-1]

    # toptickval = np.round(max_tick_fig1, 1)
    # minVal = norm2.vmin #np.round(norm2.vmin, 1)

    # mintickval = min(map(float, ticklabels))

    # if toptickval > minVal:
    #     print("toptick was greater")
    #     newticks = [minVal, toptickval] + ticks
    #     newticklabels = [f"{minVal:0.2f}",f"{toptickval:0.2f}"] + [x.get_text() for x in ticklabels]
    # else:
    #     newticks = [minVal, ] + ticks
    #     newticklabels = [f"{minVal:0.2f}",] + [x.get_text() for x in ticklabels]
    # print(f"new ticks: {newticks}, {newticklabels} norm2vmin = {norm2.vmin}")
    # cb2.set_ticks(newticks)
    # cb2.set_ticklabels(newticklabels)

    if inner_stretch in ('asinh', 'log'):
        rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=10, stretch=inner_stretch)
        cb2.set_ticks(rounded_loc)
        cb2.set_ticklabels(rounded)
        print(f"old ticks: {ticklabels}, new ticks: {rounded}")

    cb2.set_label(f"S$_{wl}$ [mJy beam$^{-1}$]", fontsize=14)

    tick_fontsize=16
    ra = ax.coords['ra']
    ra.set_major_formatter('hh:mm:ss.s')
    dec = ax.coords['dec']
    ra.set_axislabel(f"RA ({radesys})", fontsize=20)
    dec.set_axislabel(f"Dec ({radesys})", fontsize=20, minpad=0.0)
    ra.ticklabels.set_fontsize(tick_fontsize)
    ra.set_ticks(exclude_overlapping=True)
    dec.ticklabels.set_fontsize(tick_fontsize)
    dec.set_ticks(exclude_overlapping=True)

    print(image.wcs.celestial.wcs_pix2world(0.1*img.shape[1], 0.1*img.shape[0], 0))
    left_side = coordinates.SkyCoord(*image.wcs.celestial.wcs_pix2world(0.1*img.shape[1], 0.1*img.shape[0], 0)*u.deg, frame='fk5')
    print(left_side)
    length = (0.1*u.pc / field_data.distances[fieldid]).to(u.arcsec, u.dimensionless_angles())
    make_scalebar(ax, left_side, length, color='k', linestyle='-', label='0.1 pc',
                  fontsize=16, text_offset=0.5*u.arcsec)

    ell = image.beam.ellipse_to_plot(0.05*img.shape[1], 0.05*img.shape[0], pixscale=image.wcs.celestial.pixel_scale_matrix[1,1]*u.deg)
    ax.add_patch(ell)

    if title:
        ax.text(0.99, 0.99, fieldid, fontsize=16, horizontalalignment='right',
                verticalalignment='top', transform=ax.transAxes)


    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_multicolor_{band}.png', bbox_inches='tight')
    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_multicolor_{band}.pdf', bbox_inches='tight')

def determine_asinh_ticklocs(vmin, vmax, nticks, rms=None, stretch='asinh'):
    if stretch == 'asinh':
        arcsinh_range = np.arcsinh(vmin), np.arcsinh(vmax)
        new_ticks = np.sinh(np.linspace(*arcsinh_range, nticks))
    elif stretch == 'log':
        if vmin > 0:
            arcsinh_range = np.log10(vmin), np.log10(vmax)
            new_ticks = 10**(np.linspace(*arcsinh_range, nticks))
        else:
            arcsinh_range = (np.log10(rms), np.log10(vmax))
            new_ticks = np.concatenate([[-rms, 0,], np.linspace(*arcsinh_range, nticks-2)])
        #print(f"log-based asinh range={arcsinh_range}, vmin={vmin}, vmax={vmax}")
    rounded = [np.format_float_positional(x, 2, unique=False, fractional=False, trim='k') for x in new_ticks]

    rounded_loc = np.array(rounded).astype('float')
    if rounded_loc.min() < 0 and rounded_loc.max() > 0:
        zero_index = np.argmin(np.abs(rounded_loc))
        rounded_loc[zero_index] = 0
        rounded[zero_index] = 0

        if zero_index == 0:
            rounded_loc = np.array([vmin] + list(rounded_loc))
            rounded = [np.format_float_positional(vmin, 2, unique=False, fractional=False, trim='k')] + rounded

    if rounded_loc[0] < vmin:
        rounded_loc[0] = vmin

    if rounded_loc[-1] > vmax:
        rounded_loc[-1] = vmax
    else:
        rounded_loc[-1] = vmax
        rounded[-1] = np.format_float_positional(vmax, 2, unique=False, fractional=False, trim='k')

    rounded = [str(x).rstrip('.') for x in rounded]

    return rounded_loc, rounded


def make_robust_comparison(fieldid,
                  #overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'linear'},
                  overview_cmap='gray_r',
                  inner_stretch='log',
                  inner_maxpct=100,
                  inset_cmap='inferno',
                  band='B3',
                  nsigma_linear_max=15,
                  nsigma_linear_min=5,
                  nsigma_asinh=15,
                  pfxs=None,
                  finaliter_prefix=None,
                  region=None,
                  fig=None,
                  suffix="image.tt0.fits",
                  fileformat='fits',
                  ):

    if pfxs is None:
        pfxs = prefixes[fieldid]
    wl = r'\mathrm{3mm}' if band.lower() == 'b3' else r'\mathrm{1mm}'

    if finaliter_prefix is None:
        finaliter_prefix = pfxs[f'finaliter_prefix_{band}'.lower()]

    base_filename = f'{finaliter_prefix}.{suffix}'
    image = SpectralCube.read(base_filename, format=fileformat).minimal_subcube()
    if image.unit.is_equivalent(u.mJy):
        image = image.to(u.mJy)
    elif image.unit.is_equivalent(u.mJy/u.pix):
        # CASA residuals, models
        image = image.to(u.mJy/u.pix)
    elif image.unit.is_equivalent(u.mJy/u.beam):
        image = image.to(u.mJy/u.beam)

    radesys = image.wcs.wcs.radesys.upper()

    if fig is None:
        fig = pl.figure(1, figsize=(16,5))
        fig.clf()
    img = image[0].value

    img[img==0] = np.nan
    mad = mad_std(img, ignore_nan=True)

    norm = simple_norm(img, stretch='linear', min_cut=-nsigma_linear_min*mad, max_cut=nsigma_linear_max*mad,)
    vmin = norm.vmax*0.99
    norm2 = simple_norm(img, min_cut=vmin, stretch=inner_stretch, max_percent=inner_maxpct)
    norm2.vmin = vmin


    robusts = (-2,0,2)

    for ii, robust in enumerate(robusts):
        imfilename = base_filename.replace('robust0',f'robust{robust}')
        print(imfilename)
        image = SpectralCube.read(imfilename,
                                  format=fileformat).minimal_subcube()
        if region is not None:
            image = image.subcube_from_regions(region)
        if image.unit.is_equivalent(u.mJy):
            image = image.to(u.mJy)
        elif image.unit.is_equivalent(u.mJy/u.pix):
            # CASA residuals, models
            image = image.to(u.mJy/u.pix)
        elif image.unit.is_equivalent(u.mJy/u.beam):
            image = image.to(u.mJy/u.beam)

        img = image[0].value
        img[img==0] = np.nan

        ax = fig.add_subplot(1, len(robusts), ii+1,
                             projection=image.wcs.celestial)

        im1 = ax.imshow(img, cmap=overview_cmap, norm=norm)

        cm = pl.cm.get_cmap(inset_cmap)
        cm.set_under((0,0,0,0))

        if hasattr(norm2.stretch, 'a') and nsigma_asinh is not None:
            #norm2.vmax = (np.nanmedian(img) + nsigma_max*mad)
            a_point = (vmin + nsigma_asinh*mad) / (norm2.vmax - vmin)
            #print(f"a point before: {norm2.stretch.a}, after: {a_point}")
            norm2.stretch.a = a_point


        im2 = ax.imshow(img, cmap=cm, norm=norm2, vmin=norm2.vmin)

        if ii == len(robusts) - 1:
            # create an axes on the right side of ax. The width of cax will be 5%
            # of ax and the padding between cax and ax will be fixed at 0.05 inch.
            divider = make_axes_locatable(ax)
            #cax1 = divider.append_axes("right", size="5%", pad=0.05)
            #cax2 = divider.append_axes("right", size="5%", pad=0.1)
            cax1 = fig.add_axes([ax.get_position().x1+0.01,
                                 ax.get_position().y0,
                                 0.02,
                                 ax.get_position().height])
            cax2 = fig.add_axes([ax.get_position().x1+0.08,
                                 ax.get_position().y0,
                                 0.02,
                                 ax.get_position().height])

            cb2 = pl.colorbar(mappable=im2, cax=cax2)
            cb1 = pl.colorbar(mappable=im1, cax=cax1)
            cb1.ax.tick_params(labelsize=14)
            cb2.ax.tick_params(labelsize=14)

            ticklabels = cb2.ax.get_ymajorticklabels()
            ticks = list(cb2.get_ticks())

            # max_tick_fig1 = cb1.get_ticks()[-1]

            # toptickval = np.round(max_tick_fig1, 1)
            # minVal = norm2.vmin #np.round(norm2.vmin, 1)

            # mintickval = min(map(float, ticklabels))

            # if toptickval > minVal:
            #     print("toptick was greater")
            #     newticks = [minVal, toptickval] + ticks
            #     newticklabels = [f"{minVal:0.2f}",f"{toptickval:0.2f}"] + [x.get_text() for x in ticklabels]
            # else:
            #     newticks = [minVal, ] + ticks
            #     newticklabels = [f"{minVal:0.2f}",] + [x.get_text() for x in ticklabels]
            # print(f"new ticks: {newticks}, {newticklabels} norm2vmin = {norm2.vmin}")
            # cb2.set_ticks(newticks)
            # cb2.set_ticklabels(newticklabels)

            if inner_stretch in ('asinh', 'log'):
                rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=10, stretch=inner_stretch)
                cb2.set_ticks(rounded_loc)
                cb2.set_ticklabels(rounded)
                print(f"old ticks: {ticklabels}, new ticks: {rounded}")

            cb2.set_label(f"S$_{wl}$ [mJy beam$^{-1}$]", fontsize=14)

        tick_fontsize=16
        ra = ax.coords['ra']
        ra.set_major_formatter('hh:mm:ss.s')
        ra.set_axislabel(f"RA ({radesys})", fontsize=20)
        ra.ticklabels.set_fontsize(tick_fontsize)
        ra.set_ticks(exclude_overlapping=True)
        dec = ax.coords['dec']
        if ii == 0:
            dec.set_axislabel(f"Dec ({radesys})", fontsize=20, minpad=0.0)
            dec.ticklabels.set_fontsize(tick_fontsize)
            dec.set_ticks(exclude_overlapping=True)
        else:
            dec.set_ticks_visible(False)
            dec.set_ticklabel_visible(False)
            dec.set_axislabel("")

        #print(image.wcs.celestial.wcs_pix2world(0.1*img.shape[1], 0.1*img.shape[0], 0))
        left_side = coordinates.SkyCoord(*image.wcs.celestial.wcs_pix2world(0.1*img.shape[1], 0.1*img.shape[0], 0)*u.deg, frame='fk5')
        #print(left_side)
        length = (0.1*u.pc / field_data.distances[fieldid]).to(u.arcsec, u.dimensionless_angles())
        make_scalebar(ax, left_side, length, color='k', linestyle='-', label='0.1 pc',
                      fontsize=16, text_offset=0.5*u.arcsec)

        try:
            ell = image.beam.ellipse_to_plot(0.05*img.shape[1], 0.05*img.shape[0], pixscale=image.wcs.celestial.pixel_scale_matrix[1,1]*u.deg)
            ax.add_patch(ell)
        except NoBeamError:
            pass


    pl.savefig(f'/orange/adamginsburg/web/secure/ALMA-IMF/diagnostic_plots/robust_comparisons/{fieldid}_multicolor_robusts_{band}_{suffix}.png', bbox_inches='tight')
    pl.savefig(f'/orange/adamginsburg/web/secure/ALMA-IMF/diagnostic_plots/robust_comparisons/{fieldid}_multicolor_robusts_{band}_{suffix}.pdf', bbox_inches='tight')

zoom_parameters = {}
zoom_parameters[('G008', 'B3')] = [{'xl':1500, 'xr':1900, 'yl':600, 'yu':1000, 
                                    'inset_pars':{'loc': 1, 'width':3, 'height':3,  'bbox_to_anchor':(550, 0, 100,100)},
                                    'mark_inset_pars':{'loc1':1, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 1, 'stretch':'log'}
                                   },
                                   {'xl':700, 'xr':850, 'yl':1025, 'yu':1175, 
                                    'inset_pars':{'loc': 3, 'width':3, 'height':3,  'bbox_to_anchor':(0, -120, 100,100)},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.9, 'min_percent': 2, 'stretch':'linear'}
                                   },
                                  ]
zoom_parameters[('G338', 'B3')] = [{'xl':1050, 'xr':1300, 'yl':1050, 'yu':1300, 
                                    'inset_pars':{'loc': 1, 'width':3, 'height':3, 'bbox_to_anchor':(830,540,100,100)},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                   {'xl':1050, 'xr':1350, 'yl':575, 'yu':875, 
                                    'inset_pars':{'loc': 1, 'width':3, 'height':3, 'bbox_to_anchor':(830,160,100,100),},
                                    'mark_inset_pars':{'loc1':1, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                  ]
zoom_parameters[('G328', 'B3')] = [{'xl':925, 'xr':1350, 'yl':1850, 'yu':2050, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':3, 'bbox_to_anchor':(480,760,100,100)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                   {'xl':950, 'xr':1350, 'yl':1050, 'yu':1600, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':(1000,300,100,300),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                  ]
zoom_parameters[('G12', 'B3')] = [
                                   {'xl':290, 'xr':450, 'yl':300, 'yu':545, 
                                    'inset_pars':{'loc': 3, 'width':7, 'height':7, 'bbox_to_anchor':(670,100,100,300),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('W51IRS2', 'B3')] = [{'xl':1425, 'xr':1700, 'yl':1475, 'yu':1750, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':3.4, 'bbox_to_anchor':(460,760,100,140)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                   {'xl':850, 'xr':1200, 'yl':850, 'yu':1400, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':(1000,200,100,300),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                      {'xl':1850, 'xr':2000, 'yl':1000, 'yu':1200, 
                                    'inset_pars':{'loc': 1, 'width':5, 'height':5, 'bbox_to_anchor':(970,800,100,100)},
                                    'mark_inset_pars':{'loc1':2, 'loc2':2,},
                                    'vis_pars':{'max_percent':99.0, 'min_percent': 0, 'stretch':'linear'}
                                   },
                                  ]
zoom_parameters[('W51IRS2', 'B6')] = [{'xl':335, 'xr':550, 'yl':460, 'yu':630, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(850, 100, 300, 650),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'tick_locs': [-0.5, 0, 0.5, 5, 30, 100, 445],
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   {'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                    'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,50),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'tick_locs': [-0.33, -0.1, 0, 0.5, 1, 5, 26],
                                    'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('G327', 'B3')] = [{'xl':800, 'xr':1600, 'yl':900, 'yu':1300, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':3, 'bbox_to_anchor':(460,760,100,100)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                   
                                  ]
zoom_parameters[('G10', 'B3')] = [{'xl':900, 'xr':1400, 'yl':980, 'yu':1250, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':3, 'bbox_to_anchor':(460,760,100,100)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.9995, 'min_percent': 0.5, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('G337', 'B3')] = [{'xl':1000, 'xr':1300, 'yl':600, 'yu':1250, 
                                    'inset_pars':{'loc': 4, 'width':8, 'height':8, 'bbox_to_anchor':[1080,50,100,100]},
                                    'mark_inset_pars':{'loc1':3, 'loc2':2,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'asinh'}
                                   },
                                  ]
zoom_parameters[('G353', 'B3')] = [{'xl':260, 'xr':520, 'yl':345, 'yu':475, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':[480,870,100,100]},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.5, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('W51-E', 'B6')] = [{'xl':750, 'xr':950, 'yl':620, 'yu':1050, 
                                    'inset_pars':{'loc': 1, 'width':8, 'height':8, 'bbox_to_anchor':(810, 0, 330, 650),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'tick_locs': [-1.5, -0.5, 0, 0.5, 5, 10, 50, 100, 336],
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('W51-E', 'B3')] = [{'xl':2050, 'xr':2350, 'yl':1650, 'yu':2300, 
                                    'inset_pars':{'loc': 2, 'width':6, 'height':4, 'bbox_to_anchor':(-50,330,0,300), },
                                    'mark_inset_pars':{'loc1':3, 'loc2':1,},
                                    'tick_locs': [-0.2, -0.1, 0, 0.5, 1, 10, 50, 109],
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.5, 'stretch':'log'}
                                   },
                                   {'xl':2600, 'xr':3300, 'yl':1700, 'yu':3000, 
                                    'inset_pars':{'loc': 1, 'width':8, 'height':8, 'bbox_to_anchor':(1100,350,100,300),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':2,},
                                    'vis_pars':{'max_percent':99.99, 'min_percent': 0.05, 'stretch':'asinh'}
                                   },
                                   #   {'xl':1850, 'xr':2000, 'yl':1000, 'yu':1200, 
                                   # 'inset_pars':{'loc': 1, 'width':5, 'height':5, 'bbox_to_anchor':(970,800,100,100)},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':2,},
                                   # 'vis_pars':{'max_percent':99.0, 'min_percent': 0, 'stretch':'linear'}
                                   #},
                                  ]
zoom_parameters[('W43MM2', 'B3')] = [{'xl':2075, 'xr':2350, 'yl':500, 'yu':775, 
                                    'inset_pars':{'loc': 4, 'width':4, 'height':4, 'bbox_to_anchor':(1050,50,0,300), },
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.0, 'stretch':'asinh'}
                                   },
                                   {'xl':350, 'xr':650, 'yl':2200, 'yu':2500, 
                                    'inset_pars':{'loc': 2, 'width':3, 'height':3, 'bbox_to_anchor':(150,540,100,300)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.0, 'stretch':'asinh'}
                                   },
                                    {'xl':1875, 'xr':2075, 'yl':1600, 'yu':1950, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':(1010,540,100,300)},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'asinh'}
                                   },
                                  ]
zoom_parameters[('G333', 'B3')] = [{'xl':1000, 'xr':1600, 'yl':900, 'yu':1550, 
                                    'inset_pars':{'loc': 3, 'width':5, 'height':5, 'bbox_to_anchor':(150,625,300,300)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 1, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('G351', 'B3')] = [{'xl':325, 'xr':475, 'yl':325, 'yu':475, 
                                    'inset_pars':{'loc': 2, 'width':2.5, 'height':2.5,},# 'bbox_to_anchor':(150,625,300,300)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':1,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 1, 'stretch':'log'}
                                   },
                                  ]
zoom_parameters[('W43MM3', 'B3')] = [{'xl':1275, 'xr':1500, 'yl':1225, 'yu':1450, 
                                    'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1050,50,0,600), },
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.0, 'stretch':'asinh'}
                                   },
                                   {'xl':2325, 'xr':2600, 'yl':775, 'yu':1050, 
                                    'inset_pars':{'loc': 4, 'width':4, 'height':4, 'bbox_to_anchor':(1050,50,0,600)},
                                    'mark_inset_pars':{'loc1':3, 'loc2':2,},
                                    'vis_pars':{'max_percent':99.87, 'min_percent': 1.0, 'stretch':'asinh'}
                                   },

                                  ]
zoom_parameters[('W43MM1', 'B3')] = [{'xl':1300, 'xr':1700, 'yl':1225, 'yu':1650, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':(1175,25,0,550), },
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.0, 'stretch':'asinh'}
                                   },
                                  #{'xl':2325, 'xr':2600, 'yl':775, 'yu':1050, 
                                  # 'inset_pars':{'loc': 4, 'width':4, 'height':4, 'bbox_to_anchor':(1050,50,0,600)},
                                  # 'mark_inset_pars':{'loc1':3, 'loc2':2,},
                                  # 'vis_pars':{'max_percent':99.87, 'min_percent': 1.0, 'stretch':'asinh'}
                                  #},

                                  ]                                  
zoom_parameters[('W43MM1', 'B6')] = [{'xl':700, 'xr':1100, 'yl':775, 'yu':1175, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':6, 'bbox_to_anchor':(1175,25,0,550), },
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                  ]     


zoom_parameters[('G351', 'B6')] = [{'xl':320, 'xr':500, 'yl':360, 'yu':550, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(800, 20, 300, 700),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   ]

#zoom_parameters[('G338', 'B6')] = [{'xl':400, 'xr':600, 'yl':400, 'yu':575, 
#                                    'inset_pars':{'loc': 1, 'width':3, 'height':3,},
#                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
#                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
#                                   },
#                                   {'xl':435, 'xr':550, 'yl':150, 'yu':265, 
#                                    'inset_pars':{'loc': 3, 'width':3, 'height':3,},
#                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
#                                    'vis_pars':{'max_percent':99.995, 'min_percent': 1, 'stretch':'log'}
#                                   },
#                                  ]
zoom_parameters[('G338', 'B6')] = [{'xl':365, 'xr':625, 'yl':160, 'yu':570, 
                                    'inset_pars':{'loc': 4, 'width':7, 'height':7, 'bbox_to_anchor':(820, 100, 300, 700),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('G328', 'B6')] = [{'xl':450, 'xr':600, 'yl':500, 'yu':800, 
                                    'inset_pars':{'loc': 4, 'width':7, 'height':7, 'bbox_to_anchor':(1030, 120, 100, 100),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   {'xl':435, 'xr':650, 'yl':920, 'yu':1030, 
                                    'inset_pars':{'loc': 1, 'width':5, 'height':5, 'bbox_to_anchor':(450, 850, 100,100),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.95, 'min_percent': 0, 'stretch':'linear'}
                                   },
                                  ]
zoom_parameters[('G333', 'B6')] = [{'xl':450, 'xr':1000, 'yl':475, 'yu':830, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(240, 280, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':435, 'xr':650, 'yl':920, 'yu':1030, 
                                   # 'inset_pars':{'loc': 1, 'width':3, 'height':3, 'bbox_to_anchor':(450, 850, 100,100),},
                                   # 'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                   # 'vis_pars':{'max_percent':99.95, 'min_percent': 0, 'stretch':'linear'}
                                   #},
                                  ]
zoom_parameters[('G12', 'B6')] = [{'xl':270, 'xr':450, 'yl':340, 'yu':460, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(250, 280, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':435, 'xr':650, 'yl':920, 'yu':1030, 
                                   # 'inset_pars':{'loc': 1, 'width':3, 'height':3, 'bbox_to_anchor':(450, 850, 100,100),},
                                   # 'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                   # 'vis_pars':{'max_percent':99.95, 'min_percent': 0, 'stretch':'linear'}
                                   #},
                                  ]
zoom_parameters[('G327', 'B6')] = [{'xl':335, 'xr':575, 'yl':460, 'yu':630, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(270, 300, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]

zoom_parameters[('G10', 'B6')] = [{'xl':365, 'xr':625, 'yl':360, 'yu':570, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(270, 300, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('G337', 'B6')] = [{'xl':365, 'xr':625, 'yl':160, 'yu':570, 
                                    'inset_pars':{'loc': 1, 'width':7, 'height':7, 'bbox_to_anchor':(550, 0, 600, 630),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]

zoom_parameters[('G351', 'B6')] = [{'xl':320, 'xr':500, 'yl':330, 'yu':550, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(820, 0, 300, 600),},
                                    'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('G353', 'B6')] = [{'xl':220, 'xr':520, 'yl':360, 'yu':550, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(300, 260, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]

zoom_parameters[('W43MM2', 'B6')] = [{'xl':520, 'xr':720, 'yl':550, 'yu':790, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(780, 0, 300, 550),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':2,},
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('W43MM3', 'B6')] = [{'xl':330, 'xr':500, 'yl':450, 'yu':580, 
                                    'inset_pars':{'loc': 1, 'width':6, 'height':5, 'bbox_to_anchor':(260, 300, 300, 700),},
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.999, 'min_percent': 0.1, 'stretch':'log'}
                                   },
                                   #{'xl':550, 'xr':750, 'yl':160, 'yu':360, 
                                   # 'inset_pars':{'loc': 1, 'width':4, 'height':4, 'bbox_to_anchor':(1000, 300, 100,100),},
                                   # 'mark_inset_pars':{'loc1':2, 'loc2':3,},
                                   # 'vis_pars':{'max_percent':99.7, 'min_percent': 1, 'stretch':'log'}
                                   #},
                                  ]
zoom_parameters[('G008', 'B6')] = [{'xl':750, 'xr':1000, 'yl':250, 'yu':500, 
                                    'inset_pars':{'loc': 1, 'width':2.5, 'height':2.5, 'bbox_to_anchor':(0,0,560,580),
                                                  },
                                    'tick_locs': [-0.7, -0.4, 0, 1, 3, 10, 30, 165],
                                    'mark_inset_pars':{'loc1':3, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 3, 'stretch':'log'}
                                   },
                                   {'xl':250, 'xr':350, 'yl':475, 'yu':650, 
                                    'inset_pars':{'loc': 3, 'width':2.55, 'height':2.5,},
                                    'tick_locs': [-0.5, -0.25, 0, 0.5, 2, 10, 45],
                                    'tick_labels': [-0.5, -0.25, 0, 0.5, 2, 10, 45],
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_cut':45.0, 'min_cut': -0.5, 'stretch':'log'}
                                   },
                                  ]                                  


if __name__ == "__main__":
    import os
    import warnings

    os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/June2021Release/')
    
    pl.close(1)
    for band in ('B3','B6'):
        for fieldid in prefixes:
            print(fieldid, band)
            make_multifig(fieldid, band=band, inner_stretch='asinh', title=fieldid)

                
    pl.close('all')
    make_zoom('W43MM1', zoom_parameters[('W43MM1', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=15)
    make_zoom('W43MM3', zoom_parameters[('W43MM3', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=15)
    make_zoom('G351', zoom_parameters[('G351', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=25)
    make_zoom('G333', zoom_parameters[('G333', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=45)
    make_zoom('W43MM2', zoom_parameters[('W43MM2', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=15)
    make_zoom('W51-E', zoom_parameters[('W51-E', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=45)
    make_zoom('G353', zoom_parameters[('G353', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=45)
    make_zoom('G337', zoom_parameters[('G337', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, )

    make_zoom('G10', zoom_parameters[('G10', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, )
    make_zoom('G327', zoom_parameters[('G327', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, )
    make_zoom('W51IRS2', zoom_parameters[('W51IRS2', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=45)
    make_zoom('G12', zoom_parameters[('G12', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, nsigma_max=45)
    make_zoom('G328', zoom_parameters[('G328', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, )
    make_zoom('G338', zoom_parameters[('G338', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'}, )
    make_zoom('G008', zoom_parameters[('G008', 'B3')], band='B3',
            overview_vis_pars={'max_percent':99.5, 'min_percent':0.5, 'stretch':'asinh'},)
    make_zoom('G008', zoom_parameters[('G008', 'B6')], band='B6')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G338', zoom_parameters[('G338', 'B6')], band='B6',)# main_zoombox=(-200,1050,-200,1050))            
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G328', zoom_parameters[('G328', 'B6')], band='B6', nsigma_max=45)# main_zoombox=(0,1600,0,1110))4
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G333', zoom_parameters[('G333', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G12', zoom_parameters[('G12', 'B6')], band='B6', nsigma_max=45)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('W51IRS2', zoom_parameters[('W51IRS2', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G327', zoom_parameters[('G327', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G10', zoom_parameters[('G10', 'B6')], band='B6', nsigma_max=35)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G337', zoom_parameters[('G337', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G338', zoom_parameters[('G338', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G351', zoom_parameters[('G351', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('G353', zoom_parameters[('G353', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('W43MM2', zoom_parameters[('W43MM2', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('W43MM3', zoom_parameters[('W43MM3', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        make_zoom('W51-E', zoom_parameters[('W51-E', 'B6')], band='B6',)# main_zoombox=(0,1600,0,1110))

        make_zoom('W43MM1', zoom_parameters[('W43MM1', 'B6')], band='B6',
                  overview_vis_pars={'max_percent':99.75,
                                     'min_percent':1.5, 'stretch':'asinh'},
                  nsigma_max=45)        


    import glob

    for band in ('B3','B6'):
        for fieldid in prefixes:
            print(fieldid, band)
            for robust0fn in glob.glob('/orange/adamginsburg/ALMA_IMF/RestructuredImagingResults/{fieldid}/{band}/cleanest/{fieldid}_{band}_uid___A001_X1296_*_continuum_merged_12M_robust0_selfcal*_finaliter.image.tt0'):
                pfx = robust0fn.replace(".image.tt0","")

                make_robust_comparison(pfx, band=band, nsigma_linear_max=15, inner_stretch='asinh',
                                       finaliter_prefix=pfx)
