"""
Continuum imaging scripts.  There must be a ``continuum_mses.txt`` file in the
directory this is run in.  That file is produced by ``split_windows.py``.

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
    DO_BSENS=False
        By default, the "best sensitivity" continuum images will also be made
        if the _bsens.ms measurement sets exist.  If you set DO_BSENS=False,
        they will be skipped instead.  "Best sensitivity" means that no spectral
        lines are flagged out.
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only split
        fields with this name (e.g., "W43-MM1", "W51-E", etc.).
        Metadata will still be collected for *all* available MSes.
    BAND_TO_IMAGE=B3 or B6
        If this parameter is set, only image the selected band.

The environmental variable ``ALMAIMF_ROOTDIR`` should be set to the directory
containing this file.


Additional Notes
================
USE_SELFCAL_MS is an environmental variable you can set if you want the imaging
to be done using the selfcal.ms file instead of the default continuum MS file.
It is primarily for debug purposes and you shouldn't need it.
"""

import os, sys, argparse

try:
    # If run from command line
    aux = os.path.dirname(os.path.realpath(sys.argv[2]))
    if os.path.isdir(aux):
        almaimf_rootdir = aux
except:
    pass

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

from getversion import git_date, git_version
from metadata_tools import determine_imsize, determine_phasecenter, logprint
from make_custom_mask import make_custom_mask
from imaging_parameters import imaging_parameters
from tasks import tclean, exportfits, plotms, split
from taskinit import msmdtool, iatool
import copy
msmd = msmdtool()
ia = iatool()

imaging_root = "imaging_results"
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


# load the list of continuum MSes from a file
# (this file has one continuum MS full path, e.g. /path/to/file.ms, per line)
with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]


if os.getenv('DO_BSENS') is not None and os.getenv('DO_BSENS').lower() != 'false':
    do_bsens = True
    logprint("Using BSENS measurement set")
    continuum_mses += [x.replace('_continuum_merged.cal.ms',
                                 '_continuum_merged_bsens.cal.ms')
                       for x in continuum_mses]


