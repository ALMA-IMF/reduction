"""
Continuum imaging scripts.  There must be a ``continuum_mses.txt`` file in the
directory this is run in.  That file is produced by ``split_windows.py``.

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
"""

import os
from metadata_tools import determine_imsize, determine_phasecenter, logprint
import automasking_params

from tasks import tclean, exportfits, plotms

from gaincal_cli import gaincal_cli as gaincal
from rmtables_cli import rmtables_cli as rmtables
from applycal_cli import applycal_cli as applycal
from exportfits_cli import exportfits_cli as exportfits

from taskinit import msmdtool
msmd = msmdtool()

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

if 'exclude_7m' not in locals():
    if os.getenv('EXCLUDE_7M') is not None:
        exclude_7m = bool(os.getenv('EXCLUDE_7M').lower() == 'true')
    else:
        exclude_7m = False


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
        parkw = "12m_long" # keyword for automasking parameters
    else:
        antennae = ""
        suffix = '7M12M'
        parkw = "7m12m"

    coosys,racen,deccen = determine_phasecenter(ms=continuum_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=continuum_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                spw=0, pixfraction_of_fwhm=1/4.))
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


    # only do robust = 0
    robust = 0
    imname = contimagename+"_robust{0}".format(robust)

    if not os.path.exists(imname+".image.tt0"):
        # do this even if the output file exists: we need to populate the
        # modelcolumn
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
               usemask='auto-multithresh',
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               weighting='briggs',
               robust=robust,
               # be _very_ conservative with the first clean (negative pb means
               # only mask with this pb)
               pblimit=-0.6,
               pbcor=True,
               antenna=antennae,
               savemodel='modelcolumn',
               datacolumn='data', # need to use original (pipeline-calibrated) data here!
               **automasking_params.continuum[parkw],
              )
        # overwrite=True because these could already exist
        exportfits(imname+".image.tt0", imname+".image.tt0.fits", overwrite=True)
        exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits", overwrite=True)

    # iteration #1 of phase-only self-calibration
    caltable = '{0}_phase{1}_int.cal'.format(basename, 1)
    if not os.path.exists(caltable):
        gaincal(vis=continuum_ms,
                caltable=caltable,
                solint='int',
                gaintype='G',
                calmode='p',
                solnorm=True)

    imname = contimagename+"_robust{0}_selfcal1".format(robust)

    if not os.path.exists(imname+".image.tt0"):
        applycal(vis=continuum_ms,
                 gaintable=[caltable],
                 interp='linear',
                 applymode='calonly',
                 calwt=True)

        # do this even if the output file exists: we need to populate the
        # modelcolumn
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
               usemask='auto-multithresh',
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               weighting='briggs',
               robust=robust,
               pbcor=True,
               antenna=antennae,
               pblimit=-0.5, # be somewhat conservative with the second clean
               savemodel='modelcolumn',
               datacolumn='corrected', # now use corrected data
               **automasking_params.continuum[parkw],
              )
        # overwrite=True because these could already exist
        exportfits(imname+".image.tt0", imname+".image.tt0.fits", overwrite=True)
        exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits", overwrite=True)


    # do a second iteration, because the first was pretty effective
    # This second iteration should have very little effect

    # iteration #2 of phase-only self-calibration
    selfcaliter = 2
    caltable = '{0}_phase{1}_int.cal'.format(basename, selfcaliter)
    if not os.path.exists(caltable):
        gaincal(vis=continuum_ms,
                caltable=caltable,
                solint='int',
                gaintype='G',
                calmode='p',
                solnorm=True)

    imname = contimagename+"_robust{0}_selfcal{1}".format(robust, selfcaliter)

    if not os.path.exists(imname+".image.tt0"):
        applycal(vis=continuum_ms,
                 gaintable=[caltable],
                 interp='linear',
                 applymode='calonly',
                 calwt=True)


        # do this even if the output file exists: we need to populate the
        # modelcolumn
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
               usemask='auto-multithresh',
               interactive=False,
               cell=cellsize,
               imsize=imsize,
               weighting='briggs',
               robust=robust,
               pbcor=True,
               antenna=antennae,
               pblimit=-0.5, # be somewhat conservative with the second clean
               savemodel='modelcolumn',
               datacolumn='corrected', # now use corrected data
               **automasking_params.continuum[parkw],
              )
        # overwrite=True because these could already exist
        exportfits(imname+".image.tt0", imname+".image.tt0.fits", overwrite=True)
        exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits", overwrite=True)
