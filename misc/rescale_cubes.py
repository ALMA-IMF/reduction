'''
rescale_cubes.py
'''

from beam_volume_tools import *

psf_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.psf'
model_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.model'
residual_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.residual'


# Output is: {'epsilon': epsilon_arr, 'clean_beam': common_beam}
result = epsilon_from_psf(psf_image=psf_image)

# Output is: {'conv_arr': conv_arr, 'conv_model_head': model.header}
result2 = conv_model(model_image=model_image, clean_beam=result['clean_beam'])

rescale(conv_model=result2['conv_arr'], epsilon=result['epsilon'], \
residual_image=residual_image, clean_beam=result['clean_beam'], export_fits=True)
