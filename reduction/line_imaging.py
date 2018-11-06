"""
Line imaging script.  There needs to be a to_image.json file in the directory
this is run in.  The to_image.json file is produced by the split_windows.py
script.

You can set the following environmental variables for this script:
    CHANCHUNKS=<number>
        The chanchunks parameter for tclean.  Depending on the version, it may
        be acceptable to specify this as -1, or it has to be positive.  This is
        the number of channels that will be imaged all at once; if this is too
        large, the data won't fit into memory and CASA will crash.
    EXCLUDE_7M=<boolean>
        If this parameter is set (to anything), the 7m data will not be
        included in the images if they are present.
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only image
        fields with this name (e.g., "W43-MM1", "W51-E", etc.)
"""

import json
import os
import numpy as np
from tasks import tclean, uvcontsub
from parse_contdotdat import parse_contdotdat, freq_selection_overlap

from taskinit import msmdtool, iatool
msmd = msmdtool()
ia = iatool()

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)

if os.getenv('FIELD_ID'):
    field_id = os.getenv('FIELD_ID')
    for band in to_image:
        to_image[band] = {key:value for key,value in to_image[band].items()
                          if key == field_id}

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

def is_7m(ms):
    """
    Determine if a measurement set includes 7m data
    """
    msmd.open(ms)
    diameter = msmd.antennadiameter(0)['value']
    msmd.close()
    if diameter == 7.0:
        return True
    else:
        return False

def get_indiv_phasecenter(ms, field):
    """
    Get the phase center of an individual field in radians
    """
    msmd.open(ms)
    field_matches = np.array([fld == field for fld in msmd.fieldnames()], dtype=bool)
    field_ids, = np.where(field_matches)
    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids]
    mean_ra = np.mean([pc['m0']['value'] for pc in ptgctrs])
    mean_dec = np.mean([pc['m1']['value'] for pc in ptgctrs])
    csys = ptgctrs[0]['refer']
    msmd.close()

    return mean_ra, mean_dec, csys

def determine_phasecenter(ms, field):
    """
    Identify the correct phasecenter for the MS (apparently, if you don't do
    this, the phase center is set to some random pointing in the mosaic)
    """

    if isinstance(ms, list):
        results = [get_indiv_phasecenter(vis, field) for vis in ms]
        csys = results[0][2]

        mean_ra = np.mean([ra for ra, dec, csys in results])
        mean_dec = np.mean([dec for ra, dec, csys in results])
    else:
        mean_ra, mean_dec, csys = get_indiv_phasecenter(ms, field)

    return (csys, mean_ra*180/np.pi, mean_dec*180/np.pi)

def get_indiv_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    cen_ra, cen_dec = phasecenter

    msmd.open(ms)

    field_matches = np.array([fld == field for fld in msmd.fieldnames()], dtype=bool)
    field_ids, = np.where(field_matches)

    antsize = msmd.antennadiameter(0)['value'] # m
    # because we're working with line-split data, we assume the reffreq comes
    # from spw 0
    freq = msmd.reffreq(spw)['m0']['value'] # Hz
    # go a little past the first null in each direction
    primary_beam = 1.25 * freq/299792458.0 / antsize
    pb_pix = primary_beam / pixscale

    ptgctrs = [msmd.phasecenter(ii) for ii in field_ids]
    furthest_ra_pix_plus = np.max([pc['m0']['value']*180/np.pi+pb_pix-cen_ra for pc in ptgctrs])
    furthest_ra_pix_minus = np.min([pc['m0']['value']*180/np.pi-pb_pix-cen_ra for pc in ptgctrs])
    furthest_dec_pix_plus = np.max([pc['m1']['value']*180/np.pi+pb_pix-cen_dec for pc in ptgctrs])
    furthest_dec_pix_minus = np.min([pc['m1']['value']*180/np.pi-pb_pix-cen_dec for pc in ptgctrs])

    msmd.close()

    dra,ddec = furthest_ra_pix_plus-furthest_ra_pix_minus, furthest_dec_pix_plus-furthest_dec_pix_minus

    # go to the next multiple of 20, since it will come up with _something_ when you do 6/5 or 5/4 * n
    return dra-(dra%20)+20, ddec-(ddec%20)+20


def determine_imsize(ms, field, phasecenter, spw=0, pixscale=0.05):

    if isinstance(ms, list):
        results = [determine_imsize(vis, field, phasecenter, spw, pixscale) for vis in ms]

        dra = np.max([ra for ra, dec in results])
        ddec = np.max([dec for ra, dec in results])
    else:
        dra,ddec = [determine_imsize(vis, field, phasecenter, spw, pixscale) for vis in ms]

    return dra, ddec

# set the 'chanchunks' parameter globally.
# CASAguides recommend chanchunks=-1, but this resulted in:
# 2018-09-05 23:16:34     SEVERE  tclean::task_tclean::   Exception from task_tclean : Invalid Gridding/FTM Parameter set : Must have at least 1 chanchunk
chanchunks = os.getenv('CHANCHUNKS') or 16

