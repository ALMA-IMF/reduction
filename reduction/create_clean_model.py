# Script to create a startmodel for cube cleaning based on the continuum clean components
# Last modified 04.08.2020

# Notes: 
# 1) The output continuum_cube.model is what will be used as startmodel in tclean. It probably needs a better name within the pipeline framework
# 2) robust0 cleanest model .tt0 and .tt1 are used to construct continuum_cube.model. A next level of complexity would be to use the robust 1 or 
# robust -1 continuum images depending on the robust param of the line tclean command. 

results_path = "./imaging_results/"  # imaging_results frmo the pipeline
contmodel_path = "./imaging_results_test_casatools/"  #Path with input and temporary continuum models
contmodel = ""

# Create continuum_model.image.tt0 and .tt1 regridded to the cube spatial frame, but still with 1 spectral pix
temp_dict_cont_tt0 = imregrid(imagename=contmodel_path+"G333.60_B3__continuum_merged_12M_robust0_selfcal5_finaliter.model.tt0", template="get")
temp_dict_cont_tt1 = imregrid(imagename=contmodel_path+"G333.60_B3__continuum_merged_12M_robust0_selfcal5_finaliter.model.tt1", template="get")

temp_dict_line = imregrid(imagename=results_path+"G333.60_B3_spw1_12M_h41a.model", template="get")
temp_dict_line['shap'][-1] = 1
temp_dict_line['csys']['spectral2'] = temp_dict_cont_tt0['csys']['spectral2']
temp_dict_line['csys']['worldreplace2'] = temp_dict_cont_tt0['csys']['worldreplace2']

imregrid(imagename=contmodel_path+"G333.60_B3__continuum_merged_12M_robust0_selfcal5_finaliter.model.tt0", output=contmodel_path+"continuum_model.image.tt0", template=temp_dict_line, overwrite=True)
imregrid(imagename=contmodel_path+"G333.60_B3__continuum_merged_12M_robust0_selfcal5_finaliter.model.tt1", output=contmodel_path+"continuum_model.image.tt1", template=temp_dict_line, overwrite=True)

# Use CASA tools to create a model cube from the continuum model
os.system('cp -r '+str(results_path)+'G333.60_B3_spw1_12M_h41a.model'+' '+str(contmodel_path)+'continuum_cube.model')
os.system('rm -rf '+str(results_path)+'*')

dict_line = imregrid(imagename=contmodel_path+"continuum_cube.model", template="get")
line_im = ia.newimagefromfile(contmodel_path+'continuum_cube.model')
#print(line_im.shape())

tt0_im =  ia.newimagefromfile(contmodel_path+'continuum_model.image.tt0')    
#print(tt0_im.shape())
tt0_pixvalues = tt0_im.getchunk()
tt0_im.close()

tt1_im =  ia.newimagefromfile(contmodel_path+'continuum_model.image.tt1')    
#print(tt1_im.shape())
tt1_pixvalues = tt1_im.getchunk()
tt1_im.close()

# From Eq. 2 of Rau & Cornwell (2011)
# temp_dict_cont_tt0['csys']['spectral2']['wcs']
# dict_line['csys']['spectral2']['wcs']
# dnu_plane: dnu with respect to cube reference freq. 
# dnu: dnu with respect to tt0 continuum reference
for plane in range(dict_line['shap'][-1]):
	print('Calculating continuum model for plane '+str(plane))
	dnu_plane = (plane - dict_line['csys']['spectral2']['wcs']['crpix'])*dict_line['csys']['spectral2']['wcs']['cdelt']
	nu_plane = dict_line['csys']['spectral2']['wcs']['crval'] + dnu_plane
	#print(dnu_plane, nu_plane)
	factor = (nu_plane - temp_dict_cont_tt0['csys']['spectral2']['wcs']['crval'])/temp_dict_cont_tt0['csys']['spectral2']['wcs']['crval']
	#print(factor)
	plane_pixvalues = tt0_pixvalues + factor*tt1_pixvalues
	blc = [0, 0, 0, plane]
	#trc = [line_im.shape()[0]-1, line_im.shape()[1]-1, 0, plane]
	line_im.putchunk(plane_pixvalues, blc=blc, replicate=False)
line_im.close()

# Commented block is for the case where only tt0 info is used 
'''
blc = [0, 0, 0, 0]
trc = [line_im.shape()[0]-1, line_im.shape()[1]-1, 0, 0]
line_im.putchunk(tt0_pixvalues, blc=blc, replicate=True)
line_im.close()
'''
