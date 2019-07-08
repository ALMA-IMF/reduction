"""
Imaging parameters for all continuum imaging work.

The first variable is used by ``continuum_imaging.py``.  It specifies the
parameters to be used for the first-pass imaging before any self-calibration is
done.  Please add your source name to the 'field' section.
DO NOT modify the default imaging parameters; if there are any that are
unsuitable for your target field, add them to the
``imaging_parameters_nondefault`` keyword, following the naming scheme laid out
there.

The self-calibration parameters are specified in ``selfcal_pars``.  The default is to
do 4 iterations of phase-only self calibration.  If you would like to add additional
steps, you can add them by adding new entries to the self-calibration parameter
dictionary for your source following the template laid out below.

"""
# set up global defaults
imaging_parameters = {"{0}_{1}_{2}_robust{3}".format(field, band, array, robust):
                      {'threshold': '1mJy', # RMS ~0.5-0.6 mJy
                       'pblimit': 0.1,
                       'niter': 100000,
                       'robust': robust,
                       'weighting': 'briggs',
                       'scales': [0,3,9],
                       'gridder': 'mosaic',
                       'specmode': 'mfs',
                       'deconvolver': 'mtmfs',
                       'nterms': 2,
                      }
                      for field in ('W51-E', 'G008.67', 'W51-IRS2', 'G351.77', 'G333.60')
                      for band in ('B3','B6')
                      for array in ('12M', '7M12M')
                      for robust in (-2, 0, 2)
                     }

imaging_parameters_nondefault = {
    'G333.60_B3_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'}, 
			     'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                             'maskname': {0: 'clean_mask1.crtf', 1: 'clean_mask2.crtf', 2: 'clean_mask3.crtf', 3: 'clean_mask4.crtf'},
                              },
    'W51-E_B6_12M_robust0': {'threshold': '1mJy', # RMS ~0.5-0.6 mJy
                             'scales': [0,3,9,27],
                            },
    'W51-E_B3_12M_robust0': {'threshold': '0.15mJy', # RMS ~0.1-0.4 mJy
                             'scales': [0,3,9,27],
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


# for the first image, and first selfcal
# to make the first image to be used for the first iteration of selfcal
# the cleaning is better to be relatively shallow (e.g., 4 rms)
# remove the affix "_firstim" before you make the first image, followed by the first iteration of selfcal
imaging_parameters_nondefault_firstim = {
    #12M of band 3
    'G353.41_B3_12M_robust-2': {'threshold': '1.8mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust0': {'threshold': '1.8mJy', # 4*RMS 
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust0.5': {'threshold': '2.1mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust2': {'threshold': '3.3mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    #7M12M of band 3
    'G353.41_B3_7M12M_robust-2': {'threshold': '4.4mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust0': {'threshold': '4.0mJy', # 4*RMS 
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust0.5': {'threshold': '4.0mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust2': {'threshold': '4.8mJy', # 4*RMS
                             'scales': [0,3,9,27],
                            },
    #12M of band 6
    'G353.41_B6_12M_robust-2': {'threshold': '2.9mJy', # 4*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust0': {'threshold': '2.2mJy', # 4*RMS 
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust0.5': {'threshold': '1.5mJy', # 4*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust2': {'threshold': '1.6mJy', # 4*RMS
                             'scales': [0,3,9],
                            },
    #7M12M of band 6
    'G353.41_B6_7M12M_robust-2': {'threshold': '3.1mJy', # 4*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust0': {'threshold': '2.5mJy', # 4*RMS 
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust0.5': {'threshold': '2.3mJy', # 4*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust2': {'threshold': '3.4mJy', # 4*RMS
                             'scales': [0,3,9],
                            }

}


# for selfcal2,selfcal3, ....
# after the first selfcal, we can clean deeper (e.g., 2rms as the threshold)
# remove the affix "_selfcalX" before starting selfcal2, selfcal3, ...

imaging_parameters_nondefault_selfcalX = {
    #12M of band 3
    'G353.41_B3_12M_robust-2': {'threshold': '0.5mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust0': {'threshold': '0.36mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust0.5': {'threshold': '0.26mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust2': {'threshold': '0.28mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    #7M12M of band 3
    'G353.41_B3_7M12M_robust-2': {'threshold': '0.52mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust0': {'threshold': '0.4mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust0.5': {'threshold': '0.36mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_7M12M_robust2': {'threshold': '0.42mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    #12M of band 6
    'G353.41_B6_12M_robust-2': {'threshold': '1.4mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust0': {'threshold': '1.04mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust0.5': {'threshold': '0.74mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_12M_robust2': {'threshold': '0.74mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    #7M12M of band 6
    'G353.41_B6_7M12M_robust-2': {'threshold': '1.4mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust0': {'threshold': '1.06mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust0.5': {'threshold': '0.8mJy', # 2*RMS
                             'scales': [0,3,9],
                            },
    'G353.41_B6_7M12M_robust2': {'threshold': '0.82mJy', # 2*RMS
                             'scales': [0,3,9],
                            },

}


selfcal_pars['G353.41_B6_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B6_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B3_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B3_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B6_7M12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B6_7M12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B3_7M12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['G353.41_B3_7M12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }



for key in imaging_parameters_nondefault:
    assert key in imaging_parameters
    imaging_parameters[key].update(imaging_parameters_nondefault[key])



"""
Self-calibration parameters are defined here
"""

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
selfcal_pars['W51-E_B3_12M_robust0'][5] = selfcal_pars['W51-E_B3_12M_robust0'][4]
selfcal_pars['W51-E_B3_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['W51-E_B3_12M_robust0'][7] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }

selfcal_pars['G333.60_B3_12M_robust0'][4] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }

