"""
Continuum imaging scripts.  There must be a ``continuum_mses.txt`` file in the
directory this is run in.  That file is produced by ``split_windows.py``.

You can set the following environmental variables for this script:
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.

The environmental variable ``ALMAIMF_ROOTDIR`` should be set to the directory
containing this file.
"""

import os

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

from metadata_tools import determine_imsize, determine_phasecenter, logprint
from make_custom_mask import make_custom_mask
from imaging_parameters import imaging_parameters
from tasks import tclean, exportfits, plotms, split
from taskinit import msmdtool, iatool
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


# load the list of continuum MSes from a file
# (this file has one continuum MS full path, e.g. /path/to/file.ms, per line)
with open('continuum_mses.txt', 'r') as fh:
    continuum_mses = [x.strip() for x in fh.readlines()]

for continuum_ms in continuum_mses:

    # strip off .cal.ms
    basename = os.path.split(continuum_ms[:-7])[1]

    band = 'B3' if 'B3' in basename else 'B6' if 'B6' in basename else 'ERROR'

    field = basename.split("_")[0]

    if exclude_7m:
        msmd.open(continuum_ms)
        antennae = ",".join([x for x in msmd.antennanames() if 'CM' not in x])
        msmd.close()
        arrayname = '12M'

        # split out the 12M-only data to make further processing slightly
        # faster
        new_continuum_ms = continuum_ms.replace(".cal.ms", "_12M.cal.ms")
        split(vis=continuum_ms, outputvis=new_continuum_ms, antenna=antennae,
              field=field, datacolumn='data')
        continuum_ms = new_continuum_ms
    else:
        antennae = ""
        arrayname = '7M12M'

    coosys,racen,deccen = determine_phasecenter(ms=continuum_ms, field=field)
    phasecenter = "{0} {1}deg {2}deg".format(coosys, racen, deccen)
    (dra,ddec,pixscale) = list(determine_imsize(ms=continuum_ms, field=field,
                                                phasecenter=(racen,deccen),
                                                exclude_7m=exclude_7m,
                                                spw=0, pixfraction_of_fwhm=1/4.))
    imsize = [dra, ddec]
    cellsize = ['{0:0.2f}arcsec'.format(pixscale)] * 2

    contimagename = os.path.join(imaging_root, basename) + "_" + arrayname

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


    for robust in (-2, 0, 2):

        impars = imaging_parameters["{0}_{1}_{2}_robust{3}".format(field, band,
                                                                   arrayname,
                                                                   robust)]
        dirty_impars = copy.copy(impars)
        dirty_impars['niter'] = 0

        imname = contimagename+"_robust{0}_dirty".format(robust)

        if not os.path.exists(imname+".image.tt0"):
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

            ia.open(imname+".image.tt0")
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
            ia.close()

        maskname = make_custom_mask(field, imname+".image.tt0",
                                    os.getenv('ALMAIMF_ROOTDIR'),
                                    band,
                                    rootdir=imaging_root,
                                    suffix='_dirty_robust{0}_{1}'.format(robust,
                                                                         arrayname)
                                   )
        imname = contimagename+"_robust{0}".format(robust)

        if not os.path.exists(imname+".image.tt0"):
            tclean(vis=continuum_ms,
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
                   pbcor=True,
                   **impars
                  )
            ia.open(imname+".image.tt0")
            ia.sethistory(origin='almaimf_cont_imaging',
                          history=["{0}: {1}".format(key, val) for key, val in
                                   impars.items()])
            ia.close()

            exportfits(imname+".image.tt0", imname+".image.tt0.fits")
            exportfits(imname+".image.tt0.pbcor", imname+".image.tt0.pbcor.fits")
        else:
            logprint("Skipping completed file {0}".format(imname), origin='almaimf_cont_imaging')
