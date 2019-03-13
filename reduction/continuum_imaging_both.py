"""
Continuum imaging scripts.  There must be a ``continuum_mses.txt`` file in the
directory this is run in.  That file is produced by ``split_windows.py``.

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
"""
import sys
sys.path.append('.')

import os
import json
from metadata_tools import determine_imsize, determine_phasecenter, logprint
from tasks import tclean, exportfits, plotms
from taskinit import msmdtool
msmd = msmdtool()

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

if 'exclude_7m' not in locals():
    exclude_7m=bool(os.getenv('exclude_7m'))

logprint("exclude_7m={0}".format(exclude_7m),
         origin='almaimf_contimg_both')


# load the list of continuum MSes from a file
# (this file has one continuum MS full path, e.g. /path/to/file.ms, per line)
with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]

for continuum_ms in continuum_mses:

    # strip off .cal.ms
    basename = os.path.split(continuum_ms[:-7])[1]

    field = basename.split("_")[0]

    if exclude_7m:
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' not in x])
        msmd.close()
        suffix = '12M'
    else:
        antennae = ""
        suffix = '7M12M'

    coosys,racen,deccen = determine_phasecenter(ms=continuum_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=continuum_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                spw=0))#, pixfraction_of_fwhm=1/4.))
    imsize = [dra, ddec]
    cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

    contimagename = os.path.join(imaging_root, basename) + "_" + suffix

    if not os.path.exists(contimagename+".uvwave_vs_amp.png"):
        # make a diagnostic plot to show the UV distribution
        plotms(vis=continuum_ms,
               xaxis='uvwave',
               yaxis='amp',
               avgchannel='1000', # minimum possible # of channels
               plotfile=contimagename+".uvwave_vs_amp.png",
               showlegend=True,
               showgui=False,
               antenna=antennae,
              )


# ----------------------------------------------
# CLEAN FOR THE 'CLEANEST' CONTINUUM:

    for robust in [-2, 0, 2]:
    #for robust in [0]:
        imname = contimagename+"_robust{0}".format(robust)+"_cleanest"
        logprint("Im={0}".format(imname),
                 origin='almaimf_contimg_both')
        if not os.path.exists(imname+".image.tt0"):
            tclean(vis=continuum_ms,
                   field=field.encode(),
                   imagename=imname,
                   gridder='mosaic',
                   specmode='mfs',
                   phasecenter=phasecenter,
                   deconvolver='mtmfs',
                   scales=[0,3,9,27,81],
                   nterms=2,
                   outframe='LSRK',
                   veltype='radio',
                   niter=10000,
                   # If you want to use auto-multithreshold,
                   # these parameters work more or less:
                   # growiterations=75,
                   # sidelobethreshold=0.2,
                   # minbeamfrac=0.5, #3
                   # negativethreshold=0.0,
                   # noisethreshold=3.0,lownoisethreshold=0.5,
                   # usemask='auto-multithresh',
                   usemask='pb',
                   interactive=False,#True,
                   cell=cellsize,
                   imsize=imsize,
                   weighting='briggs',
                   robust=robust,
                   pbcor=True,
                   antenna=antennae,
                   pblimit=0.1
                  )

            exportfits(imname+".image.tt0", imname+".image.tt0.fits")
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")

        logprint("Cleanest continuum images done.",
                 origin='almaimf_contimg_both')
        # ----------------------------------------------
        # CLEAN FOR THE BEST SENSITIVITY CONTINUUM:

        # Using here the splitted spw for line imaging:
        # For B3: only spw 1,2,3 is used (spw 0 is for N2H+ J=1-0)
        # For B6: only spw 6,7 is used

        with open('to_image.json', 'r') as fh:
            to_image = json.load(fh)

        for band in to_image:
            for field in to_image[band]:
                # Used for debugging
                #print band, field

                if band == 'B3':
                    continuum_ms_all=list(map(str,to_image[band][field]['1']))
                    continuum_ms_all.extend(list(map(str,to_image[band][field]['2'])))
                    continuum_ms_all.extend(list(map(str,to_image[band][field]['3'])))


                if band == 'B6':
                    continuum_ms_all=list(map(str,to_image[band][field]['7']))
                    continuum_ms_all.extend(list(map(str,to_image[band][field]['6'])))

                logprint("Continuum_ms_all={0}".format(continuum_ms_all),
                         origin='almaimf_contimg_both')

                if exclude_7m:
                    antenna_list = []
                    for cms in continuum_ms_all:
                        msmd.open(cms)
                        antenna_list.append(",".join([x for x in msmd.antennanames() if 'CM' not in x]))
                        msmd.close()
                    antennae = antenna_list
                else:
                    antenna_list = []
                    for cms in continuum_ms_all:
                        msmd.open(cms)
                        antenna_list = ""
                        msmd.close()
                    antennae = antenna_list


                logprint("Antennae={0}".format(antennae),
                         origin='almaimf_contimg_both')
                for robust in [-2, 0, 2]:
                #for robust in [0]:
                    imname = contimagename+"_robust{0}".format(robust)+"_bsens"
                    logprint("Im={0}".format(imname,continuum_ms_all),
                             origin='almaimf_contimg_both')
                    if not os.path.exists(imname+".image.tt0"):
                        tclean(vis=continuum_ms_all,
                               field=field.encode(),
                               imagename=imname,
                               gridder='mosaic',
                               specmode='mfs',
                               phasecenter=phasecenter,
                               deconvolver='mtmfs',
                               scales=[0,3,9,27,81],
                               nterms=2,
                               outframe='LSRK',
                               veltype='radio',
                               niter=10000,
                               # If you want to use auto-multithreshold,
                               # these parameters work more or less:
                               # growiterations=75,
                               # sidelobethreshold=0.2,
                               # minbeamfrac=0.5, #3
                               # negativethreshold=0.0,
                               # noisethreshold=3.0,lownoisethreshold=0.5,
                               # usemask='auto-multithresh',
                               interactive=False, #True
                               cell=cellsize,
                               imsize=imsize,
                               weighting='briggs',
                               robust=robust,
                               pbcor=True,
                               antenna=antennae,
                               pblimit=0.1
                        )

                        exportfits(imname+".image.tt0", imname+".image.tt0.fits")
                        exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")
                    else:
                        logprint("Skipping completed file {0}".format(imname),
                                 origin='almaimf_contimg_both')
