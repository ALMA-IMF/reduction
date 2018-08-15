"""
Assumes SPW, Field, and Band will be specified
"""

import json
import os
from tasks import tclean, uvcontsub
from parse_contdotdat import parse_contdotdat, freq_selection_overlap
from spectral_cube import SpectralCube
from astropy import units as u

# Load the pipeline heuristics tools
from h_init_cli import h_init_cli as h_init
from hifa_importdata_cli import hifa_importdata_cli as hifa_importdata
from hif_makeimlist_cli import hif_makeimlist_cli as hif_makeimlist

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)

imaging_root = "imaging_results"
if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)

for band in to_image:
    for field in to_image[band]:
        for spw in to_image[band][field]:

            vis = list(map(str, to_image[band][field][spw]))
            lineimagename = os.path.join(imaging_root,
                                         "{0}_{1}_spw{2}_lines".format(field, band, spw))

            context = h_init()
            hifa_importdata(vis=vis)
            res = hif_makeimlist(specmode='cube')

            # Force a square image
            imsize = [max(res.targets[0]['imsize'])]*2
            cellsize = [res.targets[0]['cell'][0]]*2

            # start with cube imaging

            if not os.path.exists(lineimagename+".image"):
                # json is in unicode by default, but CASA rejects unicode
                # first iteration makes a dirty image to estimate the RMS
                tclean(vis=vis,
                       imagename=lineimagename,
                       field=[field.encode()]*len(vis),
                       specmode='cube',
                       outframe='LSRK',
                       veltype='radio',
                       niter=0,
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
                       chanchunks=-1)

                # estimate RMS
                imgcube = SpectralCube.read(lineimagename+".image",
                                            format='casa_image')
                rms = imgcube.with_mask(imgcube != 0*imgcube.unit).mad_std()
                if rms.unit.is_equivalent(u.Jy):
                    threshold = "{0}mJy".format(rms.to(u.mJy).value * 3)
                else:
                    # assume Jy
                    threshold = "{0}mJy".format(rms.value / 1e3 * 3)


                # continue imaging using a threshold
                tclean(vis=vis,
                       imagename=lineimagename,
                       field=[field.encode()]*len(vis),
                       specmode='cube',
                       outframe='LSRK',
                       veltype='radio',
                       niter=2000,
                       threshold=threshold,
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
                       chanchunks=-1)


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
                       chanchunks=-1)