for continuum_ms in continuum_mses:

    # strip off .cal.ms
    basename = os.path.split(continuum_ms[:-7])[1]

    band = 'B3' if 'B3' in basename else 'B6' if 'B6' in basename else 'ERROR'

    # allow optional cmdline args to skip one or the other band
    if os.getenv('BAND_TO_IMAGE'):
        if band not in os.getenv('BAND_TO_IMAGE'):
            logprint("Skipping band {0} because it is not in {1}"
                     .format(band, os.getenv('BAND_TO_IMAGE')),
                     origin='almaimf_cont_imaging')
            continue
        logprint("Imaging only band {0}".format(os.getenv('BAND_TO_IMAGE')),
                 origin='almaimf_cont_imaging')


    field = basename.split("_")[0]

    if os.getenv('FIELD_ID'):
        if field not in os.getenv('FIELD_ID'):
            logprint("Skipping {0} because it is not in FIELD_ID={1}"
                     .format(field, os.getenv('FIELD_ID')),
                     origin='almaimf_cont_imaging'
                    )
            continue


    suffix = "_bsens" if "bsens" in continuum_ms else ""

    if exclude_7m:
        arrayname = '12M'
        if os.getenv("USE_SELFCAL_MS"):
            antennae = ""
        else:
            logprint("Splitting MS {0} to select 12m antennae".format(continuum_ms),
                     origin='almaimf_cont_imaging')
            msmd.open(continuum_ms)
            antennae = ",".join([x for x in msmd.antennanames() if 'CM' not in x])
            msmd.close()

            if antennae == "":
                raise ValueError("No 12M antennae found; likely the 'split_windows'"
                                 " merging stage failed.")

            # split out the 12M-only data to make further processing slightly
            # faster
            new_continuum_ms = continuum_ms.replace(".cal.ms", "_12M.cal.ms")
            split(vis=continuum_ms, outputvis=new_continuum_ms, antenna=antennae,
                  field=field, datacolumn='data')
            continuum_ms = new_continuum_ms
    elif only_7m:
        arrayname = '7M'
        logprint("Splitting MS {0} to select 7m antennae".format(continuum_ms),
                 origin='almaimf_cont_imaging')
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' in x])
        msmd.close()

        if antennae == "":
            raise ValueError("No 7M antennae found; likely the 'split_windows'"
                             " merging stage failed.")

        # split out the 7M-only data to make further processing slightly
        # faster
        new_continuum_ms = continuum_ms.replace(".cal.ms", "_7M.cal.ms")
        split(vis=continuum_ms, outputvis=new_continuum_ms, antenna=antennae,
              field=field, datacolumn='data')
        continuum_ms = new_continuum_ms
    else:
        antennae = ""
        arrayname = '7M12M'

    if os.getenv("USE_SELFCAL_MS"):
        selfcal_ms = basename+"_"+arrayname+"_selfcal.ms"
        continuum_ms = selfcal_ms

    logprint("Imaging MS {0} with array {1}".format(continuum_ms, arrayname),
             origin='almaimf_cont_imaging')

    coosys,racen,deccen = determine_phasecenter(ms=continuum_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=continuum_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                exclude_7m=exclude_7m,
                                                only_7m=only_7m,
                                                spw=0, pixfraction_of_fwhm=1/4.))
    imsize = [dra, ddec]
    cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

    contimagename = os.path.join(imaging_root, basename) + "_" + arrayname + suffix



    for robust in (0, 2, -2):

        impars = imaging_parameters["{0}_{1}_{2}_robust{3}".format(field, band,
                                                                   arrayname,
                                                                   robust)]
        impars = copy.copy(impars)
        dirty_impars = copy.copy(impars)
        dirty_impars['niter'] = 0
        if 'maskname' in dirty_impars:
            maskname = dirty_impars['maskname'][0]
            del dirty_impars['maskname']

        imname = contimagename+"_robust{0}_dirty".format(robust)

        if not os.path.exists(imname+".image.tt0"):
            logprint("Dirty imaging file {0}".format(imname),
                     origin='almaimf_cont_imaging')
            tclean(vis=continuum_ms,
                   field=field.encode(),
                   imagename=imname,
                   phasecenter=phasecenter,
                   outframe='LSRK',
                   veltype='radio',
                   usemask='pb',
                   interactive=False,
                   cell=cellsize,
                   imsize=imsize,
                   antenna=antennae,
                   pbcor=True,
                   **dirty_impars
                  )

            ia.open(imname+".residual.tt0")
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["git_version: {0}".format(git_version),
                                   "git_date: {0}".format(git_date)])
            ia.close()

        try:
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        os.getenv('ALMAIMF_ROOTDIR'),
                                        band,
                                        rootdir=imaging_root,
                                        suffix='_dirty_robust{0}_{1}'.format(robust,
                                                                             arrayname)
                                       )
        except KeyError as ex:
            if 'label' in str(ex):
                logprint("Bad Region Exception: {0}".format(str(ex)))
                raise KeyError("No text label was found in one of the regions."
                               "  Regions must have text={xxJy} or {xxmJy} to "
                               "indicate the threshold level")
        except Exception as ex:
            logprint("Exception: {0}".format(str(ex)))
            logprint("Because no region file was found to create a mask, only "
                     "the dirty image was made for {0}".format(imname))
            continue
            #raise ValueError("Make the region file first!")

        # for compatibility w/self-calibration: if a list of parameters is used,
        # just use the 0'th iteration's parameters
        impars_thisiter = copy.copy(impars)
        if 'maskname' in impars_thisiter:
            maskname = impars_thisiter['maskname'][0]
            del impars_thisiter['maskname']
        for key, val in impars_thisiter.items():
            if isinstance(val, dict):
                impars_thisiter[key] = val[0]



        if 'mask' not in impars_thisiter:
            impars_thisiter['mask'] = maskname

        imname = contimagename+"_robust{0}".format(robust)

        if not os.path.exists(imname+".image.tt0"):
            logprint("Cleaning file {0}".format(imname),
                     origin='almaimf_cont_imaging')
            tclean(vis=continuum_ms,
                   field=field.encode(),
                   imagename=imname,
                   phasecenter=phasecenter,
                   outframe='LSRK',
                   veltype='radio',
                   usemask='user',
                   interactive=False,
                   cell=cellsize,
                   imsize=imsize,
                   antenna=antennae,
                   pbcor=True,
                   **impars_thisiter
                  )
            ia.open(imname+".image.tt0")
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["git_version: {0}".format(git_version),
                                   "git_date: {0}".format(git_date)])
            ia.close()

            exportfits(imname+".image.tt0", imname+".image.tt0.fits")
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")
        else:
            logprint("Skipping completed file {0}".format(imname), origin='almaimf_cont_imaging')




        # reclean step (optional)
        try:
            maskname = make_custom_mask(field, imname+".image.tt0",
                                        os.getenv('ALMAIMF_ROOTDIR'),
                                        band,
                                        rootdir=imaging_root,
                                        suffix='_clean_robust{0}_{1}'.format(robust,
                                                                             arrayname)
                                       )
        except IOError as ex:
            logprint("No cleaned-once mask found; skipping reclean")
        except KeyError as ex:
            if 'label' in str(ex):
                logprint("Bad Region Exception: {0}".format(str(ex)))
                raise KeyError("No text label was found in one of the regions."
                               "  Regions must have text={xxJy} or {xxmJy} to "
                               "indicate the threshold level")
        except Exception as ex:
            logprint("Exception: {0}".format(str(ex)))
            continue


        # for compatibility w/self-calibration: if a list of parameters is used,
        # just use the 0'th iteration's parameters
        impars_thisiter = copy.copy(impars)
        if 'maskname' in impars_thisiter:
            maskname = impars_thisiter['maskname'][0]
            del impars_thisiter['maskname']
        for key, val in impars_thisiter.items():
            if isinstance(val, dict):
                impars_thisiter[key] = val[0]



        if 'mask' not in impars_thisiter:
            impars_thisiter['mask'] = maskname

        imname = contimagename+"_reclean_robust{0}".format(robust)

        if not os.path.exists(imname+".image.tt0"):
            logprint("re-Cleaning file {0}".format(imname),
                     origin='almaimf_cont_imaging')
            tclean(vis=continuum_ms,
                   field=field.encode(),
                   imagename=imname,
                   phasecenter=phasecenter,
                   outframe='LSRK',
                   veltype='radio',
                   usemask='user',
                   interactive=False,
                   cell=cellsize,
                   imsize=imsize,
                   antenna=antennae,
                   pbcor=True,
                   **impars_thisiter
                  )
            ia.open(imname+".image.tt0")
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["git_version: {0}".format(git_version),
                                   "git_date: {0}".format(git_date)])
            ia.close()

            exportfits(imname+".image.tt0", imname+".image.tt0.fits")
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")
        else:
            logprint("Skipping completed file {0}".format(imname),
                     origin='almaimf_cont_imaging')
