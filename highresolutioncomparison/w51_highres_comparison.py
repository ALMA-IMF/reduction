"""
I don't remember what I originally made this for, but it is a nice proof that
we _will_ see high multiplicity on smaller scales than the ALMA-IMF data
provide.
"""
import numpy as np
from astropy.table import Table
from astropy import units as u
from astropy import coordinates
import pylab as pl
from astropy.io import fits
from astropy import wcs
import astropy.visualization
from astropy.convolution import convolve, Gaussian2DKernel
from mpl_plot_templates import asinh_norm
import matplotlib
from collections import defaultdict
import warnings
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

psf_center = coordinates.SkyCoord('19:23:43.5 -14:30:20',
                                  unit=(u.h, u.deg),
                                  frame='icrs')



zoomregions = {'eSmm2':
               {'bottomleft': coordinates.SkyCoord('19:23:43.823',
                                                   '+14:30:21.814',
                                                   unit=(u.h, u.deg),
                                                   frame='icrs'),
                'topright': coordinates.SkyCoord('19:23:43.743',
                                                 '+14:30:22.857',
                                                 unit=(u.h, u.deg),
                                                 frame='icrs'),
                'inregion': 'W51e',
                'bbox':[0.26,0.43],
                'loc': 2,
                'l1':4,
                'l2':1,
                'min': -0.0005,
                'max': 0.004,
                'zoom': 0.45,
               },
               'e8s':
               {'bottomleft': coordinates.SkyCoord('19:23:43.915',
                                                   '+14:30:27.164',
                                                   unit=(u.h, u.deg),
                                                   frame='icrs'),
                'topright': coordinates.SkyCoord('19:23:43.884',
                                                 '+14:30:27.828',
                                                 unit=(u.h, u.deg),
                                                 frame='icrs'),
                'inregion': 'W51e',
                'bbox':[0.26,0.9],
                'loc': 2,
                'l1':3,
                'l2':1,
                'min': -0.0005,
                'max': 0.005,
                'zoom': 0.45,
               },
              }

def mark_inset_specify_transforms(parent_axes, inset_axes, loc1, loc2,
                                  transform=None,
                                  **kwargs):

    if transform is None:
        transform = parent_axes.transData

    from matplotlib.transforms import TransformedBbox
    from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector

    print('viewlims: ', inset_axes.viewLim,
          transform.transform(inset_axes.viewLim))
    rect = TransformedBbox(inset_axes.viewLim, transform)

    fill = kwargs.pop("fill", False)
    pp = BboxPatch(rect, fill=fill, **kwargs)
    parent_axes.add_patch(pp)

    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1, **kwargs)
    inset_axes.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2, **kwargs)
    inset_axes.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2

