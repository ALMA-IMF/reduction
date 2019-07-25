import numpy as np
try:
    from casac import casac
    synthesisutils = casac.synthesisutils
    from taskinit import msmdtool, casalog, qatool, tbtool, mstool
except ImportError:
    from casatools import quanta as qatool, table as tbtool, msmetadata as msmdtool, synthesisutils, ms as mstool
    from casatasks import casalog
msmd = msmdtool()
ms = mstool()
qa = qatool()
st = synthesisutils()
tb = tbtool()

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

def get_indiv_imsize(ms, field, phasecenter, spw=0, pixfraction_of_fwhm=1/4.,
                     min_pixscale=0.05, only_7m=False, exclude_7m=False,
                     makeplot=False):
    """
    Parameters
    ----------
    min_pixscale : float
        Minimum allowed pixel scale in arcsec
    """

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

    logprint("Field IDs {0} matching field name {1} have scans."
             .format(field_ids[field_id_has_scans], field))

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

    # compute baselines to determine synth beamsize
    tb.open(ms+"/ANTENNA")
    positions = tb.getcol('POSITION')
    tb.close()

    # note that for concatenated MSes, this includes baselines that don't exist
    # (i.e., it includes baselines between TM1 and TM2 positions)
    baseline_lengths = (((positions[None,:,:]-positions.T[:,:,None])**2).sum(axis=1)**0.5)
    max_baseline = baseline_lengths.max()
    logprint("Maximum baseline length = {0}".format(max_baseline))

    antsize = np.array([msmd.antennadiameter(antid)['value']
                        for antid in first_antid]) # m

    if exclude_7m:
        assert 12 in antsize, "No 12m antennae found in ms {0}".format(ms)
        assert len(first_antid) == len(antsize) == len(first_scan_for_field) == len(field_ids[field_id_has_scans]) == (field_id_has_scans).sum()
        first_antid = [x for x,y in zip(first_antid, antsize) if y > 7]
        first_scan_for_field = [x for x,y in zip(first_scan_for_field, antsize) if y > 7]
        field_ids = np.array([x for x,y in zip(field_ids[field_id_has_scans], antsize) if y > 7])
        # this one is trivial: should be all True
        field_id_has_scans = np.array([x for x,y in zip(field_id_has_scans[field_id_has_scans], antsize) if y > 7])

        antsize = np.array([x for x in antsize if x > 7])
    elif only_7m:
        assert 7 in antsize, "No 7m antennae found in ms {0}".format(ms)
        assert len(first_antid) == len(antsize) == len(first_scan_for_field) == len(field_ids[field_id_has_scans]) == (field_id_has_scans).sum()
        first_antid = [x for x,y in zip(first_antid, antsize) if y == 7]
        first_scan_for_field = [x for x,y in zip(first_scan_for_field, antsize) if y == 7]
        field_ids = np.array([x for x,y in zip(field_ids[field_id_has_scans], antsize) if y == 7])
        # this one is trivial: should be all True
        field_id_has_scans = np.array([x for x,y in zip(field_id_has_scans[field_id_has_scans], antsize) if y == 7])

        antsize = np.array([x for x in antsize if x == 7])
    else:
        # the shape matters if any are false...
        field_id_has_scans = field_id_has_scans[field_id_has_scans]

    # because we're working with line-split data, we assume the reffreq comes
    # from spw 0
    freq = msmd.reffreq(spw)['m0']['value'] # Hz
    wavelength = 299792458.0/freq # m
    # go a little past the first null in each direction
    # (radians)
    primary_beam_fwhm = 1.22 * wavelength / antsize

    # synthesized beam minimum size (max_baseline in m)
    synthbeam_minsize_fwhm = 1.22 * wavelength / max_baseline
    # (radians)
    pixscale = pixfraction_of_fwhm * synthbeam_minsize_fwhm

    # round to nearest 0.01"
    if pixscale > 0.01/206265.:
        pixscale_as = np.floor((pixscale * 180/np.pi * 3600 * 100) % 100) / 100
        if pixscale_as < min_pixscale:
            pixscale_as = min_pixscale
        else:
            pixscale = pixscale_as * np.pi / 3600 / 180
        logprint("Pixel scale = {0} rad = {1} \" ".format(pixscale, pixscale_as))
    else:
        raise ValueError("Pixel scale was {0}\", too small".format(pixscale*206265))

    pb_pix = (primary_beam_fwhm / pixscale)[field_id_has_scans]


    def r2d(x):
        return x * 180 / np.pi

    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids[field_id_has_scans]]

    ptgctrs_ra_deg, ptgctrs_dec_deg = (np.array([r2d(zero_to_2pi(pc['m0']['value'])) for pc in ptgctrs]),
                                       np.array([r2d(pc['m1']['value']) for pc in ptgctrs]))
    pix_centers_ra = (ptgctrs_ra_deg - cen_ra) / r2d(pixscale)
    pix_centers_dec = (ptgctrs_dec_deg - cen_dec) / r2d(pixscale)

    furthest_ra_pix_plus = (pix_centers_ra+pb_pix).max()
    furthest_ra_pix_minus = (pix_centers_ra-pb_pix).min()
    furthest_dec_pix_plus = (pix_centers_dec+pb_pix).max()
    furthest_dec_pix_minus = (pix_centers_dec-pb_pix).min()

    if makeplot:
        import pylab as pl
        pl.figure(figsize=(10,10)).clf()
        pl.plot(pix_centers_ra, pix_centers_dec, 'o')
        circles = [pl.matplotlib.patches.Circle((x,y), radius=rad, facecolor='none', edgecolor='b')
                   for x,y,rad in zip(pix_centers_ra, pix_centers_dec, pb_pix)]
        collection = pl.matplotlib.collections.PatchCollection(circles)
        collection.set_facecolor('none')
        collection.set_edgecolor('r')
        pl.gca().add_collection(collection)
        pl.gca().axis([furthest_ra_pix_minus, furthest_ra_pix_plus,
                       furthest_dec_pix_minus, furthest_dec_pix_plus])


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
    # EDIT: instead, we'll use the st.getOptimumSize tool below
    #imsize = dra-(dra % 20)+20, ddec-(ddec % 20)+20
    imsize = int(dra), int(ddec)

    logprint("Determined imsize of individual ms {0} = {1} at center {2}"
             .format(ms, imsize, phasecenter))

    imsize_corrected = [st.getOptimumSize(x) for x in imsize]
    logprint("Optimized imsize is {0}".format(imsize_corrected))

    return imsize_corrected[0], imsize_corrected[1], pixscale_as


