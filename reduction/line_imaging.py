"""
Line imaging script.  There needs to be a to_image.json file in the directory
this is run in.  The to_image.json file is produced by the split_windows.py
script.

You can set the following environmental variables for this script:
    CHANCHUNKS=<number>
        The chanchunks parameter for tclean.  Depending on the version, it may
        be acceptable to specify this as -1, or it has to be positive.  From inline
help in CASA 5.6.1: This parameter controls the number of chunks to split the cube into.
For now, please pick chanchunks so that nchan/chanchunks is an integer.
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only image
        fields with this name (e.g., "W43-MM1", "W51-E", etc.)
    BAND_NUMBERS=<band(s)>
        Image this/these bands.  Can be "3", "6", or "3,6" (no quotes)
    LINE_NAME=<name>
        Image only one line at each run.  Can be 'n2hp', 'CO' (Case insensitive)
    LOGFILENAME=<name>
        Optional.  If specified, the logger will use this filenmae
"""

import json
import os
import numpy as np
import astropy.units as u
from astropy import constants
try:
    from tasks import tclean, uvcontsub, impbcor, concat
    from taskinit import casalog
except ImportError:
    # futureproofing: CASA 6 imports this way
    from casatasks import tclean, uvcontsub, impbcor, concat
    from casatasks import casalog
from parse_contdotdat import parse_contdotdat, freq_selection_overlap
from metadata_tools import determine_imsizes, determine_phasecenter, is_7m, logprint
from imaging_parameters import line_imaging_parameters, selfcal_pars, line_parameters
from taskinit import msmdtool, iatool, mstool
from metadata_tools import effectiveResolutionAtFreq
from getversion import git_date, git_version
msmd = msmdtool()
ia = iatool()
ms = mstool()

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)

if os.getenv('LOGFILENAME'):
    casalog.setlogfile(os.path.join(os.getcwd(), os.getenv('LOGFILENAME')))


if os.getenv('FIELD_ID'):
    field_id = os.getenv('FIELD_ID')
    for band in to_image:
        to_image[band] = {key:value for key, value in to_image[band].items()
                          if key == field_id}
else:
    field_id = 'all'


if os.getenv('BAND_NUMBERS'):
    band_list = list(map(lambda x: "B"+x, os.getenv('BAND_NUMBERS').split(',')))
    for BB in band_list:
        if BB not in to_image:
            raise ValueError("Band {0} was specified but is not in to_image.json"
                             .format(BB))
else:
    band_list = list(to_image.keys())

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

if 'exclude_7m' not in locals():
    if os.getenv('EXCLUDE_7M') is not None:
        exclude_7m = bool(os.getenv('EXCLUDE_7M').lower() == 'true')
    else:
        exclude_7m = False

if os.getenv('LINE_NAME'):
    line_name = os.getenv('LINE_NAME').lower()
else:
    raise ValueError("line_name was not defined")

if 'do_contsub' not in locals():
    if os.getenv('DO_CONTSUB') is not None:
        do_contsub = bool(os.getenv('DO_CONTSUB').lower() == 'true')
    else:
        do_contsub = False
if do_contsub:
    contsub_suffix = '.contsub'
else:
    contsub_suffix = ''

# set the 'chanchunks' parameter globally.
# CASAguides recommend chanchunks=-1, but this resulted in: 2018-09-05 23:16:34     SEVERE  tclean::task_tclean::   Exception from task_tclean : Invalid Gridding/FTM Parameter set : Must have at least 1 chanchunk
chanchunks = int(os.getenv('CHANCHUNKS') or 16)