def inset_overlays(fn, zoomregions, fignum=1,
                   fnzoom=None,
                   psffn=None,
                   vmin=-0.001, vmax=0.01,
                   bottomleft=None,
                   topright=None,
                   tick_fontsize=pl.rcParams['axes.labelsize']):

    hdu = fits.open(fn)[0]
    print(fn)

    mywcs = wcs.WCS(hdu.header).celestial

    figure = pl.figure(fignum)
    figure.clf()
    ax = figure.add_axes([0.15, 0.1, 0.8, 0.8], projection=mywcs)

    ra = ax.coords['ra']
    ra.set_major_formatter('hh:mm:ss.s')
    dec = ax.coords['dec']
    ra.set_axislabel("RA (ICRS)", fontsize=pl.rcParams['axes.labelsize'])
    dec.set_axislabel("Dec (ICRS)", fontsize=pl.rcParams['axes.labelsize'], minpad=0.0)
    ra.ticklabels.set_fontsize(tick_fontsize)
    ra.set_ticks(exclude_overlapping=True)
    dec.ticklabels.set_fontsize(tick_fontsize)
    dec.set_ticks(exclude_overlapping=True)


    im = ax.imshow(hdu.data.squeeze()*1e3,
                   transform=ax.get_transform(mywcs),
                   vmin=vmin*1e3, vmax=vmax*1e3, cmap=pl.cm.gray_r,
                   interpolation='nearest',
                   origin='lower', norm=asinh_norm.AsinhNorm())

    (x1,y1),(x2,y2) = (mywcs.wcs_world2pix([[bottomleft.ra.deg,
                                             bottomleft.dec.deg]],0)[0],
                       mywcs.wcs_world2pix([[topright.ra.deg,
                                             topright.dec.deg]],0)[0]
                      )

    # we'll want this later
    #make_scalebar(ax, scalebarpos,
    #              length=(0.5*u.pc / distance).to(u.arcsec,
    #                                              u.dimensionless_angles()),
    #              color='k',
    #              label='0.5 pc',
    #              text_offset=1.0*u.arcsec,
    #             )


    ax.set_aspect(1)
    ax.axis([x1,x2,y1,y2])


    if fnzoom is not None:
        hduzoom = fits.open(fnzoom)[0]
        wcszoom = wcs.WCS(hduzoom.header).celestial
    else:
        hduzoom = hdu
        wcszoom = mywcs

    for zoomregion in zoomregions:

        ZR = zoomregions[zoomregion]

        parent_ax = zoomregions[ZR['inset_axes']]['axins'] if 'inset_axes' in ZR else ax

        bl, tr = ZR['bottomleft'],ZR['topright'],
        (zx1,zy1),(zx2,zy2) = (wcszoom.wcs_world2pix([[bl.ra.deg,
                                                       bl.dec.deg]],0)[0],
                               wcszoom.wcs_world2pix([[tr.ra.deg,
                                                       tr.dec.deg]],0)[0]
                              )
        print(zoomregion,zx1,zy1,zx2,zy2)

        inset_data = hduzoom.data.squeeze()[int(zy1):int(zy2), int(zx1):int(zx2)]
        #inset_data = hdu.data.squeeze()
        inset_wcs = wcszoom.celestial[int(zy1):int(zy2), int(zx1):int(zx2)]
        #inset_wcs = mywcs

        axins = zoomed_inset_axes(parent_ax, zoom=ZR['zoom'], loc=ZR['loc'],
                                  bbox_to_anchor=ZR['bbox'],
                                  bbox_transform=figure.transFigure,
                                  axes_class=astropy.visualization.wcsaxes.core.WCSAxes,
                                  axes_kwargs=dict(wcs=inset_wcs))
        ZR['axins'] = axins
        imz = axins.imshow(inset_data,
                           #transform=parent_ax.get_transform(inset_wcs),
                           extent=[int(zx1), int(zx2), int(zy1), int(zy2)],
                           vmin=ZR['min'], vmax=ZR['max'], cmap=pl.cm.gray_r,
                           interpolation='nearest',
                           origin='lower', norm=asinh_norm.AsinhNorm())


        ax.axis([x1,x2,y1,y2])
        #axins.axis([zx1,zx2,zy1,zy2])
        #print(axins.axis())

        axins.set_xticklabels([])
        axins.set_yticklabels([])

        lon = axins.coords['ra']
        lat = axins.coords['dec']
        lon.set_ticklabel_visible(False)
        lat.set_ticklabel_visible(False)
        lon.set_ticks_visible(False)
        lat.set_ticks_visible(False)

        # draw a bbox of the region of the inset axes in the parent axes and
        # connecting lines between the bbox and the inset axes area
        mark_inset_specify_transforms(parent_axes=parent_ax, inset_axes=axins,
                                      transform=parent_ax.get_transform(wcszoom),
                                      loc1=ZR['l1'], loc2=ZR['l2'], fc="none",
                                      ec="0.5", lw=0.5)


        figure.canvas.draw()
        assert np.abs(ax.bbox._bbox.x1 - 0.95) > 1e-4

    cax = figure.add_axes([ax.bbox._bbox.x1+0.01, ax.bbox._bbox.y0, 0.02,
                           ax.bbox._bbox.y1-ax.bbox._bbox.y0])
    cb = figure.colorbar(mappable=im, cax=cax)
    #print("1. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))
    cb.set_label("$S_{1 mm}$ [mJy beam$^{-1}$]")
    #print("2. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))
    cb.formatter.format = "%3.1f"
    #print("3. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))
    cb.set_ticks(cb.formatter.locs)
    #print("4. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))
    cb.set_ticklabels(["{0:3.1f}".format(float(x)) for x in cb.formatter.locs])
    #print("5. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))
    cb.ax.set_yticklabels(["{0:3.1f}".format(float(x.get_text())) for x in cb.ax.get_yticklabels()])
    #print("6. cb labels: {0}".format([x.get_text() for x in cb.ax.get_yticklabels()]))



    if psffn is not None:
        psf = fits.open(psffn)
        psfwcs = wcs.WCS(psf[0].header)
        cx,cy = psfwcs.celestial.wcs_world2pix(psf_center.ra.deg, psf_center.dec.deg, 0)
        cx = int(cx)
        cy = int(cy)
        zy1 = cy-50
        zy2 = cy+50
        zx1 = cx-50
        zx2 = cx+50

        inset_wcs = psfwcs.celestial[zy1:zy2, zx1:zx2]
        inset_data = psf[0].data[cy-50:cy+50, cx-50:cx+50]

        axins = zoomed_inset_axes(parent_ax, zoom=10, loc=2,
                                  bbox_to_anchor=(0.05,0.25),
                                  bbox_transform=figure.transFigure,
                                  axes_class=astropy.visualization.wcsaxes.core.WCSAxes,
                                  axes_kwargs=dict(wcs=inset_wcs),
                                 )
        imz = axins.imshow(inset_data,
                           extent=[int(zx1), int(zx2), int(zy1), int(zy2)],
                           vmin=0, vmax=1, cmap=pl.cm.gray_r,
                           interpolation='nearest',
                           origin='lower', norm=asinh_norm.AsinhNorm())
        axins.contour(np.linspace(zx1, zx2, inset_data.shape[1]),
                      np.linspace(zy1, zy2, inset_data.shape[0]),
                      inset_data,
                      levels=[0.05, 0.1, 0.2, 0.3],
                      linewidths=[0.3]*10,
                      alpha=0.75,
                      #colors=['r']*10,
                     )
        axins.set_xticks([])
        axins.set_yticks([])
        axins.set_xticklabels([])
        axins.set_yticklabels([])
        lon = axins.coords['ra']
        lat = axins.coords['dec']
        lon.set_ticklabel_visible(False)
        lat.set_ticklabel_visible(False)
        lon.set_ticks_visible(False)
        lat.set_ticks_visible(False)


    return figure


