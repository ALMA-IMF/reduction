# Script to create a startmodel for cube cleaning based on the continuum clean components
# Last modified 04.08.2020

from tasks import imregrid
from taskinit import iatool
import shutil

from metadata_tools import logprint

ia = iatool()

# Notes:
# 1) The output continuum_cube.model is what will be used as startmodel in tclean. It probably needs a better name within the pipeline framework
# 2) robust0 cleanest model .tt0 and .tt1 are used to construct continuum_cube.model. A next level of complexity would be to use the robust 1 or
# robust -1 continuum images depending on the robust param of the line tclean command.

def create_clean_model(cubeimagename, contimagename, imaging_results_path, contmodel_path=None,):
    #results_path = "./imaging_results/"  # imaging_results frmo the pipeline
    #contmodel_path = "./imaging_results_test_casatools/"  #Path with input and temporary continuum models
    if contmodel_path is None:
        contmodel_path = imaging_results_path

    # Create continuum_model.image.tt0 and .tt1 regridded to the cube spatial frame, but still with 1 spectral pix
    tt0name = "{contmodelpath}/{contimagename}.model.tt0".format(contimagename=contimagename, contmodelpath=contmodel_path)
    tt1name = "{contmodelpath}/{contimagename}.model.tt1".format(contimagename=contimagename, contmodelpath=contmodel_path)
    temp_dict_cont_tt0 = imregrid(imagename=tt0name, template="get")
    # not needed temp_dict_cont_tt1 = imregrid(imagename=tt1name, template="get")

    cubeinmodelpath = ("{results_path}/{cubeimagename}.model"
                       .format(results_path=imaging_results_path,
                               cubeimagename=cubeimagename))
    cubeoutmodelpath = ("{results_path}/{cubeimagename}.contcube.model"
                        .format(results_path=imaging_results_path,
                                cubeimagename=cubeimagename))
    temp_dict_line = imregrid(imagename=cubeinmodelpath, template="get")
    temp_dict_line['shap'][-1] = 1
    temp_dict_line['csys']['spectral2'] = temp_dict_cont_tt0['csys']['spectral2']
    temp_dict_line['csys']['worldreplace2'] = temp_dict_cont_tt0['csys']['worldreplace2']

    tt0model = ("{contmodel_path}/{cubeimagename}_continuum_model.image.tt0"
                .format(contmodel_path=contmodel_path,
                        cubeimagename=cubeimagename))
    tt1model = ("{contmodel_path}/{cubeimagename}_continuum_model.image.tt1"
                .format(contmodel_path=contmodel_path,
                        cubeimagename=cubeimagename))

    imregrid(imagename=tt0name, output=tt0model, template=temp_dict_line, overwrite=True)
    imregrid(imagename=tt1name, output=tt1model, template=temp_dict_line, overwrite=True)

    # Use CASA tools to create a model cube from the continuum model
    shutil.copytree(cubeinmodelpath, cubeoutmodelpath)

    dict_line = imregrid(imagename=cubeoutmodelpath, template="get")
    line_im = ia.newimagefromfile(cubeoutmodelpath)
    #print(line_im.shape())

    tt0_im = ia.newimagefromfile(tt0model)
    #print(tt0_im.shape())
    tt0_pixvalues = tt0_im.getchunk()
    tt0_im.close()

    tt1_im = ia.newimagefromfile(tt1model)
    #print(tt1_im.shape())
    tt1_pixvalues = tt1_im.getchunk()
    tt1_im.close()

    # From Eq. 2 of Rau & Cornwell (2011)
    # temp_dict_cont_tt0['csys']['spectral2']['wcs']
    # dict_line['csys']['spectral2']['wcs']
    # dnu_plane: dnu with respect to cube reference freq.
    # dnu: dnu with respect to tt0 continuum reference
    for plane in range(dict_line['shap'][-1]):
        logprint('Calculating continuum model for plane {}'.format(plane))
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

    return cubeoutmodelpath

    # Commented block is for the case where only tt0 info is used
    '''
    blc = [0, 0, 0, 0]
    trc = [line_im.shape()[0]-1, line_im.shape()[1]-1, 0, 0]
    line_im.putchunk(tt0_pixvalues, blc=blc, replicate=True)
    line_im.close()
    '''
