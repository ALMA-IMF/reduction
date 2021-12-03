'''
rescale_cubes.py
'''

from beam_volume_tools import *

psf_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.psf'
model_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.model'
residual_image = '/home/roberto/ALMA_IMF/residuals_fix/6sigma/G351.77_B3_spw0_7M12M_n2hp.residual'


# Output is: {'epsilon': epsilon_arr, 'clean_beam': common_beam}
result = epsilon_from_psf(psf_image=psf_image)

# Output is: conv (spectral_cube object)
result2 = conv_model(model_image=model_image, clean_beam=result['clean_beam'])

# Output is: restor (spectral_cube object)
rescale(conv_model=result2, epsilon=result['epsilon'], residual_image=residual_image, export_fits=True)
