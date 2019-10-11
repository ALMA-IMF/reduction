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
    BAND_TO_IMAGE=B3 or B6
        If this parameter is set, only image the selected band.

The environmental variable ``ALMAIMF_ROOTDIR`` should be set to the directory
containing this file.


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
