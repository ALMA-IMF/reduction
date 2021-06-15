"""
Continuum imaging self-calibration script.  

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only split
        fields with this name (e.g., "W43-MM1", "W51-E", etc.).
        Metadata will still be collected for *all* available MSes.
    SELFCAL_FIELD_ID=<number>
        Specify a single number or a comma-separated list of numbers for fields
        you want to self-calibrate on.  This will override the selfcal
        heuristics and will instead use just the selected field to
        self-calibrate on.  However, the full mosaic will still be imaged.
        (can also be specified by setting `selfcal_field_id = [1]` or similar;
        the variable must be a list of integers though)
    BAND_TO_IMAGE=B3 or B6
        If this parameter is set, only image the selected band.
    DO_BSENS=<boolean>
        Do bsens?  If not, do cleanest.  Default is cleanest
    EXCLUDE_BRIGHT_SPW=<boolean>
        Should the spws containing 230.5 GHz (CO 2-1) be excluded?
        (for B3, specifying this parameter will exclude the 93.173 GHz Diazenylium (N2H+) line)
        This is most important if DO_BSENS=True.
        This will add a _noco (or _no2hp) suffix

The environmental variable ``ALMAIMF_ROOTDIR`` should be set to the directory
containing this file.

What does it do
===============
The imaging self-calibration step does the following:

    (1) Select data based on the FIELD_ID, EXCLUDE_7M, and BAND_TO_IMAGE
    parameters
    (2) split those data into a new file called <basename>_<arrayname>_selfcal.ms,
    where <basename> is the name of the merged calibrated continuum measurement set.
    (3) do initial dirty imaging in a file named <preamble>_dirty_preselfcal
    (4) create a mask using ds9 regions based off of the dirty image (or,
    optionally, off an existing cleaned image).  This step will be skipped if you
    use a CRTF region
    (5) re-image the data in a file named <preamble>_preselfcal using the mask
    from (4) (or whatever mask you've specified).  If this image already exists,
    the model column of the ms will be populated based on the existing image.
    (6) optionally make a new mask based on the cleaned image in (5)
    (7) Begin the self-calibration iterations:
        (a) Calculate gain solutions based on the imaging_parameters.py selfcal
        parameters dictionary


Restarting
==========
If you want to restart the selfcal iterations from scratch or from a particular
self-calibration iteration (e.g., you want to change your mask and start over
from iteration #3), remove all associated imaging files.  The script will reimage
any filename for which it does not find <prefix>.image.tt0, so you must remove
that file, but you should also remove the others.  For example, if you want
to re-do iterations 3 and higher for W51-E_B3, run a command like this in the
imaging_results directory:

    rm -r W51-E_B3_*_robust0_selfcal[3456]*
    rm -r W51-E_B3_*_mask.mask
    # then, cd .. (to the parent directory of imaging_results) and:
    # (you need to match the selfcal iteration number with the chosen
    # self-cal averaging time)
    rm -r W51-E_B3_*[3456]_inf.cal
    rm -r W51-E_B3_*[3456]_int.cal

or if you want to totally start over:

    # first, ls to make sure you know what you're deleting
    ls -1d rm -r W51-E_B3_*_robust*_selfcal*
    # then, delete it
    rm -r W51-E_B3_*_robust*_selfcal*
    # and remove the .cal files in the parent directory
    rm -r W51-E_B3_*cal

MASKING
=======
There are two ways to specify masks:
    (1) the ds9 region based mask where you draw regions and name
    them with a flux level, as described in https://github.com/ALMA-IMF/notebooks/blob/master/SelfCal_Instructions_Examination.ipynb
    (2) specify 'maskname' in the imaging parameters, e.g.:
   'maskname': {0: 'clean_mask1.crtf', 1: 'clean_mask2.crtf', 2: 'clean_mask3.crtf', 3: 'clean_mask4.crtf'},
"""

import os
import copy
import sys
import shutil
import glob

from_cmd = False
# If run from command line
if len(sys.argv) > 2:
    aux = os.path.dirname(sys.argv[2])
    if os.path.isdir(aux):
        almaimf_rootdir = aux
        from_cmd = True

if 'almaimf_rootdir' in locals():
    os.environ['ALMAIMF_ROOTDIR'] = almaimf_rootdir
if os.getenv('ALMAIMF_ROOTDIR') is None:
    try:
        import metadata_tools
        os.environ['ALMAIMF_ROOTDIR'] = os.path.split(metadata_tools.__file__)[0]
    except ImportError:
        raise ValueError("metadata_tools not found on path; make sure to "
                         "specify ALMAIMF_ROOTDIR environment variable "
                         "or your PYTHONPATH variable to include the directory"
                         " containing the ALMAIMF code.")
