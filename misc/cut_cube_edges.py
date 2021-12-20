'''
Script to cut cube edges. 
Useful mainly for full-spw cubes with a few bad channels at the edge. 
Output is a CASA image, even if input is a FITS file. 
A FITS file can be created with CASA task exportfits. 
Last modified by Roberto G-M, 16.12.2021
'''

import os
from casatasks import imhead  #CASA > 6. casatasks -> tasks for CASA 5. 
from casatasks import imsubimage

######################## Defined by user #########################
path = '/lustre/roberto/ALMA_IMF/lines/hypergator/fullcubes_12m'
cubes = [\
'G333.60_B3_spw0_12M_spw0.residual.mincube.fits', 'G333.60_B3_spw1_12M_spw1.residual.mincube.fits',\
'G333.60_B3_spw2_12M_spw2.residual.mincube.fits', 'G333.60_B3_spw3_12M_spw3.residual.mincube.fits',\
'G333.60_B6_spw0_12M_spw0.residual.mincube.fits', 'G333.60_B6_spw1_12M_spw1.residual.mincube.fits',\
'G333.60_B6_spw2_12M_spw2.residual.mincube.fits', 'G333.60_B6_spw3_12M_spw3.residual.mincube.fits',\
'G333.60_B6_spw4_12M_spw4.residual.mincube.fits', 'G333.60_B6_spw5_12M_spw5.residual.mincube.fits',\
'G333.60_B6_spw6_12M_spw6.residual.mincube.fits', 'G333.60_B6_spw7_12M_spw7.residual.mincube.fits'\
]
low_chans = 5 # Channels to cut
high_chans = 5 #Channels to cut


#################################################################


for cube in cubes:
    cube_path = os.path.join(path, cube)
    print('\nCutting '+cube_path)
    head = imhead(cube_path)
    nchans =  head['shape'][2]
    min_chan = low_chans
    max_chan = nchans - 1 - high_chans
    chan_range = str(min_chan)+'~'+str(max_chan)
    print('Channel range left in cube: '+chan_range)
    basename = os.path.splitext(cube)
    new_cube = cube.replace(basename[-1],'.cut')
    new_path = os.path.join(path, new_cube)
    if os.path.exists(new_path):
        print('Skipping file '+new_path)
        continue
    print('Creating '+new_path)
    imsubimage(imagename=cube_path, outfile=new_path, chans=chan_range)

    
