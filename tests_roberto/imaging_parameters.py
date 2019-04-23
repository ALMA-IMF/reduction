# set up global defaults
imaging_parameters = {"{0}_{1}_{2}_robust{3}".format(field, band, array, robust):
                      {'threshold': '1.0mJy', # RMS ~0.35 mJy
                       'pblimit': 0.1,
                       'niter': 10000,
                       'robust': robust,
                       'weighting': 'briggs',
                       'scales': [0,3,9,27],
                       'gridder': 'mosaic',
                       'specmode': 'mfs',
                       'deconvolver': 'mtmfs',
                       'nterms': 2,
                      }
                      for field in ('G333.60',)
                      for band in ('B3',)
                      for array in ('12M',)
                      for robust in (0,)
                     }

imaging_parameters_nondefault = {
    'G333.60_B3_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'}, 
			     'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                             'maskname': {0: 'clean_mask1.crtf', 1: 'clean_mask2.crtf', 2: 'clean_mask3.crtf', 3: 'clean_mask4.crtf'}
                            },
}
for key in imaging_parameters_nondefault:
    assert key in imaging_parameters
    imaging_parameters[key].update(imaging_parameters_nondefault[key])

default_selfcal_pars = {ii: {'solint': 'int',
                             'gaintype': 'G',
                             'solnorm': True,
                             'calmode': 'p'}
                        for ii in range(1,4)}

selfcal_pars = {key: default_selfcal_pars
                for key in imaging_parameters}


selfcal_pars['G333.60_B3_12M_robust0'][4] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }


