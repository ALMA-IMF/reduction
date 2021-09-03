import numpy as np
import os
import astropy.units as u
from astropy import constants
try:
    from casac import casac
    synthesisutils = casac.synthesisutils
    from taskinit import msmdtool, casalog, qatool, tbtool, mstool, iatool
    from tasks import tclean, flagdata
except ImportError:
    from casatools import (quanta as qatool, table as tbtool, msmetadata as
                           msmdtool, synthesisutils, ms as mstool,
                           image as iatool)
    from casatasks import casalog, tclean, flagdata
msmd = msmdtool()
ms = mstool()
qa = qatool()
st = synthesisutils()
tb = tbtool()
ia = iatool()

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
                     min_pixscale=0.02, only_7m=False, exclude_7m=False,
                     makeplot=False, veryverbose=False):
    """
    Parameters
    ----------
    min_pixscale : float
        Minimum allowed pixel scale in arcsec
    """

    logprint("Determining imsize of individual ms {0} spw {1}".format(ms, spw))

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
    diameters = tb.getcol('DISH_DIAMETER')
    tb.close()

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

        bl_sel = diameters != 7

        antsize = np.array([x for x in antsize if x > 7])
        logprint("Determining pixel scale and image size for only 12m data")
    elif only_7m:
        assert 7 in antsize, "No 7m antennae found in ms {0}".format(ms)
        assert len(first_antid) == len(antsize) == len(first_scan_for_field) == len(field_ids[field_id_has_scans]) == (field_id_has_scans).sum()
        first_antid = [x for x,y in zip(first_antid, antsize) if y == 7]
        first_scan_for_field = [x for x,y in zip(first_scan_for_field, antsize) if y == 7]
        field_ids = np.array([x for x,y in zip(field_ids[field_id_has_scans], antsize) if y == 7])
        # this one is trivial: should be all True
        field_id_has_scans = np.array([x for x,y in zip(field_id_has_scans[field_id_has_scans], antsize) if y == 7])

        bl_sel = diameters == 7

        antsize = np.array([x for x in antsize if x == 7])
        logprint("Determining pixel scale and image size for only 7m data")
    else:
        # the shape matters if any are false...
        field_id_has_scans = field_id_has_scans[field_id_has_scans]
        bl_sel = slice(None)
        logprint("Determining pixel scale and image size for all data, both 7m and 12m")

    # note that for concatenated MSes, this includes baselines that don't exist
    # (i.e., it includes baselines between TM1 and TM2 positions)
    baseline_lengths = (((positions[None,:,:]-positions.T[:,:,None])**2).sum(axis=1)**0.5)
    max_baseline = baseline_lengths[bl_sel,:][:,bl_sel].max()
    logprint("Maximum baseline length = {0}".format(max_baseline))

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
        pixscale_as = 180/np.pi * 3600 * pixscale
        pixscale_as = np.round(pixscale_as, 2)
        if pixscale_as < min_pixscale:
            logprint("Pixel scale was = {0} rad = {1} \", but is begin forced to min_pixscale={2} ".format(pixscale, pixscale_as/3600/180*np.pi, min_pixscale))
            pixscale_as = min_pixscale
        # re-set pixscale to be radians
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


    if veryverbose:
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

        if spw=='all':
            msmd.open(ms)
            spws = msmd.spwsforfield(field)
            msmd.close()

            logprint("Determining imsize of all spectral windows: {0}".format(spws))
            results = [get_indiv_imsize(ms, field, phasecenter, spw,
                                        pixfraction_of_fwhm, **kwargs)
                       for spw in spws]

            dra = np.max([ra for ra, dec, pixscale in results])
            ddec = np.max([dec for ra, dec, pixscale in results])
            pixscale = np.min([pixscale for ra, dec, pixscale in results])

        else:
            dra,ddec,pixscale = get_indiv_imsize(ms, field, phasecenter, spw,
                                                 pixfraction_of_fwhm, **kwargs)

    # if the image is nearly square (to within 10%), make sure it is square.
    if float(np.abs(dra - ddec)) / dra < 0.1:
        if dra < ddec:
            dra = ddec
        else:
            ddec = dra

    logprint("Determined imsize is {0},{1} w/scale {2}\"".format(dra,ddec,pixscale))

    return int(dra), int(ddec), pixscale

