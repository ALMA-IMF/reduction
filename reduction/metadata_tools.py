import numpy as np
from taskinit import msmdtool, iatool
msmd = msmdtool()

def is_7m(ms):
    """
    Determine if a measurement set includes 7m data
    """
    msmd.open(ms)
    diameter = msmd.antennadiameter(0)['value']
    msmd.close()
    if diameter == 7.0:
        return True
    else:
        return False

def get_indiv_phasecenter(ms, field):
    """
    Get the phase center of an individual field in radians
    """
    msmd.open(ms)
    field_matches = np.array([fld == field for fld in msmd.fieldnames()], dtype=bool)
    field_ids, = np.where(field_matches)
    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids]
    mean_ra = np.mean([pc['m0']['value'] for pc in ptgctrs])
    mean_dec = np.mean([pc['m1']['value'] for pc in ptgctrs])
    csys = ptgctrs[0]['refer']
    msmd.close()

    return mean_ra, mean_dec, csys

def determine_phasecenter(ms, field):
    """
    Identify the correct phasecenter for the MS (apparently, if you don't do
    this, the phase center is set to some random pointing in the mosaic)
    """

    if isinstance(ms, list):
        results = [get_indiv_phasecenter(vis, field) for vis in ms]
        csys = results[0][2]

        mean_ra = np.mean([ra for ra, dec, csys in results])
        mean_dec = np.mean([dec for ra, dec, csys in results])
    else:
        mean_ra, mean_dec, csys = get_indiv_phasecenter(ms, field)

    return (csys, mean_ra*180/np.pi, mean_dec*180/np.pi)

def get_indiv_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    cen_ra, cen_dec = phasecenter

    msmd.open(ms)

    field_matches = np.array([fld == field for fld in msmd.fieldnames()], dtype=bool)
    field_ids, = np.where(field_matches)

    antsize = msmd.antennadiameter(0)['value'] # m
    # because we're working with line-split data, we assume the reffreq comes
    # from spw 0
    freq = msmd.reffreq(spw)['m0']['value'] # Hz
    # go a little past the first null in each direction
    primary_beam = 1.25 * freq/299792458.0 / antsize
    pb_pix = primary_beam / pixscale

    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids]
    furthest_ra_pix_plus = np.max([pc['m0']['value']*180/np.pi+pb_pix-cen_ra for pc in ptgctrs])
    furthest_ra_pix_minus = np.min([pc['m0']['value']*180/np.pi-pb_pix-cen_ra for pc in ptgctrs])
    furthest_dec_pix_plus = np.max([pc['m1']['value']*180/np.pi+pb_pix-cen_dec for pc in ptgctrs])
    furthest_dec_pix_minus = np.min([pc['m1']['value']*180/np.pi-pb_pix-cen_dec for pc in ptgctrs])

    msmd.close()

    dra,ddec = furthest_ra_pix_plus-furthest_ra_pix_minus, furthest_dec_pix_plus-furthest_dec_pix_minus

    # go to the next multiple of 20, since it will come up with _something_ when you do 6/5 or 5/4 * n
    return dra-(dra%20)+20, ddec-(ddec%20)+20


def determine_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    if isinstance(ms, list):
        results = [determine_imsize(vis, field, phasecenter, spw, pixscale) for vis in ms]

        dra = np.max([ra for ra, dec in results])
        ddec = np.max([dec for ra, dec in results])
    else:
        dra,ddec = [determine_imsize(vis, field, phasecenter, spw, pixscale) for vis in ms]

    return dra, ddec
