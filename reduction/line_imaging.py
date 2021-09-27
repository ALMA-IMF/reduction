"""
Line imaging script.  There needs to be a to_image.json file in the directory
this is run in.  The to_image.json file is produced by the split_windows.py
script.

If you want to modify any of the environmental variables from _within_ python,
you must set them!  This can be done with, e.g.,

import os
os.environ['CHANCHUNKS'] = -1

These are the environmental variables you can set for this script:
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
        (you can specify this within python using "band_list=[3,6]" or "band_list=[3]")
    LINE_NAME=<name>
        Image only one line at each run.  Can be 'n2hp', 'CO', or other
        specified lines.   Can also a be a spw number (e.g., 'spw1'). (Case insensitive)
    LOGFILENAME=<name>
        Optional.  If specified, the logger will use this filenmae
    DO_CONTSUB=True / blank
        If specified, will continuum-subtract the measurement sets before
        imaging them.  A file metadata.json containing the paths to the
        cont.dat files is required in this case.
        metadata[band][field]['cont.dat'] = ['/path/to/cont.dat']
    WORK_DIRECTORY
        If the variable WORK_DIRECTORY is specified, the final measurement set
        after any concatenation/splitting will be copied to that directory,
        and all output files will be created in that directory.  If this is
        specified, then PRODUCT_DIRECTORY must also be specified - that's where
        the final image set will be moved to at the end.
        The MSes will be cleaned up (deleted) after imaging.
        This keyword is intended to help support work on computer systems
        where the storage and high-performance computing are on different
        machines.
    PRODUCT_DIRECTORY
        See WORK_DIRECTORY.  This is where the final products will be put.
    CONTINUE_IF_MS_EXISTS
        A boolean flag that only applies if both PRODUCT_DIRECTORY and
        WORK_DIRECTORY are set.  If this is not set, and the .ms file to
        clean from exists in WORK_DIRECTORY, an error will be raised and
        the script will fail.  If this is set, it will use that file.
    TEMP_WORKDIR
        A directory to do operations in when running the code; this will allow
        storage of temporary files.  This will be set automatically if not
        specified.
"""

import json
import os
import glob
import shutil
import numpy as np
import astropy.units as u
from astropy import constants
import re
try:
    from tasks import tclean, uvcontsub, impbcor, concat, flagdata
    from taskinit import casalog
    from exportfits_cli import exportfits_cli as exportfits
    from casa_system_defaults import casa
    from taskinit import msmdtool, iatool, mstool
    version = map(int, re.split("[-.]", casa['version']))
except (ImportError,ModuleNotFoundError):
    # futureproofing: CASA 6 imports this way
    from casatasks import tclean, uvcontsub, impbcor, concat, exportfits, flagdata
    from casatasks import casalog
    import casatools
    version = casatools.version()
    from casatools import msmetadata, image, ms as mstool
    msmdtool = msmetadata
    iatool = image
versionstring = ".".join(map(str, version))
from parse_contdotdat import parse_contdotdat, freq_selection_overlap, contchannels_to_linechannels
from metadata_tools import (determine_imsize, determine_phasecenter, is_7m,
                            logprint as logprint_, check_channel_flags)
from imaging_parameters import line_imaging_parameters, selfcal_pars, line_parameters, flag_thresholds
from unite_contranges import merge_contdotdat
from metadata_tools import effectiveResolutionAtFreq
from create_clean_model import create_clean_model
from getversion import git_date, git_version
msmd = msmdtool()
ia = iatool()
ms = mstool()

def logprint(msg, origin="almaimf_line_imaging", **kwargs):
    print(msg)
    return logprint_(msg, origin=origin, **kwargs)

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)

if os.getenv('LOGFILENAME'):
    casalog.setlogfile(os.path.join(os.getcwd(), os.getenv('LOGFILENAME')))

imaging_root = "imaging_results"
if os.getenv('PRODUCT_DIRECTORY') and os.getenv('WORK_DIRECTORY'):
    copy_files = True
    workdir = os.getenv('WORK_DIRECTORY') +"/"
    proddir = os.getenv('PRODUCT_DIRECTORY') +"/"
    imaging_root = workdir
    logprint("Using working directory {workdir} and product directory {proddir}"
             .format(workdir=workdir, proddir=proddir))
else:
    copy_files = False