else:
    sys.path.append(os.getenv('ALMAIMF_ROOTDIR'))
almaimf_rootdir = os.getenv('ALMAIMF_ROOTDIR')

import numpy as np

from getversion import git_date, git_version
from metadata_tools import (determine_imsize, determine_phasecenter, logprint,
                            check_model_is_populated, test_tclean_success,
                            populate_model_column, get_non_bright_spws,
                            sethistory)
from make_custom_mask import make_custom_mask
from imaging_parameters import imaging_parameters, selfcal_pars
from selfcal_heuristics import goodenough_field_solutions

try:
    from tasks import tclean, plotms, split, flagdata

    from clearcal_cli import clearcal_cli as clearcal
    from gaincal_cli import gaincal_cli as gaincal
    from rmtables_cli import rmtables_cli as rmtables
    from applycal_cli import applycal_cli as applycal
    from exportfits_cli import exportfits_cli as exportfits
    from ft_cli import ft_cli as ft

    from taskinit import msmdtool, iatool, tbtool, mstool

    msmd = msmdtool()
    ia = iatool()
    tb = tbtool()
    ms = mstool()
except ImportError:
    from casatasks import tclean, split, flagdata
    import casaplotms as plotms

    from casatasks import clearcal, gaincal, rmtables, applycal, exportfits

    from casatools import msmetadata, image, table, ms
    msmd = msmetadata()
    ia = image()
    tb = table()
    ms = ms()


imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

# Command line options
if from_cmd:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', nargs=1, help='Casa parameter')
    parser.add_argument('--exclude7M', action='store_true',
                        help='Include 7M data')
    parser.add_argument('--only7M', action='store_true',
                        help='Only image 7M data')
    args = parser.parse_args()
    exclude_7m = args.exclude7M
    only_7m = args.only7M

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

if 'selfcal_field_id' not in locals():
    if os.getenv('SELFCAL_FIELD_ID') is not None:
        selfcal_field_id = list(map(int, os.getenv('SELFCAL_FIELD_ID').split(",")))
        logprint("Using selfcal_field_id = {0}".format(selfcal_field_id),
                 origin='contim_selfcal')
    else:
        selfcal_field_id = None
elif selfcal_field_id is not None:
    if not isinstance(selfcal_field_id, list):
        selfcal_field_id = [selfcal_field_id]
    for entry in selfcal_field_id:
        assert isinstance(entry,int), "{0} is not an int".format(entry)
    logprint("Using selfcal_field_id = {0}".format(selfcal_field_id),
             origin='contim_selfcal')



logprint("Beginning selfcal script with exclude_7m={0} and only_7m={1}".format(exclude_7m, only_7m),
         origin='contim_selfcal')


# load the list of continuum MSes from a file
# (this file has one continuum MS full path, e.g. /path/to/file.ms, per line)
with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]

if len(continuum_mses) == 0:
    raise IOError("Your continuum_mses.txt file is empty.  There is nothing "
                  "to image or self-calibrate.")

dryrun = bool(os.getenv('DRYRUN') or (dryrun if 'dryrun' in locals() else False))

if 'do_bsens' in locals():
    os.environ['DO_BSENS'] = str(do_bsens)
if os.getenv('DO_BSENS') is not None and os.getenv('DO_BSENS').lower() != 'false':
    do_bsens = True
    logprint("Using BSENS measurement set", origin='contim_selfcal')
    continuum_mses = [x.replace('_continuum_merged.cal.ms',
                                '_continuum_merged_bsens.cal.ms')
                      for x in continuum_mses]
else:
    do_bsens = False

if 'exclude_bright_spw' in locals():
    os.environ['EXCLUDE_BRIGHT_SPW'] = str(do_bsens)
elif os.getenv('EXCLUDE_BRIGHT_SPW') is not None and os.getenv('EXCLUDE_BRIGHT_SPW').lower() != 'false':
    exclude_bright_spw = True
else:
    exclude_bright_spw = False

logprint("parameters are: do_bsens={do_bsens} only_7m={only_7m} exclude_bright_spw={exclude_bright_spw}"
         "exclude_7m={exclude_7m} selfcal_field_id={selfcal_field_id}".format(**locals()),
         origin='contim_selfcal')


