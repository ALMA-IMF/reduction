from astropy import units as u

def hide_labels(ax):
    lon = ax.coords['RA']
    lat = ax.coords['Dec']

    lon.set_ticks_visible(False)
    lon.set_ticklabel_visible(False)
    lat.set_ticks_visible(False)
    lat.set_ticklabel_visible(False)
    lon.set_axislabel('')
    lat.set_axislabel('')

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

def hide_scalebar(sb):
    for line in sb[0]:
        line.set_visible(False)
    sb[1].set_visible(False)

def hide_labels_nonwcs(ax):
    for tt in ax.xaxis.get_ticklabels():
        tt.set_visible(False)
    for tt in ax.yaxis.get_ticklabels():
        tt.set_visible(False)