if os.getenv('FIELD_ID'):
    if 'field_id' in locals():
        if os.getenv('FIELD_ID') is not None and os.getenv('FIELD_ID') != field_id:
            raise ValueError("Mismatch between ENVIRON field id {0} and field id {1}"
                             .format(os.getenv('FIELD_ID'), field_id))
        # else: all is good, go on
    else:
        field_id = os.getenv('FIELD_ID')
    for band in to_image:
        to_image[band] = {key:value for key, value in to_image[band].items()
                          if key == field_id}
else:
    field_id = 'all'

dryrun = bool(os.getenv('DRYRUN') or (dryrun if 'dryrun' in locals() else False))

if os.getenv('BAND_NUMBERS'):
    band_list = list(map(lambda x: "B"+x, os.getenv('BAND_NUMBERS').split(',')))
    for BB in band_list:
        if BB not in to_image:
            raise ValueError("Band {0} was specified but is not in to_image.json"
                             .format(BB))
elif 'band_list' not in locals():
    band_list = list(to_image.keys())

if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

if 'exclude_7m' not in locals():
    if os.getenv('EXCLUDE_7M') is not None:
        exclude_7m = bool(os.getenv('EXCLUDE_7M').lower() == 'true')
    else:
        exclude_7m = False

if 'only_7m' not in locals():
    if os.getenv('ONLY_7M') is not None:
        only_7m = bool(os.getenv('ONLY_7M').lower() == 'true')
    else:
        only_7m = False

if os.getenv('LINE_NAME'):
    line_name = os.getenv('LINE_NAME').lower()
elif 'line_name' not in locals():
    raise ValueError("line_name was not defined")

if 'do_contsub' not in locals():
    if os.getenv('DO_CONTSUB') is not None:
        do_contsub = bool(os.getenv('DO_CONTSUB').lower() == 'true')
    else:
        do_contsub = False
if do_contsub:
    contsub_suffix = '.contsub'

    # needed for cont.dat files
    with open('metadata.json', 'r') as fh:
        metadata = json.load(fh)
else:
    contsub_suffix = ''

if os.getenv('DO_NOT_CONCAT'):
    do_not_concat = os.getenv('DO_NOT_CONCAT').lower() != 'false'
    logprint("DO_NOT_CONCAT was set")
else:
    do_not_concat = False

if os.getenv('TEMP_WORKDIR'):
    temp_workdir = os.getenv('TEMP_WORKDIR')
else:
    temp_workdir = "_".join((field_id,
            line_name,
            ('7M' if only_7m else ('12M' if exclude_7m else '7M12M')),
            "_".join(band_list)
            ))
if not os.path.exists(temp_workdir):
    os.mkdir(temp_workdir)
logprint("Working in directory {0}".format(temp_workdir))
os.chdir(temp_workdir)

# hacky approach to paralellism
parallel = bool(os.getenv('MPICASA'))

# TODO: make this optional
do_export_fits = True

# set the 'chanchunks' parameter globally.
# CASAguides recommend chanchunks=-1, but this resulted in: 2018-09-05 23:16:34     SEVERE  tclean::task_tclean::   Exception from task_tclean : Invalid Gridding/FTM Parameter set : Must have at least 1 chanchunk
chanchunks = int(os.getenv('CHANCHUNKS') or 16)

# default: don't continue imaging
# (TODO: check whether we actually want to continue sometimes)
continue_imaging = False

