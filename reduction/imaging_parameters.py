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
                      for field in ('W51-E', 'G008.67', 'W51-IRS2', 'G351.77',
                          'G333.60', 'G338.93')
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
                             'maskname': {0: 'clean_mask1.crtf', 1: 'clean_mask2.crtf', 2: 'clean_mask3.crtf', 3: 'clean_mask4.crtf'},
                            },
    'G338.93_B3_12M_robust0': {'threshold': {0: '1mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                'niter': {0: 1000, 1: 5000, 2: 10000, 3: 20000},
                'maskname':{0:'G338.93_B3_dirty_12M.crtf',
                    1:'G338.93_B3_selfcal1_12M.crtf',
                    2:'G338.93_B3_selfcal2_12M.crtf', 
                    3:'G338.93_B3_selfcal3_12M.crtf',
                    4:'G338.93_B3_selfcal4_12M.crtf'}
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

selfcal_pars['W51-E_B6_7M12M_robust0'][5] = selfcal_pars['W51-E_B6_7M12M_robust0'][4] # one extra phase iteration
selfcal_pars['W51-E_B6_7M12M_robust0'][6] = {'solint': 'inf',
                                             'gaintype': 'G',
                                             'calmode': 'ap',
                                            }
selfcal_pars['W51-E_B6_7M12M_robust0'][7] = {'solint': 'inf',
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
selfcal_pars['G338.93_B3_12M_robust0'][4] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'ap',
                                          }


line_imaging_parameters = {"{0}_{1}_{2}_robust{3}{4}".format(field, band, array, robust, contsub):
                           {
                            'niter': 20000,
                            'robust': robust,
                            'weighting': 'briggs',
                            'scales': [0,3,9,27,81],
                            'gridder': 'mosaic',
                            'specmode': 'cube',
                            'deconvolver': 'multiscale',
                            'outframe':'LSRK',
                            'veltype':'radio',
                            'sidelobethreshold': 1.0,
                            'noisethreshold': 5.0,
                           'usemask':'auto-multithresh',
                           }
                           for field in ('W51-E', 'G008.67', 'W51-IRS2', 'G351.77', 'G333.60')
                           for band in ('B3','B6')
                           for array in ('12M', '7M12M', '7M')
                           for robust in (-2, 0, 2)
                           for contsub in ("","_contsub")
                          }

# use the continuum image as the startmodel for the non-contsub'd data
line_imaging_parameters['W51-E_B6_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust0_selfcal7.model.tt0'
line_imaging_parameters['W51-E_B3_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7.model.tt0'