for continuum_ms in continuum_mses:

    # strip off .cal.ms
    basename = os.path.split(continuum_ms[:-7])[1]

    band = 'B3' if 'B3' in basename else 'B6' if 'B6' in basename else 'ERROR'

    # allow optional cmdline args to skip one or the other band
    if os.getenv('BAND_TO_IMAGE'):
        if 'B' not in os.getenv('BAND_TO_IMAGE'):
            os.environ['BAND_TO_IMAGE'] = 'B'+os.getenv('BAND_TO_IMAGE')
        logprint("Imaging only band {0}".format(os.getenv('BAND_TO_IMAGE')),
                 origin='contim_selfcal')
        if band not in os.getenv('BAND_TO_IMAGE'):
            continue

    field = basename.split("_")[0]

    if os.getenv('FIELD_ID'):
        if field not in os.getenv('FIELD_ID'):
            logprint("Skipping {0} because it is not in FIELD_ID={1}"
                     .format(field, os.getenv('FIELD_ID')))
            continue
        elif '_' in os.getenv('FIELD_ID'):
            field = os.getenv('FIELD_ID')

    if exclude_7m:
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' not in x])
        msmd.close()
        arrayname = '12M'
    elif only_7m:
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' in x])
        msmd.close()
        arrayname = '7M'
    else:
        antennae = ""
        arrayname = '7M12M'


    logprint("Beginning {2} band {0} array {1}".format(band, arrayname, field),
             origin='contim_selfcal')
    logprint("Continuum MS is: {0}".format(continuum_ms), origin='contim_selfcal')

    # create a downsampled split MS
    # A different MS will be used for the 12M-only and 7M+12M data
    # (much of the processing time is writing models to the MS, which takes a
    # long time even if 7M antennae are selected out)
    if do_bsens:
        selfcal_ms = basename+"_"+arrayname+"_selfcal_bsens.ms"
    else:
        selfcal_ms = basename+"_"+arrayname+"_selfcal.ms"

    logprint("Selfcal MS is: "
             "{0}".format(selfcal_ms), origin='contim_selfcal')
    assert os.path.exists(selfcal_ms)

    flagsum = flagdata(vis=selfcal_ms, mode='summary', uvrange='0~1m')
    if flagsum is not None and 'flagged' in flagsum and flagsum['flagged'] != flagsum['total']:
        raise ValueError("Found unflagged autocorrelation data (or at least, short baselines) in {0}".format(selfcal_ms))

    coosys,racen,deccen = determine_phasecenter(ms=selfcal_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=selfcal_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                exclude_7m=exclude_7m,
                                                only_7m=only_7m,
                                                spw='all',
                                                pixfraction_of_fwhm=1/8. if only_7m else 1/4.))
    imsize = [dra, ddec]
    cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

    for key, value in imaging_parameters.items():
        if 'cell' not in imaging_parameters[key]:
            imaging_parameters[key]['cell'] = cellsize
        if 'imsize' not in imaging_parameters[key]:
            imaging_parameters[key]['imsize'] = imsize

    contimagename = os.path.join(imaging_root, basename) + "_" + arrayname
    if do_bsens:
        # just a sanity check
        assert 'bsens' in contimagename

    # only do robust = 0
    robust = 0

    pars_key = "{0}_{1}_{2}_robust{3}".format(field, band, arrayname, robust)
    if do_bsens and (pars_key+"_bsens") in imaging_parameters:
        impars = imaging_parameters[pars_key+"_bsens"]
    else:
        impars = imaging_parameters[pars_key]

    if exclude_bright_spw:
        if band == 'B6':
            non_bright_spws = get_non_bright_spws(selfcal_ms)
            brightlinesuffix = '_noco'
        elif band == 'B3':
            non_bright_spws = get_non_bright_spws(selfcal_ms, frequency=93.173e9)
            brightlinesuffix = '_non2hp'
        else:
            raise ValueError("Invalid band specified: {band}".format(band=band))
        contimagename = contimagename+brightlinesuffix
        impars['spw'] = ",".join(map(str, non_bright_spws))
    else:
        brightlinesuffix = ''

    if do_bsens and (pars_key+"_bsens") in selfcal_pars:
        selfcalpars = selfcal_pars[pars_key+"_bsens"]
    else:
        selfcalpars = selfcal_pars[pars_key]

    logprint("Selfcal parameters are: {0}".format(selfcalpars),
             origin='almaimf_cont_selfcal')


    # BEGIN SELFCAL HERE
    cals = []

    for selfcaliter in selfcalpars.keys():

        logprint("Gaincal iteration {0}".format(selfcaliter),
                 origin='contim_selfcal')

        imname = contimagename+"_robust{0}_selfcal{1}".format(robust,
                                                              selfcaliter)

        # iteration #1 of phase-only self-calibration
        caltype = 'amp' if 'a' in selfcalpars[selfcaliter]['calmode'] else 'phase'
        caltable = '{0}{5}_{1}_{2}{3}_{4}.cal'.format(basename, arrayname, caltype, selfcaliter,
                                                      selfcalpars[selfcaliter]['solint'], brightlinesuffix)

        cals.append(caltable)


        logprint("Completed gaincal iteration {0}".format(selfcaliter),
                 origin='contim_selfcal')



    # finaliter section begins here


    # make sure the calibration tables have been applied, otherwise re-runs can
    # result in starting from un-corrected data
    if not dryrun:
        clearcal(vis=selfcal_ms, addmodel=True)
        # use gainfield so we interpolate the good solutions to the other
        # fields
        assert len(cals) >= selfcaliter

        okfields_list = []
        for caltable in cals:
            with open(caltable+".fields", 'r') as fh:
                okfields_str = fh.read().strip()
            okfields_list.append(okfields_str)
        assert len(cals) == len(okfields_list)

        applycal(vis=selfcal_ms, gainfield=okfields_list, gaintable=cals,
                 interp="linear", applymode='calonly', calwt=False)


    for order,robusts in zip(('bottomup', 'topdown'),
                             [(-2, -1, -0.5, 0, 0.5, 1, 2),
                              (-2, -1, -0.5, 0, 0.5, 1, 2)[::-1]]):
        robust_startmod = 0
        first = True

        for robust in robusts:
            logprint("Imaging self-cal iter {0} (final) with robust {1}"
                     .format(selfcaliter, robust),
                     origin='contim_selfcal')

            pars_key = "{0}_{1}_{2}_robust{3}".format(field, band, arrayname, robust)
            if do_bsens and (pars_key+"_bsens") in imaging_parameters:
                impars_finaliter = copy.copy(imaging_parameters[pars_key+"_bsens"])
            else:
                impars_finaliter = copy.copy(imaging_parameters[pars_key])

            for key, val in impars_finaliter.items():
                if isinstance(val, dict):
                    logprint("dictionary being updated from: {0}".format(val))  # DEBUG
                    impars_finaliter[key] = val['final'] if 'final' in val else val[selfcaliter]


            finaliterimname = contimagename+"_robust{0}_selfcal{1}_finaliter_pb_{2}".format(robust,
                                                                                            selfcaliter,
                                                                                            order)

            if 'maskname' in impars_finaliter:
                del impars_finaliter['maskname']

            if os.path.exists(finaliterimname + ".mask"):
                impars_finaliter['usemask'] = 'pb'
                impars_finaliter['mask'] = ''
            else:
                # Force PB mask
                impars_finaliter['usemask'] = 'pb'
                impars_finaliter['mask'] = 'pb'

            # force more major cycles
            impars_finaliter['cyclefactor'] = 2.0

            if os.path.exists(finaliterimname+".model.tt0"):
                # if there is already a model with this name on disk, we're continuing from that
                # one instead of starting from scratch
                modelname=''
            else:
                # we're going to start from 0 in the last iteration, then build up -2, -1, -0.5 ...
                if first:
                    modelname = [contimagename+"_robust{1}_selfcal{0}_finaliter.model.tt0".format(selfcaliter, robust_startmod),
                                 contimagename+"_robust{1}_selfcal{0}_finaliter.model.tt1".format(selfcaliter, robust_startmod)]
                    first = False
                else:
                    modelname = [contimagename+"_robust{1}_selfcal{0}_finaliter_pb_{2}.model.tt0".format(selfcaliter, robust_startmod, order),
                                 contimagename+"_robust{1}_selfcal{0}_finaliter_pb_{2}.model.tt1".format(selfcaliter, robust_startmod, order)]
            if not dryrun:
                logprint("Final imaging parameters are: {0} for image name {1}".format(impars_finaliter, finaliterimname),
                         origin='almaimf_cont_selfcal')
                tclean(vis=selfcal_ms,
                       field=field.encode(),
                       imagename=finaliterimname,
                       phasecenter=phasecenter,
                       startmodel=modelname,
                       outframe='LSRK',
                       veltype='radio',
                       interactive=False,
                       antenna=antennae,
                       savemodel='none',
                       datacolumn='corrected',
                       pbcor=True,
                       **impars_finaliter
                      )
                test_tclean_success()
                sethistory(finaliterimname, impars=impars_finaliter, selfcalpars=selfcalpars, selfcaliter=selfcaliter)
                # overwrite=True because these could already exist
                exportfits(finaliterimname+".image.tt0", finaliterimname+".image.tt0.fits", overwrite=True)
                exportfits(finaliterimname+".image.tt0.pbcor", finaliterimname+".image.tt0.pbcor.fits", overwrite=True)

            robust_startmod = robust
