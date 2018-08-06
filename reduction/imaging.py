"""
Assumes SPW, Field, and Band will be specified
"""

import json

with open('to_image.json', 'r') as fh:
    to_image = json.load(fh)


vis = to_image[band][field][spw]
imagename = "{0}_{1}_{2}".format(field, band, spw)

imsize = [2000, 2000]
cellsize = [0.05, 0.05]

# start with cube imaging

tclean(vis=vis,
       imagename=lineimagename, 
       field=field,
       specmode='cube',
       outframe='LSRK',
       veltype='radio', 
       niter=2000,  
       usemask='auto-multithresh',
       interactive=False,
       cell=cellsize,
       imsize=imsize, 
       weighting='briggs',
       robust=0.0,
       gridder='mosaic',
       restoringbeam='common',
       chanchunks=-1)
