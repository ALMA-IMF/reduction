"""
Continuum imaging self-calibration script.  This script expects that you have
sucessfully run ``continuum_imaging.py`` first.

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

"""
"""
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
    import sys
    sys.path.append(os.getenv('ALMAIMF_ROOTDIR'))
almaimf_rootdir = os.getenv('ALMAIMF_ROOTDIR')

import numpy as np

from getversion import git_date, git_version
from metadata_tools import (determine_imsize, determine_phasecenter, logprint,
                            check_model_is_populated, test_tclean_success,
                            populate_model_column)
from make_custom_mask import make_custom_mask
from imaging_parameters import imaging_parameters, selfcal_pars
from selfcal_heuristics import goodenough_field_solutions

from tasks import tclean, plotms, split

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

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

# Command line options
if from_cmd:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', nargs=1, 
            help='Casa parameter')
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


logprint("Beginning selfcal script with exclude_7m={0} and only_7m={1}".format(exclude_7m, only_7m),
         origin='contim_selfcal')


# load the list of continuum MSes from a file
# (this file has one continuum MS full path, e.g. /path/to/file.ms, per line)
with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]

if len(continuum_mses) == 0:
    raise IOError("Your continuum_mses.txt file is empty.  There is nothing "
                  "to image or self-calibrate.")

if os.getenv('DO_BSENS') is not None and os.getenv('DO_BSENS').lower() != 'false':
    do_bsens = True
    logprint("Using BSENS measurement set",
             origin='contim_selfcal')
    continuum_mses += [x.replace('_continuum_merged.cal.ms',
                                 '_continuum_merged_bsens.cal.ms')
                       for x in continuum_mses]
else:
    do_bsens = False


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
    if not os.path.exists(selfcal_ms):

        logprint("Did not find selfcal ms.  Creating new one: "
                 "{0}".format(selfcal_ms), origin='contim_selfcal')

        msmd.open(continuum_ms)
        fdm_spws = msmd.spwsforfield(field)
        assert len(fdm_spws) > 0
        bws = msmd.bandwidths()[fdm_spws]
        spwstr = ",".join(map(str, fdm_spws))
        freqs = [msmd.reffreq(spw)['m0']['value'] for spw in fdm_spws]
        chwids = [np.mean(msmd.chanwidths(spw)) for spw in fdm_spws]

        # using Roberto's numbers
        # https://science.nrao.edu/facilities/vla/docs/manuals/oss2016A/performance/fov/bw-smearing
        Synth_HPBW = 0.3 # Smallest synth HPBW among target sample in arcsec
        #PB_HPBW = 21. * (300. / minfrq) # PB HPBW at lowest band freq (arcsec)
        #targetwidth = 0.25 * (Synth_HPBW / PB_HPBW) * minfrq # 98% BW smearing criterion

        width = [int(np.abs(0.25 * (Synth_HPBW / (21. * (300e9 / frq))) * frq / chwid))
                 for frq, chwid in zip(freqs, chwids)]
        # do not allow downsampling below 1/2 original width because that drops
        # edge channels sometimes
        width = [ww if float(ww)/msmd.nchan(spw) < 0.5 else int(msmd.nchan(spw)/2)
                 for ww, spw in zip(width, fdm_spws)]

        msmd.close()

        tb.open(continuum_ms)
        if 'CORRECTED_DATA' in tb.colnames():
            datacolumn='corrected'
        else:
            datacolumn='data'
        tb.close()

        split(vis=continuum_ms,
              outputvis=selfcal_ms,
              datacolumn=datacolumn,
              antenna=antennae,
              spw=spwstr,
              width=width,
              field=field,
             )

    logprint("Selfcal MS is: "
             "{0}".format(selfcal_ms), origin='contim_selfcal')

    coosys,racen,deccen = determine_phasecenter(ms=selfcal_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=selfcal_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                exclude_7m=exclude_7m,
                                                only_7m=only_7m,
                                                spw='all',
                                                pixfraction_of_fwhm=1/4.))
    imsize = [dra, ddec]
    cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

    contimagename = os.path.join(imaging_root, basename) + "_" + arrayname

    if not os.path.exists(contimagename+".uvwave_vs_amp.png"):
        # make a diagnostic plot to show the UV distribution
        plotms(vis=selfcal_ms,
               xaxis='uvwave',
               yaxis='amp',
               avgchannel='1000', # minimum possible # of channels
               plotfile=contimagename+".uvwave_vs_amp.png",
               coloraxis='observation',
               showlegend=True,
               showgui=False,
               antenna=antennae,
              )


    # only do robust = 0
    robust = 0

    pars_key = "{0}_{1}_{2}_robust{3}".format(field, band, arrayname, robust)
    impars = imaging_parameters[pars_key]
    dirty_impars = copy.copy(impars)
    dirty_impars['niter'] = 0
    # NOTE: if anything besides `maskname` and `niter` ends up with a
    # dictionary, we'll need to parse it here

    selfcalpars = selfcal_pars[pars_key]

    logprint("Selfcal parameters are: {0}".format(selfcalpars),
             origin='almaimf_cont_selfcal')

    if 'maskname' in dirty_impars:
        if isinstance(dirty_impars['maskname'], str):
            maskname = dirty_impars['maskname']
            logprint("Warning: only one mask found!  "
                     "Mask should be set to a dictionary of format "
                     "{iternumber: maskname}.  Self calibration iterations "
                     "will not work until this is changed.",
                     origin='almaimf_cont_selfcal')
        else:
            maskname = dirty_impars['maskname'][0]
        del dirty_impars['maskname']
        if '/' not in maskname and not os.path.exists(maskname):
            maskname = os.path.join(almaimf_rootdir,
                                    'clean_regions',
                                    maskname)
        if not os.path.exists(maskname):
            raise IOError("Mask {0} not found".format(maskname))


    imname = contimagename+"_robust{0}_dirty_preselfcal".format(robust)

    if not os.path.exists(imname+".image.tt0"):
        logprint("(dirty, pre-) Imaging parameters are: {0}".format(dirty_impars),
                 origin='almaimf_cont_selfcal')
        tclean(vis=selfcal_ms,
               field=field.encode(),
               imagename=imname,
               phasecenter=phasecenter,
               outframe='LSRK',
               veltype='radio',
               usemask='pb',
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               pbcor=True,
               antenna=antennae,
               datacolumn='data',
               **dirty_impars
              )
        test_tclean_success()

        ia.open(imname+".image.tt0")
        ia.sethistory(origin='almaimf_cont_selfcal',
                      history=["{0}: {1}".format(key, val) for key, val in
                               dirty_impars.items()])
        ia.sethistory(origin='almaimf_cont_imaging',
                      history=["git_version: {0}".format(git_version),
                               "git_date: {0}".format(git_date)])
        ia.close()

    if 'maskname' not in locals():
        # either use the reclean-based mask or the dirty mask
        try:
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        almaimf_rootdir,
                                        band,
                                        rootdir=imaging_root,
                                        suffix='_clean_robust{0}_{1}'.format(robust,
                                                                             arrayname)
                                       )
        except IOError:
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        almaimf_rootdir,
                                        band,
                                        rootdir=imaging_root,
                                        suffix='_dirty_robust{0}_{1}'.format(robust,
                                                                             arrayname)
                                       )
    imname = contimagename+"_robust{0}_preselfcal".format(robust)

    # copy the imaging parameters and make the "iter-zero" version
    impars_thisiter = copy.copy(impars)
    if 'maskname' in impars_thisiter:
        if isinstance(impars_thisiter['maskname'], str):
            maskname = impars_thisiter['maskname']
            logprint("Warning: only one mask found!  "
                     "Mask should be set to a dictionary of format "
                     "{iternumber: maskname}.  Self calibration iterations "
                     "will not work until this is changed.",
                     origin='almaimf_cont_selfcal')
        else:
            maskname = impars_thisiter['maskname'][0]
        del impars_thisiter['maskname']
        if '/' not in maskname and not os.path.exists(maskname):
            maskname = os.path.join(almaimf_rootdir,
                                    'clean_regions',
                                    maskname)
        if not os.path.exists(maskname):
            raise IOError("Mask {0} not found".format(maskname))

    for key, val in impars_thisiter.items():
        if isinstance(val, dict):
            impars_thisiter[key] = val[0]

    if not os.path.exists(imname+".image.tt0"):
        if maskname:
            assert os.path.exists(maskname), "Mask {0} was not found.".format(maskname)
        logprint("Imaging parameters are: {0}".format(impars_thisiter),
                 origin='almaimf_cont_selfcal')
        tclean(vis=selfcal_ms,
               field=field.encode(),
               imagename=imname,
               phasecenter=phasecenter,
               outframe='LSRK',
               veltype='radio',
               usemask='user',
               mask=maskname,
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               antenna=antennae,
               savemodel='modelcolumn',
               datacolumn='data',
               pbcor=True,
               **impars_thisiter
              )
        test_tclean_success()
        ia.open(imname+".image.tt0")
        ia.sethistory(origin='almaimf_cont_selfcal',
                      history=["{0}: {1}".format(key, val) for key, val in
                               impars.items()])
        ia.sethistory(origin='almaimf_cont_imaging',
                      history=["git_version: {0}".format(git_version),
                               "git_date: {0}".format(git_date)])
        ia.close()

        exportfits(imname+".image.tt0", imname+".image.tt0.fits")
        exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")

        # CHECK FOR MODEL FAILURES!
        ms.open(selfcal_ms)
        model_data = ms.getdata(['MODEL_PHASE'])
        ms.close()
        if 'model_phase' not in model_data or np.all(model_data['model_phase'] == 0):
            logprint("SEVERE error encountered: model column was not populated!"
                     "Therefore, populated model column from {0}".format(imname),
                     origin='almaimf_cont_selfcal')
            populate_model_column(imname, selfcal_ms, field, impars_thisiter,
                                  phasecenter, maskname, cellsize, imsize,
                                  antennae)
        else:
            logprint("Model column was populated from pre-selfcal image.",
                     origin='almaimf_cont_selfcal')

    else:
        # populate the model column (should be from data on disk matching
        # this format, but we don't need to - and can't - specify it)
        # If you want to use `ft`, you need to specify this:
        # modelname = [contimagename+"_robust{0}.model.tt0".format(robust),
        #              contimagename+"_robust{0}.model.tt1".format(robust)]

        populate_model_column(imname, selfcal_ms, field, impars_thisiter,
                              phasecenter, maskname, cellsize, imsize,
                              antennae)

        logprint("Skipped completed file {0} (dirty),"
                 " populated model column".format(imname),
                 origin='almaimf_cont_selfcal')

    # make a custom mask using the first-pass clean
    # (note: this will be replaced after each iteration if there is a file with
    # the appropriate name)
    try:
        maskname = make_custom_mask(field, imname+".image.tt0",
                                    almaimf_rootdir, band,
                                    rootdir=imaging_root,
                                    suffix='_clean_robust{0}_{1}'.format(robust,
                                                                         arrayname)
                                   )
    except Exception as ex:
        logprint("Did not make a mask from the clean data.  The exception was: "
                 "{0}.  If you specified {{'maskname': <something>}} for each "
                 "selfcal iteration in imaging_parameters.py, this is OK and "
                 "can be ignored.".format(str(ex)),
                 origin='almaimf_cont_selfcal')


    cals = []

    for selfcaliter in selfcalpars.keys():

        logprint("Gaincal iteration {0}".format(selfcaliter),
                 origin='contim_selfcal')

        # iteration #1 of phase-only self-calibration
        caltype = 'amp' if 'a' in selfcalpars[selfcaliter]['calmode'] else 'phase'
        caltable = '{0}_{1}_{2}{3}_{4}.cal'.format(basename, arrayname, caltype, selfcaliter,
                                                   selfcalpars[selfcaliter]['solint'])
        if not os.path.exists(caltable):
            #check_model_is_populated(selfcal_ms)
            gaincal(vis=selfcal_ms,
                    caltable=caltable,
                    gaintable=cals,
                    **selfcalpars[selfcaliter])
        else:
            logprint("Skipping existing caltable {0}".format(caltable),
                     origin='contim_selfcal')

        cals.append(caltable)

        # set up the imaging parameters for this round, allowing for a flexible definition
        # with either, e.g. {'niter': 1000} or {'niter': {1:1000, 2:100000, 3:999999}} etc
        impars_thisiter = copy.copy(impars)
        if 'maskname' in impars_thisiter:
            if selfcaliter in impars_thisiter['maskname']:
                maskname = impars_thisiter['maskname'][selfcaliter]
            else:
                logprint("Self cal iteration {0} has no associated mask. "
                         "Using mask {1} instead.".format(selfcaliter, maskname),
                         origin="contim_selfcal"
                        )
            del impars_thisiter['maskname']
        if '/' not in maskname and not os.path.exists(maskname):
            maskname = os.path.join(almaimf_rootdir,
                                    'clean_regions',
                                    maskname)
        if not os.path.exists(maskname):
            raise IOError("Mask {0} not found".format(maskname))

        # grab any iteration-specific values of the self-cal parameter
        for key, val in impars_thisiter.items():
            if isinstance(val, dict):
                impars_thisiter[key] = val[selfcaliter]


        # start from previous model to save time
        # (in principle, should converge anyway)
        if selfcaliter == 1:
            modelname = [contimagename+"_robust{0}_preselfcal.model.tt0".format(robust),
                         contimagename+"_robust{0}_preselfcal.model.tt1".format(robust)]
        else:
            modelname = [contimagename+"_robust{0}_selfcal{1}.model.tt0".format(robust, selfcaliter-1),
                         contimagename+"_robust{0}_selfcal{1}.model.tt1".format(robust, selfcaliter-1)]

        imname = contimagename+"_robust{0}_selfcal{1}".format(robust,
                                                              selfcaliter)

        if not os.path.exists(imname+".image.tt0"):

            if 'minsnr' in selfcalpars[selfcaliter]:
                minsnr = selfcalpars[selfcaliter]['minsnr']
            else:
                minsnr = 5

            okfields,notokfields = goodenough_field_solutions(caltable,
                                                              minsnr=minsnr)
            logprint("Fields {0} had min snr 5, fields {1} did not"
                     .format(okfields, notokfields), origin='contim_selfcal')
            if len(okfields) == 0:
                if selfcal_field_id is None:
                    logprint("All fields flagged out of gaincal solns!",
                             origin='contim_selfcal')
                    raise ValueError("All fields flagged out of gaincal solns!")
                else:
                    logprint("All fields flagged out of gaincal solns.  "
                             "Using manually-specified self-calibration field {0}".format(selfcal_field_id),
                             origin='contim_selfcal')
                    okfields = selfcal_field_id
            elif selfcal_field_id is not None:
                intersection = set(okfields).intersection(set(selfcal_field_id))
                logprint("Using fields {0} as manually specified for self-calibration, "
                         "though {1} were found to be good (the intersection is {2}"
                         .format(selfcal_field_id, okfields, intersection),
                         origin='contim_selfcal')
                okfields = selfcal_field_id
            okfields_str = ",".join(["{0}".format(x) for x in okfields])
            clearcal(vis=selfcal_ms, addmodel=True)
            # use gainfield so we interpolate the good solutions to the other
            # fields
            applycal(vis=selfcal_ms,
                     gainfield=okfields_str,
                     gaintable=cals,
                     interp="linear",
                     applymode='calonly',
                     calwt=False)

            # do not run the clean if no mask exists
            assert os.path.exists(maskname), "Mask {0} was not found.".format(maskname)

            # do this even if the output file exists: we need to populate the
            # modelcolumn
            logprint("Imaging parameters are: {0} for image name {1}".format(impars_thisiter, imname),
                     origin='almaimf_cont_selfcal')
            existing_files = glob.glob(imname+"*")
            logprint("Pre-existing files matching imname = {0}".format(existing_files),
                     origin='almaimf_cont_selfcal')
            tclean(vis=selfcal_ms,
                   field=field.encode(),
                   imagename=imname,
                   phasecenter=phasecenter,
                   startmodel=modelname,
                   outframe='LSRK',
                   veltype='radio',
                   usemask='user',
                   mask=maskname,
                   interactive=False,
                   cell=cellsize,
                   imsize=imsize,
                   antenna=antennae,
                   savemodel='modelcolumn',
                   datacolumn='corrected', # now use corrected data
                   pbcor=True,
                   **impars_thisiter
                  )
            test_tclean_success()
            ia.open(imname+".image.tt0")
            ia.sethistory(origin='almaimf_cont_selfcal',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars_thisiter.items()])
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["git_version: {0}".format(git_version),
                                   "git_date: {0}".format(git_date)])
            ia.close()
            # overwrite=True because these could already exist
            exportfits(imname+".image.tt0", imname+".image.tt0.fits", overwrite=True)
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits", overwrite=True)

            # CHECK FOR MODEL FAILURES!
            ms.open(selfcal_ms)
            model_data = ms.getdata(['MODEL_PHASE'])
            ms.close()
            if 'model_phase' not in model_data or np.all(model_data['model_phase'] == 0):
                logprint("SEVERE error encountered: model column was not populated!"
                         "Therefore, populated model column from {0}".format(imname),
                         origin='almaimf_cont_selfcal')
                populate_model_column(imname, selfcal_ms, field, impars_thisiter,
                                      phasecenter, maskname, cellsize, imsize,
                                      antennae)

        else:
            populate_model_column(imname, selfcal_ms, field, impars_thisiter,
                                  phasecenter, maskname, cellsize, imsize,
                                  antennae)


        regsuffix = '_selfcal{2}_robust{0}_{1}'.format(robust, arrayname,
                                                       selfcaliter)
        regfn = os.path.join(almaimf_rootdir,
                             'clean_regions/{0}_{1}{2}.reg'.format(field,
                                                                   band,
                                                                   regsuffix))
        if os.path.exists(regfn):
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        almaimf_rootdir,
                                        band,
                                        rootdir=imaging_root,
                                        suffix=regsuffix
                                       )
        else:
            logprint("Did not make a custom mask for iteration {0} because "
                     "region file name {1} was not found.  The mask name being "
                     "used is {2}.  If you specified {{'maskname': {2}}}, "
                     "this is expected.".format(selfcaliter, regfn, maskname),
                     origin='contim_selfcal')


        logprint("Completed gaincal iteration {0}".format(selfcaliter),
                 origin='contim_selfcal')


    for robust in (-2, 0, 2):
        logprint("Imaging self-cal iter {0} (final) with robust {1}"
                 .format(selfcaliter, robust),
                 origin='contim_selfcal')

        pars_key = "{0}_{1}_{2}_robust{3}".format(field, band, arrayname, robust)
        impars_finaliter = copy.copy(imaging_parameters[pars_key])
        if 'maskname' in impars_finaliter:
            if isinstance(impars_finaliter['maskname'], str):
                maskname = impars_finaliter['maskname']
                logprint("Warning: only one mask found!  "
                         "Mask should be set to a dictionary of format "
                         "{iternumber: maskname}.  Self calibration iterations "
                         "will not work until this is changed.",
                         origin='almaimf_cont_selfcal')
            else:
                maskname = impars_finaliter['maskname'][0]
            del impars_finaliter['maskname']
            if '/' not in maskname and not os.path.exists(maskname):
                maskname = os.path.join(almaimf_rootdir,
                                        'clean_regions',
                                        maskname)
            if not os.path.exists(maskname):
                raise IOError("Mask {0} not found".format(maskname))


        # if a 'final iteration' region mask is specified, use that
        regsuffix = '_finaliter_robust{0}_{1}'.format(robust, arrayname)
        regfn = os.path.join(almaimf_rootdir,
                             'clean_regions/{0}_{1}{2}.reg'.format(field,
                                                                   band,
                                                                   regsuffix))
        if os.path.exists(regfn):
            # note that imname is from the final self-calibration iteration
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        almaimf_rootdir,
                                        band,
                                        rootdir=imaging_root,
                                        suffix=regsuffix
                                       )

        for key, val in impars_finaliter.items():
            if isinstance(val, dict):
                impars_finaliter[key] = val['final'] if 'final' in val else val[selfcaliter]

        finaliterimname = contimagename+"_robust{0}_selfcal{1}_finaliter".format(robust,
                                                                                 selfcaliter)
        if 'maskname' in locals() and maskname != "" and os.path.exists(finaliterimname+".mask"):
            logprint("Removing existing mask file {0} because mask {1} exists"
                     .format(finaliterimname+".mask", maskname),
                     origin='almaimf_cont_selfcal')
            shutil.rmtree(finaliterimname+".mask")

        if os.path.exists(finaliterimname+".model.tt0"):
            # if there is already a model with this name on disk, we're continuing from that
            # one instead of starting from scratch
            modelname=''
        else:
            modelname = [contimagename+"_robust0_selfcal{0}.model.tt0".format(selfcaliter),
                         contimagename+"_robust0_selfcal{0}.model.tt1".format(selfcaliter)]
        tclean(vis=selfcal_ms,
               field=field.encode(),
               imagename=finaliterimname,
               phasecenter=phasecenter,
               startmodel=modelname,
               outframe='LSRK',
               veltype='radio',
               usemask='user',
               mask=maskname,
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               antenna=antennae,
               savemodel='none',
               datacolumn='corrected',
               pbcor=True,
               **impars_finaliter
              )
        test_tclean_success()
        ia.open(finaliterimname+".image.tt0")
        ia.sethistory(origin='almaimf_cont_selfcal',
                      history=["{0}: {1}".format(key, val) for key, val in
                               impars.items()])
        ia.sethistory(origin='almaimf_cont_imaging',
                      history=["git_version: {0}".format(git_version),
                               "git_date: {0}".format(git_date)])
        ia.close()
        # overwrite=True because these could already exist
        exportfits(finaliterimname+".image.tt0", finaliterimname+".image.tt0.fits", overwrite=True)
        exportfits(finaliterimname+".image.tt0.pbcor", finaliterimname+".image.tt0.pbcor.fits", overwrite=True)

    logprint("Completed band {0}".format(band),
             origin='contim_selfcal')