def set_impars(impars, line_name, vis):
    if line_name not in ('full', ) + spwnames:
        local_impars = {}
        if 'width' in linpars:
            local_impars['width'] = linpars['width']
        else:
            # calculate the channel width
            chanwidths = []
            for vv in vis:
                msmd.open(vv)
                count_spws = len(msmd.spwsforfield(field))
                chanwidth = np.max([np.abs(
                    effectiveResolutionAtFreq(vv,
                                              spw='{0}'.format(i),
                                              freq=u.Quantity(linpars['restfreq']).to(u.GHz),
                                              kms=True)) for i in
                    range(count_spws)])

                # second awful check b/c Todd's script failed for some cases
                for spw in range(count_spws):
                    chanwidths_hz = msmd.chanwidths(int(spw))
                    chanfreqs_hz = msmd.chanfreqs(int(spw))
                    ckms = constants.c.to(u.km/u.s).value
                    if any(chanwidths_hz > (chanwidth / ckms)*chanfreqs_hz):
                        chanwidth = np.max(chanwidths_hz/chanfreqs_hz * ckms)
                msmd.close()

                chanwidths.append(chanwidth)

            # chanwidth: mean? max?
            chanwidth = np.mean(chanwidths)
            logprint("Channel widths were {0}, mean = {1}".format(chanwidths,
                                                                  chanwidth),
                     origin="almaimf_line_imaging")
            if np.any(np.array(chanwidths) - chanwidth > 1e-4):
                raise ValueError("Varying channel widths.")
            local_impars['width'] = '{0:.2f}km/s'.format(np.round(chanwidth, 2))

        local_impars['restfreq'] = linpars['restfreq']
        # calculate vstart
        vstart = u.Quantity(linpars['vlsr'])-u.Quantity(linpars['cubewidth'])/2
        local_impars['start'] = '{0:.1f}km/s'.format(vstart.value)
        local_impars['chanchunks'] = int(chanchunks)

        local_impars['nchan'] = int((u.Quantity(line_parameters[field][line_name]['cubewidth'])
                                    / u.Quantity(local_impars['width'])).value)
        if local_impars['nchan'] < local_impars['chanchunks']:
            local_impars['chanchunks'] = local_impars['nchan']
        impars.update(local_impars)
    else:
        impars['chanchunks'] = int(chanchunks)




# global default: only do robust 0 for lines
robust = 0

logprint("Initializing line imaging with global parameters"
         " exclude_7m={0}, band_list={1}, field_id={2}"
         .format(exclude_7m, band_list, field_id),
         origin='almaimf_line_imaging')

