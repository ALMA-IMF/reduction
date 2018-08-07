"""
Assumes SPW, Field, and Band will be specified
"""

import json
from tasks import tclean

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)


for band in to_image:
    for field in to_image[band]:
        for spw in to_image[band][field]:

            vis = to_image[band][field][spw]
            lineimagename = "{0}_{1}_spw{2}_lines".format(field, band, spw)

            imsize = [2000, 2000]
            cellsize = [0.05, 0.05]

            # start with cube imaging

            # json is in unicode by default, but CASA rejects unicode
            tclean(vis=list(map(str, vis)),
                   imagename=lineimagename, 
                   field=field,
                   specmode='cube',
                   outframe='LSRK',
                   veltype='radio', 
                   niter=2000,  
                   usemask='auto-multithresh',
                   deconvolver='multiscale',
                   scales=[0,3,9,27,81],
                   interactive=False,
                   cell=cellsize,
                   imsize=imsize, 
                   weighting='briggs',
                   robust=0.0,
                   gridder='mosaic',
                   restoringbeam='common',
                   chanchunks=-1)


            # TODO: Save the desired files, maybe as FITS or maybe not?