if __name__ == "__main__":


    fn1 = 'W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust-2.image.tt0.pbcor.fits'
    fn2 = 'W51e2cax.cont.image.pbcor.fits.gz'


    figure = inset_overlays(fn=fn1, fnzoom=fn2, zoomregions=zoomregions,
                            vmin=-0.001, vmax=0.1,
                            bottomleft=coordinates.SkyCoord('19:23:44.300',
                                                       '14:30:18.313',
                                                       frame='icrs',
                                                       unit=(u.hour, u.deg),),
                            topright=coordinates.SkyCoord('19:23:43.467',
                                                       '14:30:30.978',
                                                       frame='icrs',
                                                       unit=(u.hour, u.deg),),
                           )
    figure.savefig('W51e8_zoomin.pdf', bbox_inches='tight', dpi=300)
    figure.savefig('W51e8_zoomin.png', bbox_inches='tight', dpi=300)


    figure = inset_overlays(fn=fn1, fnzoom=fn2,
                            zoomregions={k:v for k,v in zoomregions.items() if v['inregion'] == 'W51e2'},
                            vmin=-0.001, vmax=0.03,
                            #norm=pl.matplotlib.colors.LogNorm(), #visualizaiton.simple_norm(stretch='log', vmin=-0.001, vmax=0.2),
                            bottomleft=coordinates.SkyCoord('19:23:44.3',
                                                       '14:30:31.500',
                                                       frame='fk5',
                                                       unit=(u.hour, u.deg),),
                            topright=coordinates.SkyCoord('19:23:43.6',
                                                       '14:30:41.620',
                                                       frame='fk5',
                                                       unit=(u.hour, u.deg),),
                           )
    figure.savefig('W51e2_zoomin.pdf', bbox_inches='tight', dpi=300)
    figure.savefig('W51e2_zoomin.png', bbox_inches='tight', dpi=300)


