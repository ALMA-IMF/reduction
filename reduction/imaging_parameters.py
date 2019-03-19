# set up global defaults
imaging_parameters = {"{0}_{1}_{2}_robust{3}".format(field, band, array, robust):
                      {'threshold': '1mJy', # RMS ~0.5-0.6 mJy
                       'pblimit': 0.1,
                       'niter': 10000,
                       'robust': robust,
                       'weighting': 'briggs',
                       'scales': [0,3,9],
                       'gridder': 'mosaic',
                       'specmode': 'mfs',
                       'deconvolver': 'mtmfs',
                       'nterms': 2,
                      }
                      for field in ('W51-E',)
                      for band in ('B3','B6')
                      for array in ('12M', '7M12M')
                      for robust in (-2, 0, 2)
                     }

imaging_parameters_nondefault = {
    'W51-E_B6_12M_robust0': {'threshold': '1mJy', # RMS ~0.5-0.6 mJy
                             'scales': [0,3,9,27],
                            },
    'W51-E_B3_12M_robust0': {'threshold': '0.5mJy', # RMS ~0.1-0.4 mJy
                             'scales': [0,3,9],
                            },
    'W51-E_B3_12M_robust2': {'threshold': '3mJy',
                             'scales': [0,3,9,27],
                            },
    'W51-E_B3_12M_robust-2': {'threshold': '1mJy',
                              'scales': [0,3,9],
                            },
    'W51-E_B6_7M12M_robust0': {'threshold': '3mJy', # RMS ~ ??
                               'scales': [0,3,9,27],
                              },
    'W51-E_B3_7M12M_robust0': {'threshold': '2mJy', # RMS ~ ??
                               'scales': [0,3,9,27],
                              },
}
for key in imaging_parameters_nondefault:
    assert key in imaging_parameters
    imaging_parameters[key].update(imaging_parameters_nondefault[key])

default_selfcal_pars = {ii: {'solint': 'int',
                             'gaintype': 'G',
                             'solnorm': True,
                             'calmode': 'p'}
                        for ii in range(1,5)}

selfcal_pars = {key: default_selfcal_pars
                for key in imaging_parameters}

selfcal_pars['W51-E_B6_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['W51-E_B6_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['W51-E_B3_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['W51-E_B3_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
