# Pylab requires this to have a visual component, so if using pylab, this should be ran from an xpra GUI session
from spectral_cube import SpectralCube
from astropy import units as u
import os

######## Input parameters here ########

#viewer('/lustre/roberto/ALMA_IMF/lines/imaging_results/W43-MM2_B6_spw1_12M_sio.residual')

#image_filename = '/lustre/roberto/ALMA_IMF/lines/imaging_results/W43-MM2_B6_spw1_12M_sio.image'
image_filename = '/lustre/roberto/ALMA_IMF/lines/imaging_results/W43-MM2-old/multiscale/W43-MM2_B6_spw5_12M_12co.image'
mask_filename = '/lustre/roberto/ALMA_IMF/lines/imaging_results/W43-MM2_B6_spw5_12M_12co_multi_2sigma' # Don't include .mask
mask_threshold = 3.0 # In mJy sigma_sio_MM2=2.5 12co_MM2=1.5 
erosion_dilation = True
erosion_iter = 3
erosion_iter_2d = 0
dilation_iter = 5
dilation_iter_2d = 0

#######################################

print("Now masking the cube at sigma threshold")
cube = SpectralCube.read(image_filename)
mask = cube > mask_threshold*u.mJy/u.beam
# Use the code below to mask the cube at a certain sigma threshold
#original code
#from casatools import image
#ia = image()
#print("Now computing boolmask")
#boolmask = mask.include().compute()

#For casa5.6

from taskinit import iatool
print("Now computing boolmask")
boolmask = mask.include()

print("Now getting coordinates from original image")
# Use the code below to output a mask file
ia.open(image_filename)
cs = ia.coordsys()
ia.close()
print("Now outputting the mask file")
ia.fromarray(outfile=mask_filename+'.mask', pixels=boolmask.astype('float')[:,None,:,:].T, csys=cs.torecord(), overwrite=True)
ia.close()

# print("Now visualizing masked cube without the circular vignette")
# Use the code below to visualize what the cube looks like without its circular vignette
# import pylab as pl; pl.ion(); pl.draw(); pl.show()
# unmasked = cube.with_mask(np.ones(cube.shape, dtype='bool'), inherit_mask=False)
# Above sometimes crashes Python. Let's try:
# unmasked = cube.with_mask(cube == cube, inherit_mask=False)

if erosion_dilation == True:
    # print("Now visualizing the erosion and dilation")
    # Use the code below to visualize the erosion and dilation
    import scipy.ndimage
    # x = boolmask[2228]
    # pl.figure()
    # pl.imshow(x)
    # y = scipy.ndimage.binary_erosion(x, iterations=2)
    # pl.imshow(y)
    # z1 = scipy.ndimage.binary_dilation(scipy.ndimage.binary_erosion(x, iterations=2), iterations=2)
    # pl.imshow(z1)
    # z2 = scipy.ndimage.binary_dilation(scipy.ndimage.binary_erosion(x, iterations=3), iterations=4)
    # pl.imshow(z2)

    print("Now calculating the eroded/dilated mask")
    # Use the code below to output an eroded/dilated mask
    boolmask_e_d = scipy.ndimage.binary_dilation(scipy.ndimage.binary_erosion(boolmask, iterations=erosion_iter), iterations=dilation_iter)
    print("Now opening the original mask to be rewritten")
    if erosion_iter_2d:
        # this might be slower - if needed we could add a progressbar
        for layerid in np.arange(boolmask_e_d.shape[0]):
            boolmask_e_d[layerid,:,:] = scipy.ndimage.binary_erosion(boolmask_e_d[layerid,:,:],
                                                                     iterations=erosion_iter_2d)
    if dilation_iter_2d:
        # this might be slower - if needed we could add a progressbar
        for layerid in np.arange(boolmask_e_d.shape[0]):
            boolmask_e_d[layerid,:,:] = scipy.ndimage.binary_dilation(boolmask_e_d[layerid,:,:],
                                                                    iterations=dilation_iter_2d)

    ia.open(mask_filename+'.mask')
    print("Now defining the eroded/dilated mask to export")
    boolmask_e_d_export = boolmask_e_d[:,None,:,:].T.astype('int')
    print("Now outputting the eroded/dilated mask")
    ia.putchunk(pixels=boolmask_e_d_export)
    ia.close()

    mask_e_d_filename = mask_filename+'_e'+str(erosion_iter)+'_d'+str(dilation_iter)+'_2dim_e'+str(erosion_iter_2d)+'_d'+str(dilation_iter_2d)
    os.rename(mask_filename+'.mask',mask_e_d_filename+'.mask')
