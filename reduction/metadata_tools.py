import numpy as np
from taskinit import msmdtool, casalog, qatool
msmd = msmdtool()
qa = qatool()

def logprint(string, origin='almaimf_metadata',
             priority='INFO'):
    print(string)
    casalog.post(string, origin=origin, priority=priority)


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

# apparently the default location is negative radians, but tclean only
# accepts positive degrees
# we therefore force the value to be 0 < r < 2pi
def zero_to_2pi(x):
    while x < 0:
        x = x + 2*np.pi
    while x > 2*np.pi:
        x = x - 2*np.pi
    return x


def get_indiv_phasecenter(ms, field):
    """
    Get the phase center of an individual field in radians
    """
    logprint("Determining phasecenter of individual {0}".format(ms))

    msmd.open(ms)
    field_matches = np.array([fld == field for fld in msmd.fieldnames()],
                             dtype=bool)
    field_ids, = np.where(field_matches)

    # only use the field IDs that have associated scans
    field_id_has_scans = np.array([len(msmd.scansforfield(fid)) > 0
                                   for fid in field_ids], dtype='bool')

    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids[field_id_has_scans]]

    mean_ra = np.mean([zero_to_2pi(pc['m0']['value']) for pc in ptgctrs])
    mean_dec = np.mean([pc['m1']['value'] for pc in ptgctrs])
    csys = ptgctrs[0]['refer']
    msmd.close()

    logprint("Phasecenter of {0} is {1} {2} {3}".format(ms, mean_ra, mean_dec, csys))

    return mean_ra, mean_dec, csys


def determine_phasecenter(ms, field, formatted=False):
    """
    Identify the correct phasecenter for the MS (apparently, if you don't do
    this, the phase center is set to some random pointing in the mosaic)
    """
    logprint("Determining phasecenter of {0}".format(ms))

    if isinstance(ms, list):
        results = [get_indiv_phasecenter(vis, field) for vis in ms]
        csys = results[0][2]

        mean_ra = np.mean([ra for ra, dec, csys in results])
        mean_dec = np.mean([dec for ra, dec, csys in results])
    else:
        mean_ra, mean_dec, csys = get_indiv_phasecenter(ms, field)

    logprint("Determined phasecenter is {0} {1}deg {2}deg".format(csys,
                                                                  mean_ra*180/np.pi,
                                                                  mean_dec*180/np.pi))

    if formatted:
        return "{0} {1} {2}".format(csys,
                                    qa.angle({'value': mean_ra, 'unit': 'rad'}, form='tim')[0],
                                    qa.angle({'value': mean_dec, 'unit': 'rad'})[0])
    else:
        return (csys, mean_ra*180/np.pi, mean_dec*180/np.pi)

def get_indiv_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    logprint("Determining imsize of individual ms {0}".format(ms))

    cen_ra, cen_dec = phasecenter

    msmd.open(ms)

    field_matches = np.array([fld == field for fld in msmd.fieldnames()], dtype=bool)
    if not any(field_matches):
        raise ValueError("Did not find any matched for field {0}.  "
                         "The valid field names are {1}."
                         .format(field, msmd.fieldnames()))
    field_ids, = np.where(field_matches)
    logprint("Found field IDs {0} matching field name {1}."
             .format(field_ids, field))

    # only use the field IDs that have associated scans
    field_id_has_scans = np.array([len(msmd.scansforfield(fid)) > 0
                                   for fid in field_ids], dtype='bool')

    noscans = field_ids[~field_id_has_scans]
    if any(~field_id_has_scans):
        logprint("Found *scanless* field IDs {0} matching field name {1}."
                 .format(noscans, field))

    first_scan_for_field = [msmd.scansforfield(fid)[0]
                            for fid,fid_ok in zip(field_ids, field_id_has_scans)
                            if fid_ok
                           ]
    first_antid = [msmd.antennasforscan(scid)[0]
                   for scid in first_scan_for_field
                   if len(msmd.antennasforscan(scid)) > 0
                  ]

    antsize = np.array([msmd.antennadiameter(antid)['value']
                        for antid in first_antid]) # m
    # because we're working with line-split data, we assume the reffreq comes
    # from spw 0
    freq = msmd.reffreq(spw)['m0']['value'] # Hz
    # go a little past the first null in each direction
    # 1.46 is empirically determined from eyeballing one case
    primary_beam = 1.25 * freq/299792458.0 / antsize * 1.46
    pb_pix = primary_beam / pixscale


    def r2d(x):
        return x * 180 / np.pi

    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids[field_id_has_scans]]

    ptgctrs_ra_deg, ptgctrs_dec_deg = (np.array([r2d(zero_to_2pi(pc['m0']['value'])) for pc in ptgctrs]),
                                       np.array([r2d(pc['m1']['value']) for pc in ptgctrs]))
    pix_centers_ra = (ptgctrs_ra_deg - cen_ra) / (pixscale / 3600)
    pix_centers_dec = (ptgctrs_dec_deg - cen_dec) / (pixscale / 3600)

    furthest_ra_pix_plus = (pix_centers_ra+pb_pix).max()
    furthest_ra_pix_minus = (pix_centers_ra-pb_pix).min()
    furthest_dec_pix_plus = (pix_centers_dec+pb_pix).max()
    furthest_dec_pix_minus = (pix_centers_dec-pb_pix).min()

    logprint("RA/Dec degree centers and pixel centers of pointings are \n{0}\nand\n{1}"
             .format(list(zip(ptgctrs_ra_deg, ptgctrs_dec_deg)),
                     list(zip(pix_centers_ra, pix_centers_dec))))
    logprint("Furthest RA pixels from center are {0},{1}"
             .format(furthest_ra_pix_minus, furthest_ra_pix_plus))
    logprint("Furthest Dec pixels from center are {0},{1}"
             .format(furthest_dec_pix_minus, furthest_dec_pix_plus))

    msmd.close()

    dra,ddec = (furthest_ra_pix_plus-furthest_ra_pix_minus,
                furthest_dec_pix_plus-furthest_dec_pix_minus)

    # go to the next multiple of 20, since it will come up with _something_ when you do 6/5 or 5/4 * n
    imsize = dra-(dra % 20)+20, ddec-(ddec % 20)+20

    logprint("Determined imsize of individual ms {0} = {1} at center {2}"
             .format(ms, imsize, phasecenter))

    return imsize


def determine_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    logprint("Determining imsize of {0}".format(ms))

    if isinstance(ms, list):
        results = [get_indiv_imsize(vis, field, phasecenter, spw, pixscale) for vis in ms]

        dra = np.max([ra for ra, dec in results])
        ddec = np.max([dec for ra, dec in results])
    else:
        dra,ddec = get_indiv_imsize(ms, field, phasecenter, spw, pixscale)

    logprint("Determined imsize is {0},{1}".format(dra,ddec))

    return int(dra), int(ddec)
