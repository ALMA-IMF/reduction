"""
Imaging parameters for all continuum imaging work.

The first variable is used by ``continuum_imaging.py``.  It specifies the
parameters to be used for the first-pass imaging before any self-calibration is
done.  Please add your source name to the 'field' section.
DO NOT modify the default imaging parameters; if there are any that are
unsuitable for your target field, add them to the
``imaging_parameters_nondefault`` keyword, following the naming scheme laid out
there.

If you want to specify a different set of imaging parameters, you can do so by
passing a dictionary instead of a single number.  For example, instead of
    threshold: '1mJy'
you can use
    threshold: {0: '2mJy', 1:'1mJy', 2:'0.75mJy'}
The requirements are:
    (1) you must have a zero entry (which is used by continuum_imaging.py)
    (2) you must have the same number of entries in each dictionary as there
    are in the calibration parameters list below

The self-calibration parameters are specified in ``selfcal_pars``.  The default is to
do 4 iterations of phase-only self calibration.  If you would like to add additional
steps, you can add them by adding new entries to the self-calibration parameter
dictionary for your source following the template laid out below.

"""
import copy
allfields = "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split()

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
                      for field in allfields
                      for band in ('B3','B6')
                      for array in ('12M', '7M12M', '7M')
                      for robust in (-2, 0, 2)
                     }

# added for 7M only data: higher threshold
for key in imaging_parameters:
    if '_7M_' in key:
        imaging_parameters[key]['threshold'] = '5mJy'
    if '7M' in key:
        imaging_parameters[key]['scales'] = [0,3,9,27]


imaging_parameters_nondefault = {
    'G333.60_B3_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                               'maskname': {0: 'clean_mask1_G333_B3.crtf', 1: 'clean_mask2_G333_B3.crtf', 2: 'clean_mask3_G333_B3.crtf', 3: 'clean_mask4_G333_B3.crtf'},
                              },
    'G333.60_B6_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                               'niter': {0: 2000, 1: 6000, 2: 18000, 3: 36000},
                               'maskname': {0: 'cleanmask_G333_B6_1.crtf', 1: 'cleanmask_G333_B6_2.crtf', 2: 'cleanmask_G333_B6_3.crtf', 3: 'cleanmask_G333_B6_4.crtf'},
                              },
    'G008.67_B6_12M_robust0': {'maskname': {0: 'G008.67_B6_12M_robust0.crtf',
                                            1: 'G008.67_B6_12M_robust0.crtf',}},
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
       #12M of band 3
    'G353.41_B3_12M_robust-2': {'threshold': '0.5mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    'G353.41_B3_12M_robust0': {'threshold': '0.36mJy', # 2*RMS
                             'scales': [0,3,9,27],
                            },
    #'G353.41_B3_12M_robust0.5': {'threshold': '0.26mJy', # 2*RMS
    #                         'scales': [0,3,9,27],
    #                        },
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
    #'G353.41_B3_7M12M_robust0.5': {'threshold': '0.36mJy', # 2*RMS
    #                         'scales': [0,3,9,27],
    #                        },
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
    #'G353.41_B6_12M_robust0.5': {'threshold': '0.74mJy', # 2*RMS
    #                         'scales': [0,3,9],
    #                        },
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
    #'G353.41_B6_7M12M_robust0.5': {'threshold': '0.8mJy', # 2*RMS
    #                         'scales': [0,3,9],
    #                        },
    'G353.41_B6_7M12M_robust2': {'threshold': '0.82mJy', # 2*RMS
                             'scales': [0,3,9],
                            },

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

selfcal_pars = {key: copy.copy(default_selfcal_pars)
                for key in imaging_parameters}

selfcal_pars['W51-E_B6_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }
selfcal_pars['W51-E_B6_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }

selfcal_pars['W51-E_B6_7M12M_robust0'][5] = copy.copy(selfcal_pars['W51-E_B6_7M12M_robust0'][4]) # one extra phase iteration
selfcal_pars['W51-E_B6_7M12M_robust0'][6] = {'solint': 'inf',
                                             'gaintype': 'G',
                                             'calmode': 'ap',
                                            }
selfcal_pars['W51-E_B6_7M12M_robust0'][7] = {'solint': 'inf',
                                             'gaintype': 'G',
                                             'calmode': 'ap',
                                            }

selfcal_pars['W51-E_B3_12M_robust0'][5] = copy.copy(selfcal_pars['W51-E_B3_12M_robust0'][4])
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




line_imaging_parameters = {"{0}_{1}_{2}_robust{3}{4}".format(field, band, array, robust, contsub):
                           {
                            'niter': 1000, # start with a light cleaning...
                            'robust': robust,
                            'weighting': 'briggs',
                            'scales': [0,3,9,27,81],
                            'gridder': 'mosaic',
                            'specmode': 'cube',
                            'deconvolver': 'multiscale',
                            'outframe': 'LSRK',
                            'veltype': 'radio',
                            #'sidelobethreshold': 1.0,
                            #'noisethreshold': 5.0,
                            #'usemask': 'auto-multithresh',
                            'threshold': '3.0mJy/beam',
                            'interactive': False,
                            'pblimit': 0.2,
                            'nterms': 1
                           }
                           for field in allfields
                           for band in ('B3','B6')
                           for array in ('12M', '7M12M', '7M')
                           for robust in (-2, 0, 2)
                           for contsub in ("","_contsub")
                          }

default_lines = {'n2hp': '93.173700GHz',
                 'sio': '217.104984GHz',
                 'h2co303': '218.222195GHz',
                 '12co': '230.538GHz',
                 'h30a': '231.900928GHz',
                 'h41a': '92.034434GHz',
                }
field_vlsr = {'W51-E': '55km/s',
              'W51-IRS2': '55km/s',
              'G010.62': '-2km/s',
              'G353.41': '-18km/s',
              'W43-MM1': '97km/s',
              'W43-MM2': '97km/s',
              'W43-MM3': '97km/s',
              'G337.92': '-40km/s',
              'G338.93': '-62km/s',
              'G328.25': '-43km/s',
              'G327.29': '-45km/s',
              'G333.60': '-47km/s',
              'G008.67': '37.60km/s',
              'G012.80': '37.00km/s',
              'G351.77': '-3.00km/s',
             }
line_parameters = {field: {line: {'restfreq': freq,
                                  'vlsr': field_vlsr[field],
                                  'cubewidth':'50km/s'}
                           for line, freq in default_lines.items()}
                   for field in allfields}

line_parameters['G353.41']['n2hp']['cubewidth'] = '32km/s'
line_parameters['W51-E']['n2hp']['cubewidth'] = '60km/s'
line_parameters['G010.62']['n2hp']['cubewidth'] = '60km/s'
line_parameters['G338.93']['sio']['cubewidth'] = '120km/s'

for field in allfields:
    line_parameters[field]['12co']['cubewidth'] = '150km/s'

# use the continuum image as the startmodel for the non-contsub'd data
line_imaging_parameters['W51-E_B6_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust0_selfcal7.model.tt0'
#line_imaging_parameters['W51-E_B3_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7.model.tt0'