def determine_imsizes(mses, field, phasecenter, **kwargs):
    assert isinstance(mses, list),"Incorrect input to determine_imsizes"
    results = [determine_imsize(ms, field, phasecenter, **kwargs) for ms in mses]
    dra, ddec, _ = np.max(results, axis=0)
    _, _, pixscale = np.min(results, axis=0)

    logprint("ALL MSES: Determined imsize is {0},{1} w/scale {2}\"".format(dra,ddec,pixscale))

    return int(dra), int(ddec), pixscale

def check_model_is_populated(msfile):
    ms.open(msfile)
    modelphase = ms.getdata(items=['model_phase'])
    if 'model_phase' not in modelphase:
        raise ValueError("model_phase not acquired")
    if modelphase['model_phase'].shape == (0,):
        raise ValueError("Model phase column was not populated")
    ms.close()



def effectiveResolutionAtFreq(vis, spw, freq, kms=True):
    """
    Returns the effective resolution of a channel (in Hz or km/s)
    of the specified measurement set and spw ID.
    Note: For ALMA, this will only be correct for cycle 3 data onward.
    freq: frequency in quanity
    kms: if True, then return the value in km/s (otherwise Hz)
    To see this information for an ASDM, use
       printLOsFromASDM(showEffective=True)
    -Todd Hunter
    """
    if (not os.path.exists(vis+'/SPECTRAL_WINDOW')):
        raise ValueError("Could not find ms (or its SPECTRAL_WINDOW table).")
    mytb = tbtool()
    mytb.open(vis+'/SPECTRAL_WINDOW')
    if (type(spw) != list and type(spw) != np.ndarray):
        spws = [int(spw)]
    else:
        spws = [int(s) for s in spw]
    bws = []
    for spw in spws:
        chfreq = mytb.getcell('CHAN_FREQ',spw) # Hz
        sepfreq = np.abs(chfreq-freq.to(u.Hz).value)
        ind = np.where(sepfreq==sepfreq.min())
        bwarr = mytb.getcell('RESOLUTION',spw) # Hz
        bw = bwarr[ind]
        if kms:
            bw = constants.c.to(u.km/u.s).value*bw/freq.to(u.Hz).value
        bws.append(bw)
    mytb.close()
    if (len(bws) == 1):
        bws = bws[0]
    return bws

def test_tclean_success():
    # An EXTREMELY HACKY way to test whether tclean succeeded on the previous iteration
    with open(casalog.logfile(), "r") as fh:
        lines = fh.readlines()

    for line in lines[-5:]:
        if 'SEVERE  tclean::::      An error occurred running task tclean.' in line:
            raise ValueError("tclean failed.  See log for detailed error report.\n{0}".format(line))
        if 'SEVERE' in line:
            raise ValueError("SEVERE error message encountered: {0}".format(line))


def populate_model_column(imname, selfcal_ms, field, impars_thisiter,
                          phasecenter, maskname, antennae,
                          startmodel=''):
    # run tclean to repopulate the modelcolumn prior to gaincal
    # (force niter = 0 so we don't clean any more)


    # bugfix: for no reason at all, the reference frequency can change.
    # tclean chokes if it gets the wrong reffreq.
    ia.open(imname+".image.tt0")
    reffreq = "{0}Hz".format(ia.coordsys().referencevalue()['numeric'][3])
    ia.close()

    # have to remove mask for tclean to work
    os.system('rm -r {0}.mask'.format(imname))
    impars_thisiter['niter'] = 0
    logprint("(dirty) Imaging parameters are: {0}".format(impars_thisiter),
             origin='almaimf_cont_selfcal')
    logprint("This tclean run with zero iterations is only being done to "
             "populate the model column from image {0}.".format(imname),
             origin='almaimf_cont_selfcal')
    try:
        tclean(vis=selfcal_ms,
                     field=field.encode(),
                     imagename=imname,
                     phasecenter=phasecenter,
                     outframe='LSRK',
                     veltype='radio',
                     mask=maskname,
                     interactive=False,
                     antenna=antennae,
                     #reffreq=reffreq,
                     startmodel=startmodel,
                     savemodel='modelcolumn',
                     datacolumn='corrected',
                     pbcor=True,
                     calcres=True,
                     calcpsf=False,
                     **impars_thisiter
                    )
        test_tclean_success()
    except Exception as ex:
        print(ex)
        logprint("tclean FAILED with reffreq unspecified."
                 "  Trying again with reffreq={0}.".format(reffreq),
                 origin='almaimf_cont_selfcal')
        tclean(vis=selfcal_ms,
               field=field.encode(),
               imagename=imname,
               phasecenter=phasecenter,
               outframe='LSRK',
               veltype='radio',
               mask=maskname,
               interactive=False,
               antenna=antennae,
               reffreq=reffreq,
               startmodel=startmodel,
               savemodel='modelcolumn',
               datacolumn='corrected',
               pbcor=True,
               calcres=True,
               calcpsf=False,
               **impars_thisiter
              )
        test_tclean_success()

    # # even if this works, I hate it.
    # if not success:
    #     logprint("tclean FAILED with NO REFFREQ.  Trying again with a totally bullshit approach",
    #              origin='almaimf_cont_selfcal')
    #     modelname = [imname+".model.tt0",
    #                  imname+".model.tt1"]
    #     success = tclean(vis=selfcal_ms,
    #                      field=field.encode(),
    #                      imagename=imname+"_BULL",
    #                      phasecenter=phasecenter,
    #                      startmodel=modelname,
    #                      outframe='LSRK',
    #                      veltype='radio',
    #                      mask=maskname,
    #                      interactive=False,
    #                      cell=cellsize,
    #                      imsize=imsize,
    #                      antenna=antennae,
    #                      #reffreq=reffreq,
    #                      savemodel='modelcolumn',
    #                      datacolumn='corrected',
    #                      pbcor=True,
    #                      calcres=True,
    #                      calcpsf=True,
    #                      **impars_thisiter
    #                     )
    #if not success:
    #    # BACKUP PLAN: use ft instead of tclean [WRONG because it doesn't
    #    # use the same imager]
    #    modelname = [imname+".model.tt0",
    #                 imname+".model.tt1"]

    #    logprint("Using ``ft`` to populate the model column from {0}".format(modelname),
    #             origin='almaimf_cont_selfcal')
    #    success = ft(vis=selfcal_ms,
    #                 field=field.encode(),
    #                 model=modelname,
    #                 nterms=2,
    #                 usescratch=True
    #                )

    #    logprint("Completed ft with result={0} for image={1}"
    #             " populated model column".format(success, imname),
    #             origin='almaimf_cont_selfcal')

    #    # link ("copy") the current mask to be this round's mask
    #    # why am I doing this?  Isn't the mask always well-defined?
    #    # this can only introduce conflicts in the mask naming...
    #    # (maybe this was copied from ft above...)
    #    #os.system('ln -s {0} {1}.mask'.format(maskname, imname))


    # if not success:
    #     raise ValueError("tclean failed to restore the model {0}.model* "
    #                      "into the model column".format(imname))


def get_non_bright_spws(vis, frequency=230.538e9):
    """
    From a measurement set, return all spw numbers that do not contain the specified line
    
    Parameters
    ----------
    vis : str
        Measurement set name
    frequency : float
        Frequency of the line to exclude
    """
    
    msmd.open(vis)
    
    spws_ontarget = msmd.spwsforintent('OBSERVE_TARGET#ON_SOURCE')
    
    spws = []
    
    for spwnum in spws_ontarget:
        frqs = msmd.chanfreqs(spwnum)
        bws = msmd.chanwidths(spwnum)
        
        if ((frqs.min() - bws[0]) > frequency) or ((frqs.min().max() + bws[0]) < frequency):
            spws.append(spwnum)
    
    return spws


