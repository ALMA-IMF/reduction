# Script that applies selfcalibration of continuum data to line data # 
# Last modified on 30.04.2020 by Roberto Galvan

######## USER PARAMETERS ################
# caltables is a list of strings with  the names of the continuum selfcal tables in the order to be applied. 
caltables = ['G333.60_B3__continuum_merged_12M_phase1_inf.cal',
'G333.60_B3__continuum_merged_12M_phase2_15s.cal',
'G333.60_B3__continuum_merged_12M_phase3_5s.cal',
'G333.60_B3__continuum_merged_12M_phase4_int.cal',
'G333.60_B3__continuum_merged_12M_amp5_inf.cal']

# vis_presc is a list of strings with the names of the line ms output from split_windows.py
vis_presc = ['uid___A002_Xc8ed16_X5c3d_G333.60_B3_spw1.split.contsub','uid___A002_Xcd07af_X41d5_G333.60_B3_spw1.split.contsub']
#vis_presc = ['uid___A002_Xc8ed16_X5c3d_G333.60_B3_spw1.split']

# TRICKY #  
# spw_presc are the spw numbers in the continuum_merged.cal.ms file
# The number of elements in this list is equal to the number of different line ms files in vis_presc
spw_presc = [21,25]

# fields is the number of pointings in the mossaic
fields = 14 
# shift is needed for renumbering the mosaic pointings to field ID 1,2,3,...
shift = 6



###########################################

import os
import numpy as np


# Cycle to create separate '.selfcal' line ms files, similar to the way continuum was selfcalibrated
for element in range(len(vis_presc)):
	print('Running split in '+vis_presc[element])
	os.system('rm -rf '+vis_presc[element]+'.selfcal')
	split(vis=vis_presc[element],outputvis=vis_presc[element]+'.selfcal',datacolumn='data')


# Clearcal 
for element in range(len(vis_presc)):
	print('Running clearcal in '+vis_presc[element]+'.selfcal')
	clearcal(vis=vis_presc[element]+'.selfcal',field='',spw='',intent='',addmodel=True)



# Create new calibration tables for line ms's from tables for continuum
line_caltables = [[vis_presc[x][19:40]+'_'+caltables[y][29:39]+'.cal' for y in range(len(caltables))] for x in range(len(vis_presc))]


# Create one calibration table for each continuum cal table for each line ms
# The tricky part is to renumber the spws and field numbers
for x in range(len(vis_presc)):
	for y in range(len(caltables)):
		#print(caltables[y])
		#print('SPECTRAL_WINDOW_ID=='+str(spw_presc[x]))
		#print(line_caltables[x][y])
		print('Working on cal table '+line_caltables[x][y])
		os.system('rm -rf '+line_caltables[x][y])
		tb.open(caltables[y])
		subt = tb.query('SPECTRAL_WINDOW_ID=='+str(spw_presc[x]))
		newt = subt.copy(newtablename=line_caltables[x][y], deep=True, valuecopy=True)
		newt.close()
		subt.close()
		tb.close()
		tb.open(line_caltables[x][y], nomodify=False)
		#tb.colnames()
		field = tb.getcol('FIELD_ID')
		#field.shape
		for element in range(fields):
			#print(element+1+shift)
			#print(element+1)
			field = np.where(field==element+1+shift, element+1, field)
		tb.putcol('FIELD_ID', field)
		spw = tb.getcol('SPECTRAL_WINDOW_ID')
		#spw.shape
		spw = np.where(spw==spw_presc[x], 0, spw)
		tb.putcol('SPECTRAL_WINDOW_ID', spw)
		tb.flush()
		tb.close()


# Applycal
# Filling spwmap has not been automatized and script will break is there is different number of tables
for element in range(len(vis_presc)):
	print('Applying calibration table to '+vis_presc[element]+'.selfcal')
	applycal(vis=vis_presc[element]+'.selfcal',field='',spw='0',spwmap=[[0],[0],[0],[0],[0]],gaintable=line_caltables[element],interp='',calwt=False,applymode='calonly')
	