def sethistory(prefix, nsigma=None, impars=None, suffixes=('.image', '.residual', '.model')):
    for suffix in suffixes:
        ia.open(prefix+suffix)
        if impars is not None:
            ia.sethistory(origin='almaimf_line_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
        if nsigma is not None:
            ia.sethistory(origin='almaimf_line_imaging',
                          history="nsigma: {0}".format(nsigma))
        ia.sethistory(origin='almaimf_line_imaging',
                      history=["git_version: {0}".format(git_version),
                               "git_date: {0}".format(git_date)])
        ia.sethistory(origin='almaimf_line_imaging',
                      history=['CASA version: {0}'.format(versionstring)])
        ia.close()
        ia.done()

def set_impars(impars, line_name, vis, linpars, spwnames=None):
    impars = impars.copy()
    if line_name not in ('full', ) + spwnames:
        local_impars = {}
        if 'width' in linpars:
            local_impars['width'] = linpars['width']
        elif 'restfreq' in linpars:
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
        else:
            raise ValueError("linpars (the line-specific parameters) were not set correctly")

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

    if 'nchan' in impars:
        # apparently you can't have nchan % chanchunks > 0
        cc = impars['chanchunks']
        while impars['nchan'] % cc > 0:
            cc -= 1
        impars['chanchunks'] = cc

    # support for chanchunks forcibly removed in casa 5.8 / 6.2
    if (version[0] == 5 and version[1] >= 8) or (version[0] == 6 and version[1] >= 2):
        del impars['chanchunks']

    return impars

def copy_ms(src, dest):
    if os.path.exists(dest):
        if not os.getenv('CONTINUE_IF_MS_EXISTS'):
            raise IOError("The target directory {dest} already exists".format(dest=dest))
        else:
            logprint("{0} exists, using it as concatvis".format(dest), origin='almaimf_line_imaging')
            return dest
    else:
        logprint("Copying concatvis {0}->{1}".format(src, dest), origin='almaimf_line_imaging')
        shutil.copytree(src, dest)
        # could use filecmp.dircmp to do a deeper comparison, but that might be expensive and unnecessary
        assert os.path.exists(dest)
        return dest



if exclude_7m:
    arrayname = '12M'
elif only_7m:
    arrayname = '7M'
else:
    arrayname = '7M12M'


# global default: only do robust 0 for lines
robust = 0

logprint("Initializing line imaging with global parameters"
         " exclude_7m={0}, only_7m={1}, band_list={2}, field_id={3}"
         .format(exclude_7m, only_7m, band_list, field_id),
         origin='almaimf_line_imaging')

for band in band_list:
    for field in to_image[band]:
        spwnames = tuple('spw{0}'.format(x) for x in to_image[band][field])
        logprint("Found spectral windows {0} in band {1}: field {2}"
                 .format(to_image[band][field].keys(), band, field),
                 origin='almaimf_line_imaging')
        if max(int(x) for x in to_image[band][field]) > 7:
            raise ValueError("Found invalid spw numbers; ALMA-IMF data do not include >8 spws")
        for spw in to_image[band][field]:

            # python 2.7 specific hack: force 'field' to be a bytestring
            # instead of a unicode string (CASA's lower-level functions
            # can't accept unicode strings)
            field = str(field)
            spw = str(spw)
            band = str(band)

            flagkey = "{0}_{1}_{2}_spw{3}".format(field, band, arrayname, spw)
            if flagkey in flag_thresholds:
                flagging_tolerance = flag_thresholds[flagkey]['tolerance']
                nflag_threshold = flag_thresholds[flagkey]['nchan']
            else:
                # defaults
                flagging_tolerance = 0.01
                nflag_threshold = 10
            logprint("Set flag threshold to {0} per channel for {1} channels (flagkey={2})"
                     .format(flagging_tolerance, nflag_threshold, flagkey))

            vis = list(map(str, to_image[band][field][spw]))

            # concatenate MSes prior to imaging
            basename = "{0}_{1}_spw{2}_{3}".format(field, band, spw, arrayname)
            logprint("Basename is: " + str(basename),
                     origin='almaimf_line_imaging')

            basepath = os.path.dirname(vis[0])
            assert os.path.split(basepath)[-1] == 'calibrated', "The data must be in a calibrated/ directory"
            concatvis = os.path.join(basepath, basename+".concat.ms")
            logprint("Concatvis is: " + str(concatvis), origin='almaimf_line_imaging')
            assert 'calibrated' in concatvis, "The concatenated visibility must be in a calibrated/ directory"

            if do_contsub and os.path.exists(concatvis+".contsub"):
                vis = [concatvis+".contsub"]
            elif os.path.exists(concatvis) and not do_not_concat:
                # we will use concatvis for the metadata
                vis = [concatvis]
            else:
                # We will skip data if there is no concatvis and the
                # visibilities are not available but if either the concatenated
                # or the unconcatenated visibilities are available, we continue
                skip = False
                for vv in vis:
                    if not os.path.exists(vv):
                        logprint("Skipped spectral window {0} for line {1}"
                                 "because filename {2} "
                                 "does not exist"
                                 .format(spw, line_name, vv),
                                 origin='almaimf_line_imaging')
                        skip = True
                if skip:
                    logprint("#### WARNING #### Skipping spw {0} because one "
                             "or more visibilities of {1} does not exist."
                             .format(spw, vis),
                             origin='almaimf_line_imaging')
                    continue

                if exclude_7m:
                    # don't use variable name 'ms' in python2.7!
                    vis = [ms_ for ms_ in vis if not is_7m(ms_)]
                elif only_7m:
                    vis = [ms_ for ms_ in vis if is_7m(ms_)]

            linpars = {}
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


            if do_not_concat:
                concatvis = vis
                logprint("DO_NOT_CONCAT set; NOT concatenating vis={0}.".format(vis),
                         origin='almaimf_line_imaging')
            elif any('concat' in x for x in vis):
                logprint("NOT concatenating vis={0}.".format(vis),
                         origin='almaimf_line_imaging')
            elif not os.path.exists(concatvis):
                if do_contsub and os.path.exists(concatvis+".contsub"):
                    logprint("Concatvis-contsub already exists, though non-contsub may not",
                             origin='almaimf_line_imaging'
                            )
                else:
                    logprint("Concatenating visibilities {vis} into {concatvis}"
                             .format(vis=vis, concatvis=concatvis),
                             origin='almaimf_line_imaging'
                            )
                    if dryrun:
                        raise ValueError("Cannot do a dry run without concatenated data in place")
                    for vv in vis:
                        # allow up to 1% flagging
                        check_channel_flags(vv, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                    concat(vis=vis, concatvis=concatvis)

            if do_contsub:

                if not os.path.exists(concatvis+".contsub"):
                    if dryrun:
                        raise ValueError("Cannot do a dry run without contsub concatenated data in place")
                    logprint("Concatvis contsub {0}.contsub does not exist, doing continuum subtraction.".format(str(concatvis)),
                             origin='almaimf_line_imaging')

                    contfile12m, contfile7m = merge_contdotdat(field, band,
                                                               basepath='.',
                                                               datfiles=metadata[band][field]['cont.dat'].values())
                    contfile = contfile12m

                    cont_freq_selection = parse_contdotdat(contfile)
                    logprint("Selected {0} as continuum channels".format(cont_freq_selection), origin='almaimf_line_imaging')

                    msmd.open(concatvis)
                    spws = msmd.spwsforfield(field)
                    msmd.close()

                    # obtain the frequency arrays for each spectral window
                    ms.open(concatvis)
                    try:
                        frqs = {spw: ms.cvelfreqs(spwid=[spw], outframe='LSRK') for spw in spws}
                    except TypeError:
                        frqs = {spw: ms.cvelfreqs(spwids=[spw], outframe='LSRK') for spw in spws}
                    ms.close()

                    # calculate the line channels from the contdatfile (which is in LSRK)
                    # and the frequency arrays
                    linechannels = contchannels_to_linechannels(cont_freq_selection, frqs)

                    uvcontsub(vis=concatvis,
                              fitspw=linechannels,
                              excludechans=True, # fit the non-line channels
                              combine='none', # DO NOT combine spws for continuum ID (since that implies combining 7m <-> 12m)
                              solint='int', # fit each integration (may be noisy?)
                              fitorder=1,
                              want_cont=False)

                # if do_contsub, we want to use the contsub'd MS
                concatvis = concatvis + contsub_suffix

            # check that autocorrs are flagged out
            if 'concat' in concatvis:
                flagsum = flagdata(vis=concatvis, mode='summary', uvrange='0~1m')
                if flagsum is not None and 'flagged' in flagsum and flagsum['flagged'] != flagsum['total']:
                    # if 'flagged' isn't in flagsum, it's an empty dict
                    raise ValueError("Found unflagged autocorrelation data (or at least, short baselines) in {0}".format(concatvis))

                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)

            elif isinstance(concatvis, list):
                for vv in concatvis:
                    flagsum = flagdata(vis=vv, mode='summary', uvrange='0~1m')
                    if flagsum is not None and 'flagged' in flagsum and flagsum['flagged'] != flagsum['total']:
                        raise ValueError("Found unflagged autocorrelation data (or at least, short baselines) in {vv}".format(vv=vv))


            if 'spw' in line_name:
                if not int(line_name.lstrip('spw')) == int(spw):
                    raise ValueError("Line name is {0}, which does not match spw number {1}".format(line_name, spw))

            baselineimagename = ("{0}_{1}_spw{2}_{3}_{4}{5}"
                                 .format(field, band, spw, arrayname,
                                         line_name, contsub_suffix))
            lineimagename = os.path.join(imaging_root, baselineimagename)

            if copy_files and not dryrun:
                # _copy_ the MS file to the working directory


                # first, make sure that we're not copying the MS into itself - that would be bad.

                if do_not_concat:
                    assert os.path.split(concatvis[0])[0] != workdir
                    newconcatvis = [os.path.join(workdir, os.path.basename(vv))
                                    for vv in concatvis]
                    concatvis = [copy_ms(vv, newvv)
                                 for vv,newvv in zip(concatvis, newconcatvis)]
                else:
                    assert os.path.split(concatvis)[0] != workdir
                    newconcatvis = os.path.join(workdir, os.path.basename(concatvis))
                    concatvis = copy_ms(concatvis, newconcatvis)


                # we need to copy the files to our working directory if they exist
                # (this allows for continuation of partly-completed processes
                # and reuse of existing startmodels)
                for suffix in ('.image', '.image.pbcor', '.mask', '.model',
                               '.pb', '.psf', '.residual', '.sumwt', '.weight',
                               '.contcube.model', '.image.fits',
                               '.image.pbcor.fits',
                               '_continuum_model.image.tt0',
                               '_continuum_model.image.tt1'):
                    dest = imaging_root
                    src = os.path.join(proddir,
                                       baselineimagename + suffix)
                    if os.path.exists(src):
                        logprint("Moving {0}->{1}".format(src, dest), origin='almaimf_line_imaging')
                        shutil.move(src, dest)

                # we don't copy or move over the continuum startmodels; they're light reads
                contmodel_path = proddir
                imaging_results_path_for_contmodel = workdir

            else:
                contmodel_path = imaging_root
                imaging_results_path_for_contmodel = imaging_root


            logprint("Measurement sets are: " + str(concatvis),
                     origin='almaimf_line_imaging')
            check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
            coosys, racen, deccen = determine_phasecenter(ms=concatvis,
                                                          field=field)
            phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
            check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
            (dra, ddec, pixscale) = list(determine_imsize(ms=concatvis,
                                                          field=field,
                                                          phasecenter=(racen, deccen),
                                                          spw='all',
                                                          # July 2, 2021 - shrink pixsize to 1/4 (actually was apparently 1/5)
                                                          pixfraction_of_fwhm=1/5. if only_7m else 1/4.,
                                                          exclude_7m=exclude_7m,
                                                          only_7m=only_7m,
                                                          min_pixscale=0.08, # arcsec; dropped 20% on Nov 6, 2020 to handle beam size issues
                                                         ))
            imsize = [int(dra), int(ddec)]
            cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2
            check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)

            dirty_tclean_made_residual = False


            # prepare for the imaging parameters
            pars_key = "{0}_{1}_{2}_robust{3}{4}".format(field, band,
                                                         arrayname, robust,
                                                         contsub_suffix.replace(".", "_"))
            if (pars_key+"_"+line_name) in line_imaging_parameters:
                logprint("Using parameter key {0} instead of {1}".format(pars_key+"_"+line_name, pars_key))
                logprint("This means we're using parameters {0} instead of {1}".format(line_imaging_parameters[pars_key+"_"+line_name],
                                                                                       line_imaging_parameters[pars_key]))
                pars_key = pars_key+"_"+line_name
            impars = line_imaging_parameters[pars_key]

            impars = set_impars(impars=impars, line_name=line_name, vis=vis,
                                linpars=linpars, spwnames=spwnames)

            if 'imsize' not in impars:
                impars['imsize'] = imsize
            else:
                logprint("Overriding imsize={0} to {1}".format(imsize, impars['imsize']))
            if 'cell' not in impars:
                impars['cell'] = cellsize
                logprint("Overriding cell={0} to {1}".format(cellsize, impars['cell']))
            if 'phasecenter' not in impars:
                impars['phasecenter'] = phasecenter
                logprint("Overriding phasecenter={0} to {1}".format(phasecenter, impars['phasecenter']))
            #impars['field'] = [field.encode()]
            impars['field'] = field

            mask_out_endchannels = False
            if 'mask_out_endchannels' in impars:
                # remove this parameter
                mask_out_endchannels = impars.pop('mask_out_endchannels')

            # default Oct 13, 2020: always make dirty image
            # so we can have a mask to work with
            make_dirty_image = True
            if 'threshold' in impars:
                if 'sigma' in impars['threshold']:
                    make_dirty_image = True
            if 'startmodel' in impars:
                # need the dirty image to populate our model
                make_dirty_image = True

            # start with cube imaging
            # step 1 is dirty imaging

            if make_dirty_image and not os.path.exists(lineimagename+".image") and not os.path.exists(lineimagename+".residual"):
                if os.path.exists(lineimagename+".psf"):
                    logprint("WARNING: The PSF for {0} exists, but no image exists."
                             "  This likely implies that an ongoing or incomplete "
                             "imaging run for this file exists.  It will not be "
                             "imaged this time; please check what is happening.  "
                             "(this warning issued /before/ dirty imaging)"
                             .format(lineimagename),
                             origin='almaimf_line_imaging',
                             priority='WARNING'
                             )
                    continue
                # first iteration makes a dirty image to estimate the RMS
                impars_dirty = impars.copy()
                impars_dirty['niter'] = 0
                if 'startmodel' in impars_dirty:
                    del impars_dirty['startmodel']

                impars_dirty['parallel'] = parallel
                # use the same mask as specified for the main run
                # impars_dirty['usemask'] = None

                logprint("Dirty imaging parameters are {0}".format(impars_dirty),
                         origin='almaimf_line_imaging')
                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                if not dryrun:
                    tclean(vis=concatvis,
                           imagename=lineimagename,
                           restoringbeam='', # do not use restoringbeam='common'
                           # it results in bad edge channels dominating the beam
                           **impars_dirty
                          )
                    sethistory(lineimagename, impars=impars_dirty, suffixes=(".image", ".residual"))
                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                for suffix in ("mask", "model"):
                    bad_fn = lineimagename + "." + suffix
                    if os.path.exists(bad_fn):
                        logprint("Removing {0} from dirty clean".format(bad_fn),
                                 origin='almaimf_line_imaging')
                        shutil.rmtree(bad_fn)

                if os.path.exists(lineimagename+".image"):
                    # tclean with niter=0 is not supposed to produce a .image file,
                    # but if it does (and it appears to have done so on at
                    # least one run), we still want to clean the cube
                    dirty_tclean_made_residual = True

                did_dirty_imaging = True
            elif make_dirty_image and not os.path.exists(lineimagename+".residual"):
                raise ValueError("The residual image is required for further imaging.")
            else:
                did_dirty_imaging = False
                if make_dirty_image:
                    logprint("Found existing files matching {0}".format(lineimagename),
                             origin='almaimf_line_imaging'
                            )
                else:
                    logprint("Skipped dirty imaging becauase a fixed threshold is used.",
                             origin='almaimf_line_imaging'
                            )

            if os.path.exists(lineimagename+".psf") and not os.path.exists(lineimagename+".image"):
                logprint("WARNING: The PSF for {0} exists, but no image exists."
                         "  This likely implies that an ongoing or incomplete "
                         "imaging run for this file exists.  It will not be "
                         "imaged this time; please check what is happening."
                         "(warning issued /after/ dirty imaging)"
                         .format(lineimagename),
                         origin='almaimf_line_imaging',
                         priority='WARNING'
                         )
                # just skip the rest here
                continue

            # if the dirty image was made or exists
            if make_dirty_image and not dryrun:
                # the threshold needs to be computed if any imaging is to be done (either contsub or not)
                # no .image file is produced, only a residual
                logprint("Computing residual image statistics for {0}".format(lineimagename),
                         origin='almaimf_line_imaging')
                ia.open(lineimagename+".residual")
                try:
                    stats = ia.statistics(robust=True)
                    rms = float(stats['medabsdevmed'] * 1.482602218505602)
                except RuntimeError as ex:
                    if "Binning accounting error" in str(ex):
                        logprint("Could not use robust statistics; reverting to non-robust",
                                 origin="almaimf_line_imaging")
                        stats = ia.statistics()
                        rms = stats['rms']
                    else:
                        raise ex
                ia.close()

                if rms >= 1:
                    logprint(str(stats), origin='almaimf_line_imaging_exception')
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


            if 'startmodel' in impars:
                if do_contsub:
                    # cannot use a startmodel for do_contsub
                    logprint("Startmodel is being ignored because MS is continuum subtracted",
                             origin='almaimf_line_imaging')
                    del impars['startmodel']
                else:
                    make_continuum_startmodel = True
                    # remove the model image
                    # (it should be created by dirty imaging above)
                    if os.path.exists(lineimagename+".model") and impars['startmodel'] == os.path.exists(lineimagename+".model"):
                        logprint("Startmodel {0} was specifield and exists; we are proceeding assuming "
                                 "that this is a full-cube startmodel.".format(impars['startmodel']))
                        make_continuum_startmodel = False
                    if did_dirty_imaging and os.path.exists(lineimagename+".model"):
                        logprint("Removing {0}.model because we're using startmodel instead"
                                 .format(lineimagename),
                                 origin='almaimf_line_imaging')
                        shutil.rmtree(lineimagename+".model")
                    elif (not did_dirty_imaging) and (os.path.exists(lineimagename+".model")):
                        logprint("Found an existing .model file, but startmodel "
                                 "was set.  The pipeline will continue "
                                 "assuming this is a continuation clean, and will "
                                 "pick up with the existing model rather than "
                                 "the specified startmodel.",
                                 origin='almaimf_line_imaging')
                        del impars['startmodel']
                        make_continuum_startmodel = False
                    else:
                        # lineimagename+".model" does not exist
                        pass # all is happy

                    # MPI HACK
                    # MPI appears to make .model files that can't be tracked in the usual fashion
                    if os.path.exists(lineimagename+".workdirectory"):
                        logprint("Removing ALL MPI-generated models in {0}.workdirectory".format(lineimagename),
                                 origin='almaimf_line_imaging')
                        for fn in glob.glob(lineimagename+".workdirectory/*.model"):
                            shutil.rmtree(fn)

                    if make_continuum_startmodel and not dryrun:
                        contmodel = create_clean_model(cubeimagename=baselineimagename,
                                                       contimagename=impars['startmodel'],
                                                       imaging_results_path=imaging_results_path_for_contmodel,
                                                       contmodel_path=contmodel_path)
                        impars['startmodel'] = contmodel



            if continue_imaging or dirty_tclean_made_residual or not os.path.exists(lineimagename+".image"):
                # continue imaging using a threshold
                logprint("Imaging parameters are {0}".format(impars),
                         origin='almaimf_line_imaging')
                logprint("continue_imaging is set to be {0}".format(continue_imaging),
                         origin='almaimf_line_imaging')
                logprint("dirty_tclean_made_residual is set to be {0}".format(dirty_tclean_made_residual),
                         origin='almaimf_line_imaging')

                # Oct 13, 2020: we'll modify the mask, not remove it
                # if os.path.exists(lineimagename+".mask") and 'usemask' in impars and impars['usemask'] not in ('', None):
                #     logprint("using pre-existing mask {0}".format(lineimagename+".mask"),
                #              origin='almaimf_line_imaging')
                #     shutil.rmtree(lineimagename+".mask")
                # elif os.path.exists(lineimagename+".mask"):
                #     if 'usemask' in impars and impars['usemask'] != 'user':
                #         raise ValueError("Mask exists but not specified as user.")
                if os.path.exists(lineimagename+".mask"):
                    impars['usemask'] = 'user'

                    if 'mask' in impars and impars['mask'] != '':
                        # this is to handle the case that a user has specified a mask:
                        # tclean will fail if the imagname.mask exists (and we
                        # know it does; see check above) but a mask is
                        # specified
                        # (This is only needed if dirty imaging is _not_ run)
                        logprint("Found an existing mask, but a user mask {0} was specified,"
                                 " so we are overwriting the existing mask.".format(impars['mask']),
                                 origin='almaimf_line_imaging')
                        shutil.rmtree(lineimagename+".mask")
                        shutil.copytree(impars['mask'], lineimagename+".mask")

                    impars['mask'] = '' # the mask exists, so CASA can't be told to use it

                    if mask_out_endchannels:
                        # we mask out the end channels because sometimes these
                        # channels have less coverage, and attempting to clean
                        # these outer channels frequently causes tclean to
                        # diverge
                        logprint("Masking out end channels {0}".format(mask_out_endchannels),
                                 origin="almaimf_line_imaging")
                        ia.open(infile=lineimagename+".mask")
                        lowedge = ia.getchunk(blc=[0,0,0,0],
                                              trc=[-1,-1,-1,mask_out_endchannels])
                        lowedge[:] = 0
                        ia.putchunk(pixels=lowedge, blc=[0,0,0,0],)

                        shape = ia.shape()

                        highedge = ia.getchunk(blc=[0,0,0,shape[3]-1-mask_out_endchannels],
                                               trc=[-1,-1,-1,-1])
                        highedge[:] = 0
                        ia.putchunk(highedge,
                                    blc=[0,0,0,shape[3]-1-mask_out_endchannels],
                                    )

                        ia.close()

                # SANITY CHECK:
                if os.path.exists(lineimagename+".model"):
                    logprint("Model {0}.model exists".format(lineimagename),
                             origin='almaimf_line_imaging')
                    if 'startmodel' in impars and impars['startmodel']:
                        raise ValueError("Startmodel is set to {0} but model {1} exists"
                                         .format(impars['startmodel'], lineimagename+".model"))

                # set by global environmental variable to auto-recognize
                # when being run from an MPI session.
                impars['parallel'] = parallel


                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                if not dryrun:
                    tclean(vis=concatvis,
                           imagename=lineimagename,
                           restoringbeam='', # do not use restoringbeam='common'
                           # it results in bad edge channels dominating the beam
                           calcres=False,
                           **impars
                          )
                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                # re-do the tclean once more, with niter=0, to force recalculation of the residual
                niter = impars['niter']
                impars['niter'] = 0
                if 'startmodel' in impars:
                    # we definitely have a model now, so we don't want a startmodel
                    smod = impars['startmodel']
                    impars['startmodel'] = ''
                else:
                    smod = ''
                if 'mask' in impars:
                    mask = impars['mask']
                    impars['mask'] = ''
                else:
                    mask = ''
                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)
                if not dryrun:
                    tclean(vis=concatvis,
                           imagename=lineimagename,
                           restoringbeam='',
                           calcres=True,
                           **impars
                          )
                    impars['niter'] = niter
                    impars['startmodel'] = smod
                    impars['mask'] = mask
                    sethistory(lineimagename, nsigma=nsigma, impars=impars)
                check_channel_flags(concatvis, tolerance=flagging_tolerance, nchan_tolerance=nflag_threshold)

                if not dryrun:
                    impbcor(imagename=lineimagename+'.image',
                            pbimage=lineimagename+'.pb',
                            outfile=lineimagename+'.image.pbcor',
                            cutoff=0.2,
                            overwrite=True)

                    if do_export_fits:
                        exportfits(lineimagename+".image", lineimagename+".image.fits", overwrite=True)
                        exportfits(lineimagename+".image.pbcor", lineimagename+".image.pbcor.fits", overwrite=True)


            if copy_files and not dryrun:
                for suffix in ('.image', '.image.pbcor', '.mask', '.model',
                               '.pb', '.psf', '.residual', '.sumwt', '.weight',
                               '.contcube.model', '.image.fits',
                               '.image.pbcor.fits',
                               '_continuum_model.image.tt0',
                               '_continuum_model.image.tt1'):
                    src = lineimagename+suffix
                    dest = proddir
                    if os.path.exists(src):
                        logprint("Moving {0}->{1}".format(src, dest), origin='almaimf_line_imaging')
                        shutil.move(src, dest)

                # use the variable name 'newconcatvis' here since that should
                # only ever take on the value specified in copy_files; this is
                # a safety mechanism to make sure we don't accidentally delete
                # the original file.
                if do_not_concat:
                    # sanity check: make sure `newconcatvis` was set to be a list
                    assert isinstance(newconcatvis, list)
                    for newvv in newconcatvis:
                        logprint("Removing MS file {0} from working directory {1}"
                                 .format(newvv, workdir),
                                 origin='almaimf_line_imaging')
                        shutil.rmtree(newvv)
                else:
                    logprint("Removing MS file {0} from working directory {1}"
                             .format(newconcatvis, workdir),
                             origin='almaimf_line_imaging')
                    shutil.rmtree(newconcatvis)


            logprint("Completed {0}->{1}".format(vis, concatvis), origin='almaimf_line_imaging')


logprint("Completed line_imaging.py run", origin='almaimf_line_imaging')