def sethistory(prefix, selfcalpars=None, impars=None, selfcaliter=None):
    from getversion import git_date, git_version
    for suffix in ('.image.tt0', '.image.tt0.pbcor', '.residual.tt0'):
        if os.path.exists(prefix+suffix):
            ia.open(prefix+suffix)
            if selfcalpars is not None:
                ia.sethistory(origin='almaimf_cont_selfcal',
                              history=["{0}: {1}".format(key, val) for key, val in
                                       selfcalpars.items()])
            if impars is not None:
                ia.sethistory(origin='almaimf_cont_selfcal',
                              history=["{0}: {1}".format(key, val) for key, val in
                                       impars.items()])
            if selfcaliter is not None:
                ia.sethistory(origin='almaimf_cont_selfcal',
                              history=["selfcaliter: {0}".format(selfcaliter)])
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["git_version: {0}".format(git_version),
                                   "git_date: {0}".format(git_date)])
            ia.close()
            ia.done()


def check_channel_flags(vis, tolerance=0, nchan_tolerance=10, **kwargs):
    flagsum = flagdata(vis=vis, mode='summary', spwchan=True, **kwargs)
    spws = set([int(key.split(":")[0]) for key in flagsum['spw:channel']])
    fractions_of_channels_flagged = {spwn: {int(key.split(":")[1]):
                                            flagsum['spw:channel'][key]['flagged']
                                            /
                                            flagsum['spw:channel'][key]['total']
                                            for key in
                                            flagsum['spw:channel'] if
                                            int(key.split(":")[0])
                                            == spwn }
                                     for spwn in spws}
    unique_fractions = {k:list(set(v.values())) for k,v in fractions_of_channels_flagged.items()}
    nunique_fractions = {k:[(np.array(list(v.values())) == vv).sum() for vv in unique_fractions[k]] for k,v in fractions_of_channels_flagged.items()}
    for spwn, nchanfracs in unique_fractions.items():
        if len(nchanfracs) != 1:
            if tolerance > 0:
                mostcommon = max(nunique_fractions[spwn])
                denominator = [frac for x, frac in zip(nunique_fractions[spwn], nchanfracs) if (x == mostcommon)][0]
                maxdiff = (max(nchanfracs) - min(nchanfracs)) / denominator

                if maxdiff < tolerance:
                    logprint("Visibility file {0} has {1}% flagged-out channels (within tolerance).".format(vis, maxdiff*100))
                else:
                    if nchan_tolerance > 0:
                        # count up the number of channels that exceed the tolerance
                        notmostcommon = [x for x, frac in zip(nunique_fractions[spwn], nchanfracs) if (x != mostcommon) and ((frac-min(nchanfracs))/denominator > tolerance)]
                        total_different = sum(notmostcommon)
                        if total_different < nchan_tolerance:
                            logprint("Visibility file {0} has at most {1} channels with differing flag % (maxdiff {3} is within tolerance {2}).".format(vis, total_different, tolerance, maxdiff))
                        else:
                            logprint("Visibility file {0} has at most {1} channels with differing flag % (maxdiff {3} is above tolerance {2}).".format(vis, total_different, tolerance, maxdiff))
                            leastcommon_ind = np.argmin(nunique_fractions[spwn])
                            discrepant_channels = sorted([key for key in
                                                   fractions_of_channels_flagged[spwn] if
                                                   fractions_of_channels_flagged[spwn][key] == unique_fractions[spwn][leastcommon_ind]])
                            logprint("The channels are: {0}".format(discrepant_channels))
                            raise ValueError("Spectral Window {0} of {1} has too many differing-flag channels".format(spwn, vis))
                    else:
                        logprint("Visibility file {0} has {1}% flagged-out channels (above tolerance).".format(vis, maxdiff*100))
                        raise ValueError("Spectral Window {0} of {1} has too many flagged out channels".format(spwn, vis))
            else:
                print("Spectral Window {0} of {1} has flagged out channels".format(spwn, vis))
                raise ValueError("Spectral Window {0} of {1} has flagged out channels".format(spwn, vis))

    logprint("Visibility file {0} has no flagged-out channels or f(flagged)<tolerance.".format(vis))
