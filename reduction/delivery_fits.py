# Script that creates ALMA-IMF continuum delivery for single source and band
# Created by Roberto Galvan-Madrid on 30.10.2019
# Last modified 26.03.2020
# The full delivery per source per band is made of:
# 1) the output of this script
# 2) the respective README 

import os
import tarfile

#########################################################################
# Define variables for delivery version, selfcal iteration to export
source = 'G333.60'
band = 'B3'
deliv_version = 'v0.2'
imtype = '12M'  # '12M' for cleanest cont. or 'bsens' or '7M12M'
iter_sc = ['preselfcal','finaliter']
impath = './imaging_results/'
readme = 'README_G333.60_B3_12M_cleanest_v0.2.txt'
#########################################################################
tar = tarfile.open(source+'_'+band+'_'+imtype+'_'+deliv_version+'.tar', "w")
#tar.add('delivery_fits.py')
tar.add(readme)
#tar.add('imaging_parameters.py')

#files = os.system('ls -d ./imaging_results/*selfcal5*')
files = os.listdir(impath)

for iteration in iter_sc:
	matching = [s for s in files if ((iteration in s) and ('.fits' not in s) and ('dirty' not in s) and (imtype in s) and ('tt0' in s))]
	matching_fits = [s for s in files if ((iteration in s) and ('.fits' in s) and ('dirty' not in s) and (imtype in s) and ('tt0' in s))]

	for element in matching:
		print('Exporting '+element+' to FITS format and adding to tar file')
		exportfits(imagename=impath+element, fitsimage=impath+element+'.fits', overwrite=True)
		tar.add(impath+element+'.fits')
	for element in matching_fits:
		print('Adding to tar file files that were already in FITS format: '+element)
		tar.add(impath+element)


#files = os.listdir(impath)
#matching = [s for s in files if deliv_version+'.fits' in s]

tar.close()
