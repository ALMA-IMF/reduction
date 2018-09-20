"""
Continuum imaging scripts.  There must be a ``continuum_mses.txt`` file in the
directory this is run in.  That file is produced by ``split_windows.py``.

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
"""

import os
from tasks import tclean, exportfits, plotms

# Load the pipeline heuristics tools
from h_init_cli import h_init_cli as h_init
from hifa_importdata_cli import hifa_importdata_cli as hifa_importdata
from hif_makeimlist_cli import hif_makeimlist_cli as hif_makeimlist

from taskinit import msmdtool
msmd = msmdtool()

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]

for continuum_ms in continuum_mses:

    # strip off .cal.ms
    basename = os.path.split(continuum_ms[:-7])[1]

    field = basename.split("_")[0]

    if os.getenv('EXCLUDE_7M'):
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' not in x])
        msmd.close()
        suffix = '12M'
    else:
        antennae = ""
        suffix = '7M12M'


    contimagename = os.path.join(imaging_root, basename) + "_" + suffix

    # make a diagnostic plot to show the UV distribution
    plotms(vis=continuum_ms,
           xaxis='uvwave',
           yaxis='amp',
           avgchannel=1000, # minimum possible # of channels
           plotfile=contimagename+".uvwave_vs_amp.png",
           showlegend=True,
           showgui=False,
           antenna=antennae,
          )

    context = h_init()
    hifa_importdata(vis=continuum_ms)
    res = hif_makeimlist(specmode='mfs') # or cont, I don't know which!

    # Force a square image using the pipeline heuristic values
    imsize = [max(res.targets[0]['imsize'])]*2
    cellsize = [res.targets[0]['cell'][0]]*2


    for robust in (-2, 0, 2):
        imname = contimagename+"_robust{0}".format(robust)

        if not os.path.exists(imname+".image.tt0"):
            tclean(vis=continuum_ms,
                   field=field.encode(),
                   imagename=imname,
                   gridder='mosaic',
                   specmode='mfs',
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
                  )

            exportfits(imname+".image.tt0", imname+".image.tt0.fits")
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")