for band in band_list:
    for field in to_image[band]:
        spwnames = tuple('spw{0}'.format(x) for x in to_image[band][field])
        logprint("Found spectral windows {0} in band {1}: field {2}"
                 .format(to_image[band][field].keys(), band, field),
                 origin='almaimf_line_imaging')
        for spw in to_image[band][field]:

            # python 2.7 specific hack: force 'field' to be a bytestring
            # instead of a unicode string (CASA's lower-level functions
            # can't accept unicode strings)
            field = str(field)
            spw = str(spw)
            band = str(band)

            vis = list(map(str, to_image[band][field][spw]))

            # load in the line parameter info
            if line_name not in ('full', ) + spwnames:
                linpars = line_parameters[field][line_name]
                restfreq = u.Quantity(linpars['restfreq'])
                vlsr = u.Quantity(linpars['vlsr'])

                # check that the line is in range
                ms.open(vis[0])
                # assume spw is 0 because we're working on split data
                freqs = ms.cvelfreqs(spwids=0, outframe='LSRK') * u.Hz
                targetfreq = restfreq * (1 - vlsr/constants.c)
                if freqs.min() > targetfreq or freqs.max() < targetfreq:
                    # Skip this spw: it is not in range
                    logprint("Skipped spectral window {0} for line {1}"
                             " with frequency {2} because it's out of range"
                             .format(spw, line_name, targetfreq),
                             origin='almaimf_line_imaging')
                    continue
                else:
                    logprint("Matched spectral window {0} to line {1}"
                             .format(spw, line_name),
                             origin='almaimf_line_imaging')
            elif line_name in spwnames and line_name.lstrip("spw") != spw:
                logprint("Skipped spectral window {0} because it's not {1}"
                         .format(spw, line_name),
                         origin='almaimf_line_imaging')
                continue


            if exclude_7m:
                # don't use variable name 'ms' in python2.7!
                vis = [ms_ for ms_ in vis if not is_7m(ms_)]
                arrayname = '12M'
            else:
                arrayname = '7M12M'




            # concatenate MSes prior to imaging
            basename = "{0}_{1}_spw{2}_{3}".format(field, band, spw, arrayname)

            basepath = os.path.dirname(vis[0])
            assert os.path.split(basepath)[-1] == 'calibrated'
            concatvis = os.path.join(basepath, basename+".concat.ms")
            assert 'calibrated' in concatvis
            if not os.path.exists(concatvis):
                logprint("Concatenating visibilities {vis} into {concatvis}"
                         .format(vis=vis, concatvis=concatvis),
                         origin='almaimf_line_imaging'
                        )
                concat(vis=vis, concatvis=concatvis)

            if do_contsub:
                # the cont_channel_selection is purely in frequency, so it should
                # "just work"
                # (there may be several cont.dats - we're just grabbing the first)
                # Different data sets are actually found to have different channel selections.
                path = os.path.split(vis[0])[0]

                contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                        "{field}.{band}.cont.dat".format(field=field, band=band))
                if not os.path.exists(contfile):
                    contfile = os.path.join(path, '../calibration/cont.dat')

                cont_freq_selection = parse_contdotdat(contfile)
                logprint("Selected {0} as continuum channels".format(cont_freq_selection), origin='almaimf_line_imaging')

                if not os.path.exists(concatvis+".contsub"):
                    # ALTERNATIVE, manual selection
                    msmd.open(concatvis)
                    spws = msmd.spwsforfield(field)
                    msmd.close()
                    new_freq_selection = ",".join([
                        freq_selection_overlap(ms=concatvis,
                                               freqsel=cont_freq_selection,
                                               spw=spw)
                        for spw in spws])
                    # Let CASA decide: All spws, here's the freqsel.  Go.
                    # (this does not work)
                    # new_freq_selection = '*:'+cont_freq_selection
                    uvcontsub(vis=concatvis,
                              fitspw=new_freq_selection,
                              excludechans=False, # fit the regions specified in fitspw
                              combine='none', # DO NOT combine spws for continuum ID (since that implies combining 7m <-> 12m)
                              solint='int', # fit each integration (may be noisy?)
                              fitorder=1,
                              want_cont=False)

                # if do_contsub, we want to use the contsub'd MS
                concatvis = concatvis + contsub_suffix

            lineimagename = os.path.join(imaging_root,
                                         "{0}_{1}_spw{2}_{3}_{4}{5}"
                                         .format(field, band, spw, arrayname,
                                                 line_name, contsub_suffix))

            logprint("Measurement sets are: " + str(concatvis),
                     origin='almaimf_line_imaging')
            coosys, racen, deccen = determine_phasecenter(ms=concatvis,
                                                          field=field)
            phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
            (dra, ddec, pixscale) = list(determine_imsizes(mses=concatvis,
                                                           field=field,
                                                           phasecenter=(racen, deccen),
                                                           spw='all',
                                                           pixfraction_of_fwhm=1/3.,
                                                           exclude_7m=exclude_7m,
                                                           min_pixscale=0.1, # arcsec
                                                          ))
            imsize = [int(dra), int(ddec)]
            cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

            dirty_tclean_made_residual = False


            # prepare for the imaging parameters
            pars_key = "{0}_{1}_{2}_robust{3}{4}".format(field, band,
                                                         arrayname, robust,
                                                         contsub_suffix.replace(".", "_"))
            impars = line_imaging_parameters[pars_key]

            set_impars(impars=impars, line_name=line_name, vis=vis)

            impars['imsize'] = imsize
            impars['cell'] = cellsize
            impars['phasecenter'] = phasecenter
            impars['field'] = [field.encode()]

            # start with cube imaging
            # step 1 is dirty imaging

            if not os.path.exists(lineimagename+".image") and not os.path.exists(lineimagename+".residual"):
                if os.path.exists(lineimagename+".psf"):
                    logprint("WARNING: The PSF for {0} exists, but no image exists."
                             "  This likely implies that an ongoing or incomplete "
                             "imaging run for this file exists.  It will not be "
                             "imaged this time; please check what is happening.  "
                             "(this warning issued /before/ dirty imaging)"
                             .format(lineimagename),
                             origin='almaimf_line_imaging')
                    continue
                # first iteration makes a dirty image to estimate the RMS
                impars_dirty = impars.copy()
                impars_dirty['niter'] = 0

                logprint("Dirty imaging parameters are {0}".format(impars_dirty),
                         origin='almaimf_line_imaging')
                tclean(vis=concatvis,
                       imagename=lineimagename,
                       restoringbeam='', # do not use restoringbeam='common'
                       # it results in bad edge channels dominating the beam
                       **impars_dirty
                      )
                for suffix in ('image', 'residual', 'model'):
                    ia.open(lineimagename+"."+suffix)
                    ia.sethistory(origin='almaimf_line_imaging',
                                  history=["{0}: {1}".format(key, val) for key, val in
                                           impars_dirty.items()])
                    ia.sethistory(origin='almaimf_line_imaging',
                                  history=["git_version: {0}".format(git_version),
                                           "git_date: {0}".format(git_date)])
                    ia.close()

                if os.path.exists(lineimagename+".image"):
                    # tclean with niter=0 is not supposed to produce a .image file,
                    # but if it does (and it appears to have done so on at
                    # least one run), we still want to clean the cube
                    dirty_tclean_made_residual = True
            elif not os.path.exists(lineimagename+".residual"):
                raise ValueError("The residual image is required for further imaging.")
            else:
                logprint("Found existing files matching {0}".format(lineimagename),
                         origin='almaimf_line_imaging'
                        )

            if os.path.exists(lineimagename+".psf") and not os.path.exists(lineimagename+".image"):
                logprint("WARNING: The PSF for {0} exists, but no image exists."
                         "  This likely implies that an ongoing or incomplete "
                         "imaging run for this file exists.  It will not be "
                         "imaged this time; please check what is happening."
                         "(warning issued /after/ dirty imaging)"
                         .format(lineimagename),
                         origin='almaimf_line_imaging')
                # just skip the rest here
                continue

            # the threshold needs to be computed if any imaging is to be done (either contsub or not)
            # no .image file is produced, only a residual
            logprint("Computing residual image statistics for {0}".format(lineimagename),
                     origin='almaimf_line_imaging')
            ia.open(lineimagename+".residual")
            stats = ia.statistics(robust=True)
            rms = float(stats['medabsdevmed'] * 1.482602218505602)
            ia.close()

            if rms >= 1:
                raise ValueError("RMS was {0} - that's absurd.".format(rms))
            if rms > 0.01:
                logprint("The RMS found was pretty high: {0}".format(rms),
                         origin='almaimf_line_imaging')

            continue_imaging = False
            nsigma = None
            if 'threshold' in impars:
                if 'sigma' in impars['threshold']:
                    nsigma = int(impars['threshold'].strip('sigma'))
                    threshold = "{0:0.4f}Jy".format(nsigma*rms) # 3 rms might be OK in practice
                    logprint("Threshold used = {0} = {2}x{1}".format(threshold, rms, nsigma),
                             origin='almaimf_line_imaging')
                    impars['threshold'] = threshold
                else:
                    threshold = impars['threshold']
                    nsigma = (u.Quantity(threshold) / rms).to(u.Jy).value
                    logprint("Manual threshold used = {0} = {2}x{1}"
                             .format(threshold, rms, nsigma),
                             origin='almaimf_line_imaging')

                if u.Quantity(threshold).to(u.Jy).value < stats['max']:
                    logprint("Threshold {0} was not reached (peak residual={1}).  "
                             "Continuing imaging.".format(threshold, stats['max']),
                             origin='almaimf_line_imaging'
                            )
                    # if the threshold was not reached, keep cleaning
                    continue_imaging = True

            if continue_imaging or dirty_tclean_made_residual or not os.path.exists(lineimagename+".image"):
                # continue imaging using a threshold
                logprint("Imaging parameters are {0}".format(impars),
                         origin='almaimf_line_imaging')
                tclean(vis=concatvis,
                       imagename=lineimagename,
                       restoringbeam='', # do not use restoringbeam='common'
                       # it results in bad edge channels dominating the beam
                       **impars
                      )
                for suffix in ('image', 'residual', 'model'):
                    ia.open(lineimagename+"."+suffix)
                    ia.sethistory(origin='almaimf_line_imaging',
                                  history=["{0}: {1}".format(key, val) for key, val in
                                           impars.items()])
                    ia.sethistory(origin='almaimf_line_imaging',
                                  history=["nsigma: {0}".format(nsigma)])
                    ia.sethistory(origin='almaimf_line_imaging',
                                  history=["git_version: {0}".format(git_version),
                                           "git_date: {0}".format(git_date)])
                    ia.close()

                impbcor(imagename=lineimagename+'.image',
                        pbimage=lineimagename+'.pb',
                        outfile=lineimagename+'.image.pbcor', overwrite=True)


            logprint("Completed {0}->{1}".format(vis, concatvis), origin='almaimf_line_imaging')


logprint("Completed line_imaging.py run", origin='almaimf_line_imaging')