def determine_imsize(ms, field, phasecenter, spw=0, pixfraction_of_fwhm=1/4., **kwargs):

    logprint("Determining imsize of {0}".format(ms))

    if isinstance(ms, list):
        results = [get_indiv_imsize(vis, field, phasecenter, spw,
                                    pixfraction_of_fwhm, **kwargs)
                   for vis in ms]

        dra = np.max([ra for ra, dec, pixscale in results])
        ddec = np.max([dec for ra, dec, pixscale in results])
        pixscale = np.min([pixscale for ra, dec, pixscale in results])
    else:
        dra,ddec,pixscale = get_indiv_imsize(ms, field, phasecenter, spw,
                                             pixfraction_of_fwhm, **kwargs)

    # if the image is nearly square (to within 10%), make sure it is square.
    if np.abs(dra - ddec) / dra < 0.1:
        if dra < ddec:
            dra = ddec
        else:
            ddec = dra

    logprint("Determined imsize is {0},{1} w/scale {2}\"".format(dra,ddec,pixscale))

    return int(dra), int(ddec), pixscale

def determine_imsizes(mses, field, phasecenter, **kwargs):
    assert isinstance(mses, list)
    results = [determine_imsize(ms, field, phasecenter, **kwargs) for ms in mses]
    dra, ddec, _ = np.max(results, axis=0)
    _, _, pixscale = np.min(results, axis=0)

    logprint("ALL MSES: Determined imsize is {0},{1} w/scale {2}\"".format(dra,ddec,pixscale))

    return dra, ddec, pixscale

def check_model_is_populated(msfile):
    ms.open(msfile)
    modelphase = ms.getdata(items=['model_phase'])
    if 'model_phase' not in modelphase:
        raise ValueError("model_phase not acquired")
    if modelphase['model_phase'].shape == (0,):
        raise ValueError("Model phase column was not populated")
    ms.close()
