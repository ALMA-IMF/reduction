import numpy as np

from astropy.visualization import simple_norm
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector
import astropy.visualization.wcsaxes
from spectral_cube import SpectralCube
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
    image = SpectralCube.read(f'{finaliter_prefix}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube().to(u.mJy)
    print(image)

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
    ra.set_axislabel("RA (J2000)", fontsize=20)
    dec.set_axislabel("Dec (J2000)", fontsize=20, minpad=0.0)
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

        im_ins = axins.imshow(img[slc], extent=[xl,xr,yl,yu], cmap=inset_cmap, norm=norm2)
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


        if 'asinh' in str(norm.stretch).lower():
            rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=nticks_inset)
            cbins.set_ticks(rounded_loc)
            cbins.set_ticklabels(rounded)
        #elif 'log' in str(norm.stretch).lower() or 

        
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
                  ):
    
    pfxs = prefixes[fieldid]

    finaliter_prefix = pfxs[f'finaliter_prefix_{band}'.lower()]
    image = SpectralCube.read(f'{finaliter_prefix}.image.tt0.fits', use_dask=False, format='fits').minimal_subcube().to(u.mJy)

    fig = pl.figure(figsize=(12,12))

    fig = pl.figure(1, figsize=(10,10))
    fig.clf()
    ax = fig.add_subplot(projection=image.wcs.celestial)

    img = image[0].value

    img[img==0] = np.nan
    mad = mad_std(img, ignore_nan=True)

    norm = simple_norm(img, stretch='linear', min_cut=-nsigma_linear_min*mad, max_cut=nsigma_linear_max*mad,)

    im1 = ax.imshow(img, cmap=overview_cmap, norm=norm)
    
    cm = pl.cm.hot
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

    rounded_loc, rounded = determine_asinh_ticklocs(norm2.vmin, norm2.vmax, nticks=10)
    cb2.set_ticks(rounded_loc)
    cb2.set_ticklabels(rounded)
    print(f"old ticks: {ticklabels}, new ticks: {rounded}")


    tick_fontsize=16
    ra = ax.coords['ra']
    ra.set_major_formatter('hh:mm:ss.s')
    dec = ax.coords['dec']
    ra.set_axislabel("RA (J2000)", fontsize=20)
    dec.set_axislabel("Dec (J2000)", fontsize=20, minpad=0.0)
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

    
    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_multicolor_{band}.png', bbox_inches='tight')
    pl.savefig(f'/orange/adamginsburg/ALMA_IMF/datapaper/figures/{fieldid}_multicolor_{band}.pdf', bbox_inches='tight')

def determine_asinh_ticklocs(vmin, vmax, nticks):
    arcsinh_range = np.arcsinh(vmin), np.arcsinh(vmax)
    new_ticks = np.sinh(np.linspace(*arcsinh_range, nticks))
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

zoom_parameters = {}
zoom_parameters[('G008', 'B3')] = [{'xl':1500, 'xr':1900, 'yl':600, 'yu':1000, 
                                    'inset_pars':{'loc': 1, 'width':3, 'height':3,  'bbox_to_anchor':(600, 0, 100,100)},
                                    'mark_inset_pars':{'loc1':1, 'loc2':3,},
                                    'vis_pars':{'max_percent':99.995, 'min_percent': 0, 'stretch':'log'}
                                   },
                                   {'xl':700, 'xr':850, 'yl':1025, 'yu':1175, 
                                    'inset_pars':{'loc': 3, 'width':3, 'height':3,  'bbox_to_anchor':(0, -120, 100,100)},
                                    'mark_inset_pars':{'loc1':2, 'loc2':4,},
                                    'vis_pars':{'max_percent':99.9, 'min_percent': 2, 'stretch':'linear'}
                                   },
                                  ]