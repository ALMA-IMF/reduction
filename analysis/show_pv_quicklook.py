import numpy as np
import itertools
from astropy import constants
from astropy import units as u
from astropy import stats

import pylab as pl
from astropy import wcs
from mpl_toolkits.axes_grid1 import make_axes_locatable


def show_pv(hdu, origin=0*u.arcsec, vrange=None,
            vcen=5*u.km/u.s, imvmin=0, imvmax=1, contour=False,
            spectral_axis=0,
            ):

    data = hdu.data
    ww = wcs.WCS(hdu.header)

    if ww.spectral.wcs.cunit[0] == 'm/s':
        scalefactor = 1000.0
    else:
        scalefactor = 1.0

    #if vrange is None:
    #    vrange = ww.spectral.wcs_pix2world([0, data.shape[spectral_axis]], 0)

    #plotted_region = ww.wcs_world2pix([0,0],
    #                                  np.array(vrange)*scalefactor,
    #                                  0)
    #plotted_slice = (slice(int(np.min(plotted_region[1])), int(np.max(plotted_region[1]))),
    #                 slice(None,None),
    #                )

    fig = pl.figure(1, figsize=(8,8))
    fig.clf()
    ax = fig.add_axes([0.15, 0.1, 0.8, 0.8],projection=ww)
    assert ww.wcs.cunit[1] == 'm/s' # this is BAD BAD BAD but necessary

    # good_limits = (np.array((np.argmax(np.isfinite(data.max(axis=0))),
    #                          data.shape[1] -
    #                          np.argmax(np.isfinite(data.max(axis=0)[::-1])) - 1
    #                         ))
    #                )
    # leftmost_position = ww.wcs_pix2world(good_limits[0],
    #                                      vrange[0]*scalefactor,
    #                                      0)[0]*u.arcsec
    # rightmost_position = ww.wcs_pix2world(good_limits[1],
    #                                       vrange[0]*scalefactor,
    #                                       0)[0]*u.arcsec
    # assert rightmost_position > 0
    # maxdist = ((rightmost_position)*distance).to(u.au, u.dimensionless_angles())
    # assert maxdist > 0

    im = ax.imshow(data, cmap='gray_r',
                   #vmin=imvmin, vmax=imvmax*1.1,
                   interpolation='none')
    ax.set_xlabel("Offset [\"]")
    ax.set_ylabel("$V_{LSR}$ [km/s]")

    if contour:
        std_est = stats.mad_std(data, ignore_nan=True)
        print("Estimate of standard deviation: {0}".format(std_est))
        con = ax.contour(data, colors=[contour]*5,
                         levels=np.array([5,10,15,20,25])*std_est,
                         linewidths=0.75)
    else:
        con = None


    # vrange = [wcs.spectral.pixel_to_world(0).to(u.km/u.s),
    #           wcs.spectral.pixel_to_world(data.shape[spectral_axis]).to(u.km/u.s)]

    # ax.set_ylim(ww.wcs_world2pix(0,vrange[0]*scalefactor,0)[1],
    #             ww.wcs_world2pix(0,vrange[1]*scalefactor,0)[1])
    # ax.set_xlim(good_limits)

    aspect = 1*data.shape[1]/data.shape[0]
    ax.set_aspect(aspect)

    ax.coords[1].set_format_unit(u.km/u.s)
    ax.coords[0].set_format_unit(u.arcsec)
    #ax.coords[0].set_major_formatter('x.xx')

    cb = pl.colorbar(mappable=im)
    pl.draw()
    bb = ax.bbox._bbox
    cb.ax.set_position([bb.x1+0.03, bb.y0, 0.05, bb.y1-bb.y0])

    #ax.set_xlim(good_limits)
    ax.coords[0].set_ticklabel(exclude_overlapping=True, rotation=45, pad=45)

    return fig,ax,cb
