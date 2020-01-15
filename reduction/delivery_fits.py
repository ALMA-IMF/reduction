# Script that creates ALMA-IMF continuum delivery for single source and band
# Created by Roberto Galvan-Madrid on 30.10.2019
# The full delivery per source per band is made of:
# 1) this script 
# 2) the output of this script
# 3) the respective README 
# 4) imaging_parameters.py

import os
import tarfile

#########################################################################
# Define variables for delivery version, selfcal iteration to export
source = 'G333.60'
band = 'B3'
deliv_version = 'v0.1'
iter_sc = ['selfcal3','selfcal4']
impath = './imaging_results/'
#########################################################################


#files = os.system('ls -d ./imaging_results/*selfcal5*')
files = os.listdir(impath)

for iteration in iter_sc:
	matching = [s for s in files if (iteration in s and '.fits' not in s)]

	for element in matching:
		print('Exporting '+element+' to FITS format')
		exportfits(imagename=impath+element, fitsimage=impath+element+'_'+deliv_version+'.fits', overwrite=True)


files = os.listdir(impath)
matching = [s for s in files if deliv_version+'.fits' in s]


tar = tarfile.open(source+'_'+band+'_'+deliv_version+'.tar', "w")
tar.add('delivery_fits.py')
tar.add('README_'+source+'_'+band+'_'+deliv_version+'.txt')
tar.add('imaging_parameters.py')
for name in matching:
    tar.add(impath+name)
tar.close()