for band in to_image:
    for field in to_image[band]:
        for spw in to_image[band][field]:

            vis = list(map(str, to_image[band][field][spw]))


            if os.getenv('EXCLUDE_7M'):
                vis = [ms for ms in vis if not(is_7m(ms))]
                suffix = '12M'
            else:
                suffix = '7M12M'

            lineimagename = os.path.join(imaging_root,
                                         "{0}_{1}_spw{2}_{3}_lines".format(field,
                                                                           band,
                                                                           spw,
                                                                           suffix))


            coosys,racen,deccen = determine_phasecenter(ms=vis, field=field)
            phasecenter = "{0} {1} deg {2} deg".format(coosys, racen, deccen)
            pixscale = 0.05
            imsize = list(determine_imsize(ms=vis, field=field,
                                           phasecenter=(racen,deccen), spw=0,
                                           pixscale=pixscale)
            cellsize = ['{0}arcsec'.format(pixscale)] * 2

            dirty_tclean_made_residual = False

            # start with cube imaging

            if not os.path.exists(lineimagename+".image") and not os.path.exists(lineimagename+".residual"):
                # json is in unicode by default, but CASA rejects unicode
                # first iteration makes a dirty image to estimate the RMS
                tclean(vis=vis,
                       imagename=lineimagename,
                       field=[field.encode()]*len(vis),
                       specmode='cube',
                       outframe='LSRK',
                       veltype='radio',
                       niter=0,
                       phasecenter=phasecenter,
                       # don't use these for dirty:
                       #usemask='auto-multithresh',
                       #scales=[0,3,9,27,81],
                       deconvolver='multiscale',
                       interactive=False,
                       cell=cellsize,
                       imsize=imsize,
                       weighting='briggs',
                       robust=0.0,
                       gridder='mosaic',
                       restoringbeam='', # do not use restoringbeam='common'
                       # it results in bad edge channels dominating the beam
                       chanchunks=chanchunks)
                if os.path.exists(lineimagename+".image"):
                    # tclean with niter=0 is not supposed to produce a .image file,
                    # but if it does (and it appears to have done so on at
                    # least one run), we still want to clean the cube
                    dirty_tclean_made_residual = True
            elif not os.path.exists(lineimagename+".residual"):
                raise ValueError("The residual image is required for further imaging.")

            # the threshold needs to be computed if any imaging is to be done
            # no .image file is produced, only a residual
            ia.open(lineimagename+".residual")
            stats = ia.statistics(robust=True)
            rms = float(stats['medabsdevmed'] * 1.482602218505602)
            threshold = "{0:0.4f}Jy".format(5*rms)
            ia.close()


            if dirty_tclean_made_residual or not os.path.exists(lineimagename+".image"):
                # continue imaging using a threshold
                tclean(vis=vis,
                       imagename=lineimagename,
                       field=[field.encode()]*len(vis),
                       specmode='cube',
                       outframe='LSRK',
                       veltype='radio',
                       niter=2000,
                       threshold=threshold,
                       phasecenter=phasecenter,
                       usemask='auto-multithresh',
                       # the sidelobethreshold is very awkward/wrong with 7m+12m
                       # combined data.  Instead, favor the more direct
                       # noisethreshold
                       sidelobethreshold=1.0,
                       # start with the default of 5-sigma?
                       noisethreshold=5.0,
                       deconvolver='multiscale',
                       scales=[0,3,9,27,81],
                       interactive=False,
                       cell=cellsize,
                       imsize=imsize,
                       weighting='briggs',
                       robust=0.0,
                       gridder='mosaic',
                       restoringbeam='', # do not use restoringbeam='common'
                       # it results in bad edge channels dominating the beam
                       chanchunks=chanchunks)
                impbcor(imagename=lineimagename+'.image',
                        pbimage=lineimagename+'.pb',
                        outfile=lineimagename+'.image.pbcor', overwrite=True)


            # TODO: Save the desired files, maybe as FITS or maybe not?


            # the cont_channel_selection is purely in frequency, so it should
            # "just work"
            # (there may be several cont.dats - we're just grabbing the first)
            path = os.path.split(vis[0])[0]

            contfile = os.path.join(path, '../calibration/cont.dat')

            cont_freq_selection = parse_contdotdat(contfile)

            for vv in vis:
                if not os.path.exists(vv+".contsub"):
                    new_freq_selection = freq_selection_overlap(vv,
                                                                cont_freq_selection)
                    uvcontsub(vis=vv,
                              fitspw=new_freq_selection,
                              excludechans=False, # fit the regions in fitspw
                              combine='spw', # redundant since we're working on single spw's
                              solint='int',
                              fitorder=1,
                              want_cont=False)

            if not os.path.exists(lineimagename+".contsub.image"):
                tclean(vis=[vv+".contsub" for vv in vis],
                       imagename=lineimagename+".contsub",
                       field=[field.encode()]*len(vis),
                       specmode='cube',
                       outframe='LSRK',
                       veltype='radio',
                       niter=2000,
                       threshold=threshold,
                       usemask='auto-multithresh',
                       sidelobethreshold=1.0,
                       noisethreshold=5.0,
                       deconvolver='multiscale',
                       scales=[0,3,9,27,81],
                       interactive=False,
                       cell=cellsize,
                       imsize=imsize,
                       weighting='briggs',
                       robust=0.0,
                       gridder='mosaic',
                       restoringbeam='',
                       chanchunks=chanchunks)
                impbcor(imagename=lineimagename+'.image',
                        pbimage=lineimagename+'.pb',
                        outfile=lineimagename+'.image.pbcor', overwrite=True)
