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


You can copy any set of parameters and add `_bsens` to the end of the name to
have it use special parameters only for the bsens imaging.  For example:
    'G010.62_B3_12M_robust0': {...},
    'G010.62_B3_12M_robust0_bsens: {...},'
would be the parameters used for non-bsens and for bsens data, respectively.
If you have ONLY a non-bsens parameter key (you do not have a _bsens set
of parameters), the bsens selfcal & imaging will use the same as the non-bsens.

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
                       'usemask': 'user',
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
# G351.77
  'G351.77_B6_7M12M_robust0': {'threshold': {0: '4.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                               'maskname': {0: 'G351.77_B6_7M12M_robust-2.crtf',
                                            1: 'G351.77_B6_7M12M_robust-2.crtf',
                                            2: 'G351.77_B6_7M12M_robust-2.crtf',
                                            3: 'G351.77_B6_7M12M_robust-2.crtf'}
                              },

   'G351.77_B6_7M12M_robust2': {'threshold': {0: '4.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                               'maskname': {0: 'G351.77_B6_7M12M_robust-2.crtf',
                                            1: 'G351.77_B6_7M12M_robust-2.crtf',
                                            2: 'G351.77_B6_7M12M_robust-2.crtf',
                                            3: 'G351.77_B6_7M12M_robust-2.crtf'}
                              },

  'G351.77_B6_7M12M_robust-2': {'threshold': {0: '4.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000},
                               'maskname': {0: 'G351.77_B6_7M12M_robust-2.crtf',
                                            1: 'G351.77_B6_7M12M_robust-2.crtf',
                                            2: 'G351.77_B6_7M12M_robust-2.crtf',
                                            3: 'G351.77_B6_7M12M_robust-2.crtf'}
                              },

                                                #rms:6e-4
   'G351.77_B6_12M_robust0': {'threshold': {0: '12e-4Jy', 1: '12e-4Jy', 2: '12e-4Jy', 3: '12e-4Jy',4: '12e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'maskname': {0: 'G351.77_B6_12M_robust2.crtf',
                                            1: 'G351.77_B6_12M_robust2.crtf',
                                            2: 'G351.77_B6_12M_robust2.crtf',
                                            3: 'G351.77_B6_12M_robust2.crtf',
                                            4: 'G351.77_B6_12M_robust2.crtf'}
                              },

                                               #rms: 5e-4
   'G351.77_B6_12M_robust2': {'threshold': {0: '10e-4Jy', 1: '10e-4Jy', 2: '10e-4Jy', 3: '10e-4Jy', 4: '10e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B6_12M_robust2.crtf',
                                            1: 'G351.77_B6_12M_robust2.crtf',
                                            2: 'G351.77_B6_12M_robust2.crtf',
                                            3: 'G351.77_B6_12M_robust2.crtf',
                                            4: 'G351.77_B6_12M_robust2.crtf'}
                              },
                                                 # rms: 7.2e-4
   'G351.77_B6_12M_robust-2': {'threshold': {0: '14.4e-4Jy', 1: '14.4e-4Jy', 2: '14.4e-4Jy', 3: '14.4e-4Jy', 4: '14.4e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B6_12M_robust-2.crtf',
                                            1: 'G351.77_B6_12M_robust-2.crtf',
                                            2: 'G351.77_B6_12M_robust-2.crtf',
                                            3: 'G351.77_B6_12M_robust-2.crtf',
                                            4: 'G351.77_B6_12M_robust-2.crtf'}
                              },




 'G351.77_B3_12M_robust-2': {'threshold': {0: '8e-4Jy', 1: '8e-4Jy', 2: '8e-4Jy', 3: '8e-4Jy', 4: '8e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2.crtf',
                                            1: 'G351.77_B3_12M_robust2.crtf',
                                            2: 'G351.77_B3_12M_robust2.crtf',
                                            3: 'G351.77_B3_12M_robust2.crtf',
                                            4: 'G351.77_B3_12M_robust2.crtf'}
                              },
                                                # rms: 2.7e-4
   'G351.77_B3_12M_robust2': {'threshold': {0: '5.4e-4Jy', 1: '5.4e-4Jy', 2: '5.4e-4Jy', 3: '5.4e-4Jy', 4: '5.4e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2.crtf',
                                            1: 'G351.77_B3_12M_robust2.crtf',
                                            2: 'G351.77_B3_12M_robust2.crtf',
                                            3: 'G351.77_B3_12M_robust2.crtf',
                                            4: 'G351.77_B3_12M_robust2.crtf'}
                              },
  'G351.77_B3_12M_robust0': {'threshold': {0: '7e-4Jy', 1: '7e-4Jy', 2: '7e-4Jy', 3: '7e-4Jy', 4: '7e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2.crtf',
                                            1: 'G351.77_B3_12M_robust2.crtf',
                                            2: 'G351.77_B3_12M_robust2.crtf',
                                            3: 'G351.77_B3_12M_robust2.crtf',
                                            4: 'G351.77_B3_12M_robust2.crtf'}
                              },




'G010.62_B3_12M_robust0': {'threshold': {0:'10mJy', 1: '5mJy', 2: '2.5 mJy', 3:'0.8mJy', 4:'0.2mJy',5:'0.14mJy'},
                                 'niter':{0:700, 1:700, 2: 2000, 3: 5000, 4: 10000, 5:15000},
                                 'maskname':{0:'G010.62_55arcsecCircle.crtf',
                                             1:'G010_ds9_15mJy.crtf', # 
                                             2:'G010_ds9_15mJy.crtf', # 
                                             3:'G010_ds9_1mJy.crtf', # 
                                             4:'G010_ds9_0.5mJy.crtf', # 
                                             5:'G010_ds9_0.3mJy.crtf'}
                       },
'G010.62_B3_7M12M_robust0': {'threshold': {0:'10mJy', 1: '5mJy', 2: '2.5 mJy', 3:'0.8mJy', 4:'0.5mJy',5:'0.32mJy'},
                                 'niter':{0:700, 1:1300, 2: 2500, 3: 5000, 4: 15000, 5:15000},
                                 'maskname':{0:'G010.62_55arcsecCircle.crtf',
                                             1:'G010_ds9_15mJy.crtf', # 
                                             2:'G010_ds9_15mJy.crtf', # 
                                             3:'G010_ds9_1mJy.crtf', # 
                                             4:'G010_ds9_0.5mJy.crtf', # 
                                             5:'G010_ds9_0.3mJy.crtf'}
                       },
'G010.62_B6_12M_robust0': {'threshold': {0:'10mJy', 1: '5mJy', 2: '2.5 mJy', 3:'0.8mJy', 4:'0.35mJy',5:'0.2mJy'},
                                 'niter':{0:700, 1:1300, 2: 2500, 3: 5000, 4: 15000, 5:15000},
                                 'maskname':{
                                     0:'G010.62_bigPoly.crtf',
                                     1:'G010_ds9_B6_20mJy.crtf', # 
                                     2:'G010_ds9_B6_5mJy.crtf', # 
                                     3:'G010_ds9_B6_1mJy.crtf', # 
                                     4:'G010_ds9_B6_05mJy.crtf', # 
                                     5:'G010.62_B6_03mJy.mask'}
                       },
        ##### G333.60 #####
        # B3 12M CLEANEST CONTINUUM #
    'G333.60_B3_12M_robust0': {'threshold': {0: '0.8mJy', 1: '0.8mJy', 2: '0.4mJy', 3: '0.2mJy', 4: '0.1mJy', 5: '0.07mJy'},
                               'niter': {0: 3000, 1: 3000, 2: 10000, 3: 30000, 4: 90000, 5: 90000},
                               'maskname': {0: 'mask_G333_B3_12m_0.1.crtf',
                                            1: 'mask_G333_B3_12m_0.1.crtf',
                                            2: 'mask_G333_B3_12m_0.03.crtf',
                                            3: 'mask_G333_B3_12m_0.01.crtf',
                                            4: 'mask_G333_B3_12m_0.003.crtf',
                                                                                        5: 'mask_G333_B3_12m_0.0015.crtf'},
                               'scales': [0,3,9,27],
                              },
    'G333.60_B3_12M_robust2': {'threshold': '0.07mJy', 'niter': 90000,
                               'scales': [0,3,9],
                               'maskname': 'mask_G333_B3_12m_0.0015.crtf',
                              },
    'G333.60_B3_12M_robust-2': {'threshold': '0.07mJy', 'niter': 90000,
                                'scales': [0,3,9,27],
                                'maskname': 'mask_G333_B3_12m_0.0015.crtf',
                            },
        # B3 7m12M CLEANEST CONTINUUM #
    'G333.60_B3_7M12M_robust0': {'threshold': {0: '0.8mJy', 1: '0.8mJy', 2: '0.4mJy', 3: '0.2mJy', 4: '0.1mJy', 5: '0.07mJy'},
                               'niter': {0: 3000, 1: 3000, 2: 10000, 3: 30000, 4: 90000, 5: 90000},
                               'maskname': {0: 'mask_G333_B3_7m12m_0.1.crtf',
                                            1: 'mask_G333_B3_7m12m_0.1.crtf',
                                            2: 'mask_G333_B3_7m12m_0.05.crtf',
                                            3: 'mask_G333_B3_7m12m_0.01.crtf',
                                            4: 'mask_G333_B3_7m12m_0.002.crtf',
                                                                                        5: 'mask_G333_B3_7m12m_0.0015.crtf'},
                               'scales': [0,3,9,27],
                              },
    'G333.60_B3_7M12M_robust2': {'threshold': '0.07mJy', 'niter': 90000,
                               'scales': [0,3,9],
                               'maskname': 'mask_G333_B3_7m12m_0.0015.crtf',
                              },
    'G333.60_B3_7M12M_robust-2': {'threshold': '0.07mJy', 'niter': 90000,
                                'scales': [0,3,9,27],
                                'maskname': 'mask_G333_B3_7m12m_0.0015.crtf',
                            },
        # B6 12M CLEANEST CONTINUUM #
    'G333.60_B6_12M_robust0': {'threshold': {0: '1.2mJy', 1: '1.2mJy', 2: '0.8mJy', 3: '0.4mJy', 4: '0.2mJy', 5: '0.15 mJy', 'final': '0.15 mJy'},
                               'niter': {0: 3000, 1: 3000, 2: 6000, 3: 12000, 4: 24000, 5: 48000, 'final': 70000},
                               'maskname': {0: 'mask_G333_B6_12m_0.1.crtf',
                                            1: 'mask_G333_B6_12m_0.1.crtf',
                                            2: 'mask_G333_B6_12m_0.03.crtf',
                                            3: 'mask_G333_B6_12m_0.03.crtf',
                                            4: 'mask_G333_B6_12m_0.01.crtf',
                                            5: 'mask_G333_B6_12m_0.01.crtf',
                                                                                        'final': 'mask_G333_B6_12m_final.crtf'},
                               'scales': [0,3,9],
                              },
    'G333.60_B6_12M_robust2': {'threshold': '0.15mJy',
                               'niter': 70000,
                               'maskname': 'mask_G333_B6_12m_final.crtf',
                               'scales': [0,3,9],
                              },
    'G333.60_B6_12M_robust-2': {'threshold': '0.1mJy',
                                'niter': 70000,
                                'maskname': 'mask_G333_B6_12m_final.crtf',
                                'scales': [0,3,9],
                              },
        # B6 7M12M CLEANEST CONTINUUM #
    'G333.60_B6_7M12M_robust0': {'threshold': {0: '1.2mJy', 1: '1.2mJy', 2: '0.8mJy', 3: '0.4mJy', 4: '0.2mJy', 5: '0.15 mJy', 'final': '0.15 mJy'},
                               'niter': {0: 3000, 1: 3000, 2: 6000, 3: 12000, 4: 24000, 5: 48000, 'final': 70000},
                               'maskname': {0: 'mask_G333_B6_7m12m_0.1.crtf',
                                            1: 'mask_G333_B6_7m12m_0.1.crtf',
                                            2: 'mask_G333_B6_7m12m_0.03.crtf',
                                            3: 'mask_G333_B6_7m12m_0.03.crtf',
                                            4: 'mask_G333_B6_7m12m_0.01.crtf',
                                            5: 'mask_G333_B6_7m12m_0.01.crtf',
                                                                                        'final': 'mask_G333_B6_7m12m_final.crtf'},
                               'scales': [0,3,9,27],
                              },
    'G333.60_B6_7M12M_robust2': {'threshold': '0.15mJy',
                               'niter': 70000,
                               'maskname': 'mask_G333_B6_7m12m_final.crtf',
                               'scales': [0,3,9],
                              },
    'G333.60_B6_7M12M_robust-2': {'threshold': '0.1mJy',
                                'niter': 70000,
                                'maskname': 'mask_G333_B6_7m12m_final.crtf',
                                'scales': [0,3,9,27],
                              },
        #####  #####
    'G008.67_B6_12M_robust0': {'maskname': {0: 'G008.67_B6_12M_robust0.crtf',
                                            1: 'G008.67_B6_12M_robust0.crtf',}},
    'G008.67_B3_12M_robust0': {'maskname': {0: 'G008.67_B6_12M_robust0.crtf',
                                            1: 'G008.67_B6_12M_robust0.crtf',}},
    'G012.80_B3_12M_robust0':{'threshold':{0:'10.0mJy', 1:'10mJy', 2:'5mJy', 3:'3mJy', 4:'1mJy', 5:'0.25mJy'},
                              'niter':{0:500, 1:100, 2:1000, 3:3000, 4:5000, 5:7000}},
    'G012.80_B3_7M12M_robust0':{'threshold':{0:'10.0mJy', 1:'10mJy', 2:'3mJy', 3:'3mJy', 4:'1mJy', 5:'0.25mJy'},
        'niter':{0:100, 1:500, 2:1000, 3:1500, 4:3000, 5:5000},
        'scales':{0:[0,3,9,27,100]},
                             },

    'G012.80_B3_12M_robust0':{'threshold':{0:'10.0mJy', 1:'10mJy', 2:'5mJy', 3:'3mJy', 4:'1mJy', 5:'0.25mJy'},
        'niter':{0:500, 1:100, 2:1000, 3:3000, 4:5000, 5:7000},
                             },
    'G012.80_B6_12M_robust0':{'threshold':{0:'3.0mJy', 1:'2mJy', 2:'1.5mJy', 3:'1mJy', 4:'1mJy', 5:'0.25mJy'},
        'niter':{0:0, 1:1500, 2:3000, 3:5000, 4:7000, 5:10000},
                             },
    'G337.92_B3_12M_robust0': {'threshold': '0.25mJy', # RMS ~0.5-0.6 mJy
                               'scales': [0,3,9,27],
                              },
    'W51-IRS2_B6_12M_robust0': {'threshold':
                                {0: '0.3mJy', 1: '0.25mJy', 2: '0.25mJy',
                                 3: '0.25mJy', 4: '0.25mJy', 5: '0.25mJy',
                                 6: '0.2mJy', 7: '0.2mJy', 8: '0.2mJy',
                                },
                                'scales': [0,3,9,27],
                            },
    'W51-IRS2_B3_12M_robust0': {'threshold':
                                {0: '0.3mJy', 1: '0.2mJy', 2: '0.2mJy',
                                 3: '0.1mJy', 4: '0.08mJy'
                                },
                                'scales': [0,3,9,27],
                            },
    # G338.93 B3 12M
    'G338.93_B3_12M_robust0': {'threshold': {0: '0.36mJy', 1:'0.30mJy',
        2:'0.15mJy', 'final':'0.1mJy'},
        'niter': {0: 2000, 1:2000, 2:5000, 'final':200000}},
    'G338.93_B3_12M_robust2': {'threshold': {'final': '0.10mJy'},
        'niter': {'final': 200000}},
    'G338.93_B3_12M_robust-2': {'threshold': {'final': '0.30mJy'},
        'niter': {'final': 200000}},
    # G338.93 B3 12M bsens
    'G338.93_B3_12M_robust0_bsens': {'threshold': {0:'0.34mJy'},
        'niter':{0:2000}
        },
    'G338.93_B3_12M_robust2_bsens': {'threshold': {'final': '0.10mJy'},
        'niter': {'final': 0}},
    'G338.93_B3_12M_robust-2_bsens': {'threshold': {'final': '0.30mJy'},
        'niter': {'final': 0}},
    # G338.93 B3 7M12M
    'G338.93_B3_7M12M_robust0': {'threshold': {0: '0.5mJy', 1:'0.4mJy',
            2:'0.2mJy', 'final':'0.1mJy'},
        'niter': {0: 2000,  1:5000, 2:8000, 'final':200000},
        'scales': [0,3,9,27],
            },
    'G338.93_B3_7M12M_robust2': {'threshold': {'final':'0.1mJy'},
        'niter': {'final':200000}},
    'G338.93_B3_7M12M_robust-2': {'threshold': {'final':'0.1mJy'},
        'niter': {'final':200000}},
    'W51-E_B6_12M_robust0': {'threshold': {0: '0.3mJy', 1: '0.25mJy', 2: '0.25mJy',
                                           3: '0.25mJy', 4: '0.25mJy', 5: '0.25mJy',
                                           6: '0.2mJy',},
                             'scales': [0,3,9,27],
                            },
    'W51-E_B3_12M_robust0': {'threshold': {0: '0.15mJy', 1: '0.15mJy',
                                           2: '0.1mJy', 3: '0.09mJy',
                                           4: '0.09mJy', 5: '0.08mJy',
                                           6: '0.07mJy'},
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
    'W51-E_B3_7M12M_robust0': {'threshold': '1mJy', # RMS ~ ??
                               'scales': [0,3,9,27],
                              },
       #W43-MM2 B6
    'W43-MM2_B6_12M_robust0': {'threshold': {0: '2.0mJy', 1: '2.0mJy', 2: '0.7mJy', 3: '0.5mJy', 4: '0.35mJy', 5: '0.25mJy', 'final': '0.35mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 10000, 3: 12000, 4: 15000, 5: 15000, 'final': 22000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
    'W43-MM2_B6_7M12M_robust0': {'threshold': {0: '2.0mJy', 1: '2.0mJy', 2: '1.0mJy', 3: '0.5mJy', 4: '0.4mJy', 'final': '0.5mJy'},
                               'niter': {0: 1000, 1: 5000, 2: 10000, 3: 10000, 4: 10000, 'final': 25000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27,81]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },

       #W43-MM3 B6
    'W43-MM3_B6_12M_robust0': {'threshold': {0: '1.0mJy', 1: '1.0mJy', 2: '0.25mJy', 3: '0.25mJy', 4: '0.25mJy', 5: '0.25mJy', 'final': '0.23mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 12000, 3: 12000, 4: 12000, 5: 15000, 'final': 18000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
    'W43-MM3_B6_7M12M_robust0': {'threshold': {0: '1.0mJy', 1: '1.0mJy', 2: '0.7mJy', 3: '0.35mJy', 4: '0.35mJy', 'final': '0.5mJy'},
                               'niter': {0: 1000, 1: 5000, 2: 10000, 3: 10000, 4: 10000, 'final': 10000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27,54]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
       #W43-MM1 B3
    'W43-MM1_B3_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.25mJy', 2: '0.15mJy', 3: '0.1mJy', 4: '0.1mJy', 'final': '0.12mJy'},
                               'niter': {0: 1000, 1: 9000, 2: 15000, 3: 15000, 4: 17000, 'final': 25000},

                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27,81]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
    'W43-MM1_B3_7M12M_robust0': {'threshold': {0: '1.0mJy', 1: '1.0mJy', 2: '0.23mJy', 3: '0.15mJy', 4: '0.1mJy', 'final': '0.05mJy'},
                               'niter': {0: 1000, 1: 9000, 2: 13000, 3: 15000, 4: 17000, 'final': 26000},

                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,9,27,81,162]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
       #W43-MM2 B3
    'W43-MM2_B3_12M_robust0': {'threshold': {0: '0.2mJy', 1: '0.5mJy', 2: '0.1mJy', 3: '0.1mJy', 4: '0.1mJy', 'final': '0.12mJy'},
                               'niter': {0: 9000, 1: 10000, 2: 16000, 3: 16000, 4: 18000, 'final': 25000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,9,27,81,162]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
    'W43-MM2_B3_7M12M_robust0': {'threshold': {0: '0.5mJy', 1: '1.0mJy', 2: '0.5mJy', 3: '0.2mJy', 4: '0.08mJy'},
                               'niter': {0: 9000, 1: 10000, 2: 12000, 3: 15000, 4: 20000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                                }
       #W43-MM3 B3
    'W43-MM3_B3_12M_robust0': {'threshold': {0: '1.0mJy', 1: '0.75mJy', 2: '0.15mJy', 3: '0.1mJy', 4: '0.1mJy', 'final': '0.11mJy'},
                               'niter': {0: 1000, 1: 6000, 2: 12000, 3: 15000, 4: 15000, 'final': 24000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,3,9,27,81]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
                              },
    'W43-MM3_B3_7M12M_robust0': {'threshold': {0: '1.0mJy', 1: '1.0mJy', 2: '0.5mJy', 3: '0.2mJy', 4: '0.1mJy', 'final': '0.04mJy'},
                               'niter': {0: 3000, 1: 8000, 2: 15000, 3: 17000, 4: 20000, 'final': 25000},
                               'scales': {0: [0,3,9,27], 1: [0,3,9,27], 2: [0,3,9,27], 3: [0,3,9,27], 4: [0,3,9,27], 'final': [0,9,27,81,162]},
                               'maskname': {'final':''},
                               'usemask': {'final':'pb'},
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
    # G327.29
    # G327.29 B3 12M selfcal
    'G327.29_B3_12M_robust0': {'threshold': {0: '1.5mJy', 1: '0.6mJy', 
        2: '0.5mJy', 'final':'0.4mJy'},
        'niter': {0: 1000, 1:2000, 2:5000, 'final':200000},
        'scales': [0,3,9,27],
        },
    'G327.29_B3_12M_robust-2': {'threshold': {'final': '0.4mJy'},
        'niter': {'final': 200000},
        'scales': [0,3,9,27]
        },
    'G327.29_B3_12M_robust2': {'threshold': {'final': '0.4mJy'},
        'niter': {'final': 200000},
        'scales': [0,3,9,27]
        },
    # G327.29 B3 12M bsens selfcal
    # G327.29 B3 7M12M no selfcal
    #'G327.29_B3_7M12M_robust0': {'threshold': {0: '1.5mJy'},
    #    'niter': {0: 200000},
    #    'maskname':{0:'G327.29_B3_noselfcal_7M12M.crtf'},
    #    'scales': [0,3,9,27]
    #    },
    #'G327.29_B3_7M12M_robust-2': {'threshold': {0: '0.5mJy'},
    #    'niter': {0: 200000},
    #    'maskname':{0:'G327.29_B3_noselfcal_7M12M.crtf'},
    #    'scales': [0,3,9,27]
    #    },
    #'G327.29_B3_7M12M_robust2': {'threshold': {0: '0.5mJy'},
    #    'niter': {0: 100000},
    #    'maskname':{0:'G327.29_B3_noselfcal_7M12M.crtf'},
    #    'scales': [0,3,9,27]
    #    },
    # G327.29 B3 7M12M selfcal
    'G327.29_B3_7M12M_robust0': {'threshold': {0: '2.0mJy', 1:'1.8mJy', 
        'final': '1.5mJy'},
        'niter': {0: 5000, 1:5000, 'final':200000},
        'scales': [0,3,9,27]
        },
    'G327.29_B3_7M12M_robust-2': {'threshold': {'final': '0.5mJy'},
        'niter': {'final': 200000},
        'scales': [0,3,9,27]
        },
    'G327.29_B3_7M12M_robust2': {'threshold': {'final': '0.5mJy'},
        'niter': {'final': 100000},
        'scales': [0,3,9,27]
        },
    # G327.29 B6 12M no selfcal imaging
    #'G327.29_B6_12M_robust0': {'threshold': {0:'0.5mJy'},
    #    'niter': {0:10000},
    #    'maskname':{0:'G327.29_B6_noselfcal_12M.crtf'},
    #    'scales': [0,3,9,27]
    #    },
    #'G327.29_B6_12M_robust2': {'threshold':{0:'1.0mJy'},
    #    'niter': {0: 20000},
    #    'maskname':{0:'G327.29_B6_noselfcal_12M.crtf'}
    #    },
    #'G327.29_B6_12M_robust-2': {'threshold': {0:'1.0mJy'},
    #    'niter': {0: 20000},
    #    'maskname':{0:'G327.29_B6_noselfcal_12M.crtf'}
    #    },
    # G327.29 B6 12M selfcal
    'G327.29_B6_12M_robust0': {'threshold': {0: '2.0mJy', 1:'1.5mJy', 
        2:'1.0mJy', 3:'1.0mJy', 4:'0.8mJy', 5:'0.5mJy', 'final':'0.5mJy'},
        'niter': {0: 1000, 1:1000, 2:5000, 3:8000, 4:10000, 5:10000,
            'final':20000},
        'scales': [0,3,9,27]
        },
    'G327.29_B6_12M_robust2': {'threshold': {'final': '1.0mJy'},
        'niter': {'final': 20000}},
    'G327.29_B6_12M_robust-2': {'threshold': {'final': '1.0mJy'},
        'niter': {'final': 20000}},
    # G327.29 B6 7M12M no selfcal imaging
    #'G327.29_B6_7M12M_robust0': {'threshold': {0:'0.5mJy'},
    #    'niter': {0:200000},
    #    'maskname':{0:'G327.29_B6_noselfcal_7M12M.crtf'},
    #    'scales': [0,3,9,27]
    #    },
    #'G327.29_B6_7M12M_robust2': {'threshold':{0:'1.0mJy'},
    #    'niter': {0: 20000},
    #    'maskname':{0:'G327.29_B6_noselfcal_7M12M.crtf'}
    #    },
    #'G327.29_B6_7M12M_robust-2': {'threshold': {0:'1.0mJy'},
    #    'niter': {0: 20000},
    #    'maskname':{0:'G327.29_B6_noselfcal_7M12M.crtf'}
    #    },
    # G327.29 B6 7M12M selfcal
    'G327.29_B6_7M12M_robust0': {'threshold': {0: '2.0mJy', 1:'1.5mJy', 
            2:'1.0mJy', 3:'0.8mJy', 4:'0.8mJy', 5:'0.5mJy'},
        'niter': {0: 1000, 1:1000, 2:5000, 3:8000, 4:10000, 5:200000},
        'scales': [0,3,9,27]
        },
    'G327.29_B6_7M12M_robust2': {'threshold': {5: '1.0mJy'},
        'niter': {5: 20000}},
    'G327.29_B6_7M12M_robust-2': {'threshold': {5: '1.0mJy'},
        'niter': {5: 20000}},
'G010.62_B3_7M12M_robust0': {'threshold': {0:'7mJy', 1: '3mJy', 2: '1.5 mJy', 3:'0.7mJy', 4:'0.35mJy'},
                                 'niter':{0:700, 1:1300, 2: 2500, 3: 5000, 4: 10000},
                                 'maskname':{0:'G010.62_centralBox_50_30.reg',
                                             1:'G010.62_B3_50mJy.crtf', #
                                             2:'G010.62_B3_15mJy.crtf', #
                                             3:'G010.62_B3_05mJy.crtf', #
                                             4:'G010.62_B3_03mJy.crtf', #
                             }},
'G010.62_B3_12M_robust0': {'threshold': {0:'10mJy', 1: '5mJy', 2: '2.5 mJy', 3:'1.0mJy', 4:'0.5mJy',5:'0.3mJy'},
                                 'niter':{0:700, 1:1300, 2: 2500, 3: 5000, 4: 10000,5:10000},
                                 'maskname':{0:'G010.62_centralBox_50_30.crtf',
                                             1:'G010.62_B3_50mJy.crtf', #
                                             2:'G010.62_B3_15mJy.crtf', #
                                             3:'G010.62_B3_05mJy.crtf', #
                                             4:'G010.62_B3_03mJy.crtf', #
                                             5:'G010.62_B3_01mJy.crtf'
                                         }},
'G010.62_B6_12M_robust0': {'threshold': {0:'10mJy', 1: '5mJy', 2: '2.5 mJy', 3:'1.0mJy', 4:'0.5mJy',5:'0.3mJy'},
                                 'niter':{0:700, 1:1300, 2: 2500, 3: 5000, 4: 10000,5:10000},
                                 'maskname':{0:'G010.62_centralBox_50_30.crtf',
                                             1:'G010.62_B3_50mJy.crtf', # Using Band 3 masks for the moment
                                             2:'G010.62_B3_15mJy.crtf', #
                                             3:'G010.62_B3_05mJy.crtf', #
                                             4:'G010.62_B3_03mJy.crtf', #
                                             5:'G010.62_B3_01mJy.crtf'
                                         }},


# G351.77                                        6.64e-3
  'G351.77_B6_7M_robust0': {'threshold': {0: '12.0mJy', 1: '12mJy', 2: '3mJy', 3: '0.25mJy', 4: '0.25mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 25000},
                               'scales':[0,3],
                               'maskname': {0: 'G351.77_B6_7M12M_iter1.crtf',
                                            1: 'G351.77_B6_7M_iter1.crtf',
                                            2: 'G351.77_B6_7M_iter1.crtf',
                                            3: 'G351.77_B6_7M_iter1.crtf',
                                            4: 'G351.77_B6_7M_iter1.crtf'}
                              },
                                            # rms = 5e-4 Jy/beam
   'G351.77_B6_7M12M_robust0': {'threshold': {0: '10.0mJy', 1: '10.0mJy', 2: '5.0mJy', 3: '1.0mJy', 4: '1.0mJy','final':'1.0mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 25000},
                               'scales':[0,3],
                              'maskname': {0: 'G351.77_B6_7M12M_iter1.crtf',
                                            1: 'G351.77_B6_7M_iter1.crtf',
                                            2: 'G351.77_B6_7M_iter1.crtf',
                                            3: 'G351.77_B6_7M_iter1.crtf',
                                            4: 'G351.77_B6_7M_iter1.crtf',
                                            'final': 'G351.77_B6_7M12M_finaliter.crtf'}
                         },

   'G351.77_B6_7M12M_robust2': {'threshold': {0: '4.0mJy', 1: '0.75mJy', 2: '0.50mJy', 3: '0.25mJy', 4: '0.25mJy','final':'1.0mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 25000},
                               'scales':[0,3],
                               'maskname': {0: 'G351.77_B6_12M_robust2.crtf',
                                            1: 'G351.77_B6_12M_robust2.crtf',
                                            2: 'G351.77_B6_12M_robust2.crtf',
                                            3: 'G351.77_B6_12M_robust2.crtf',
                                            4: 'G351.77_B6_12M_robust2.crtf',
                                            'final': 'G351.77_B6_7M12M_finaliter.crtf'}
                              },
  'G351.77_B6_7M12M_robust-2': {'threshold': {0: '10.0mJy', 1: '5mJy', 2: '5.0mJy', 3: '1.0mJy', 4: '1.0mJy','final':'1.0mJy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'scales':[0,3],
                               'maskname': {0: 'G351.77_B6_7M_iter1.crtf',
                                            1: 'G351.77_B6_7M_iter1.crtf',
                                            2: 'G351.77_B6_7M_iter1.crtf',
                                            3: 'G351.77_B6_7M_iter1.crtf',
                                            4: 'G351.77_B6_7M12M_finaliter.crtf',
                                            'final': 'G351.77_B6_7M12M_finaliter.crtf'}
                              },
                                                #rms:6e-4
   'G351.77_B6_12M_robust0': {'threshold': {0: '12e-4Jy', 1: '12e-4Jy', 2: '12e-4Jy', 3: '12e-4Jy',4: '12e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'maskname': {0: 'G351.77_B6_12M.crtf',
                                            1: 'G351.77_B6_12M.crtf',
                                            2: 'G351.77_B6_12M.crtf',
                                            3: 'G351.77_B6_12M.crtf',
                                            4: 'G351.77_B6_12M.crtf',
                                            'final':'G351.77_B6_12M_final.crtf'}
                              },


                                               #rms: 5e-4
   'G351.77_B6_12M_robust2': {'threshold': {0: '10e-4Jy', 1: '10e-4Jy', 2: '10e-4Jy', 3: '10e-4Jy', 4: '10e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B6_12M.crtf',
                                            1: 'G351.77_B6_12M.crtf',
                                            2: 'G351.77_B6_12M.crtf',
                                            3: 'G351.77_B6_12M.crtf',
                                            4: 'G351.77_B6_12M.crtf',
                                            'final':'G351.77_B6_12M_final.crtf'}
                              },
                                                 # rms: 7.2e-4
   'G351.77_B6_12M_robust-2': {'threshold': {0: '14.4e-4Jy', 1: '14.4e-4Jy', 2: '14.4e-4Jy', 3: '14.4e-4Jy', 4: '14.4e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B6_12M.crtf',
                                            1: 'G351.77_B6_12M.crtf',
                                            2: 'G351.77_B6_12M.crtf',
                                            3: 'G351.77_B6_12M.crtf',
                                            4: 'G351.77_B6_12M.crtf',
                                            'final':'G351.77_B6_12M_final.crtf'}
                              },

  'G351.77_B3_12M_robust-2': {'threshold': {0: '8e-4Jy', 1: '8e-4Jy', 2: '8e-4Jy', 3: '8e-4Jy', 4: '8e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_12M_robust2_bsens.crtf'}
                              },
                                                # rms: 2.7e-4 for bsens # rms : 1.5e-4
#   'G351.77_B3_12M_robust2': {'threshold': {0: '5.4e-4Jy', 1: '5.4e-4Jy', 2: '5.4e-4Jy', 3: '5.4e-4Jy', 4: '5.4e-4Jy'},
   'G351.77_B3_12M_robust2': {'threshold': {0: '3e-4Jy', 1: '3e-4Jy', 2: '3e-4Jy', 3: '3e-4Jy', 4: '3e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_12M_robust2_bsens.crtf'}
                              },
#  'G351.77_B3_12M_robust0': {'threshold': {0: '7e-4Jy', 1: '7e-4Jy', 2: '7e-4Jy', 3: '7e-4Jy', 4: '7e-4Jy'},
  'G351.77_B3_12M_robust0': {'threshold': {0: '3e-4Jy', 1: '3e-4Jy', 2: '3e-4Jy', 3: '3e-4Jy', 4: '3e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'maskname': {0: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_12M_robust2_bsens.crtf'}
                              },
#  'G351.77_B3_7M12M_robust-2': {'threshold': {0: '8e-4Jy', 1: '8e-4Jy', 2: '8e-4Jy', 3: '8e-4Jy', 4: '8e-4Jy'},
#  rms = 1.6 e-4Jy/b
  'G351.77_B3_7M12M_robust-2': {'threshold': {0: '3.2e-4Jy', 1: '3.2e-4Jy', 2: '3.2e-4Jy', 3: '3.2e-4Jy', 4: '3.2e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
                               'scales': [0,3],
                               'maskname': {0: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_7M12M_robust2_bsens.crtf'}
                              },
                                                # rms: 2.7e-4
#   'G351.77_B3_7M12M_robust2': {'threshold': {0: '5.4e-4Jy', 1: '5.4e-4Jy', 2: '5.4e-4Jy', 3: '5.4e-4Jy', 4: '5.4e-4Jy'},
# rms ~ 0.9e-5
   'G351.77_B3_7M12M_robust2': {'threshold': {0: '1.8e-4Jy', 1: '1.8e-4Jy', 2: '1.8e-4Jy', 3: '1.8e-4Jy', 4: '1.8e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4:18000},
                               'scales': [0,3],                        
                               'maskname': {0: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_7M12M_robust2_bsens.crtf'}
                              },
#rms ~1e-4 Jy/b
  'G351.77_B3_7M12M_robust0': {'threshold': {0: '2e-4Jy', 1: '2e-4Jy', 2: '2e-4Jy', 3: '2e-4Jy', 4: '2e-4Jy'},
# no bsens
#  'G351.77_B3_7M12M_robust0': {'threshold': {0: '7e-4Jy', 1: '7e-4Jy', 2: '7e-4Jy', 3: '7e-4Jy', 4: '7e-4Jy'},
                               'niter': {0: 1000, 1: 3000, 2: 9000, 3: 9000, 4:9000},
                               'scales': [0,3],
                               'maskname': {0: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            1: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            2: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            3: 'G351.77_B3_7M12M_robust2_bsens.crtf',
                                            4: 'G351.77_B3_7M12M_robust2_bsens.crtf'}
                              },



# G328.25 B6
#...............
    'G328.25_B6_7M12M_robust0': {'threshold': {0: '5mJy', 1: '2mJy', 2: '1.5mJy', 3: '1.2mJy',4:'1.2mJy'},
                           # rms:                   2.3e-3     1e-3     7e-4         6e-4        6e-4
                                 'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000,4:18000},
                                 'maskname': {0: 'G328_B6_clean_robust0.crtf',
                                              1: 'G328_B6_clean_robust0.crtf',
                                              2: 'G328_B6_clean_robust0.crtf',
                                              3: 'G328_B6_clean_robust0.crtf',
                                              4:'G328_B6_clean_robust0.crtf'}},
                                              
    'G328.25_B6_7M12M_robust2': {'threshold': {0: '8.0mJy', 1: '2mJy', 2: '1mJy', 3: '0.5mJy',4:'1.0mJy'},
                           # rms:                   6e-4                            3.5e-4
                                 'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000,4:18000},
                                 'maskname': {0: 'G328_B6_clean_robust0.crtf',
                                              1: 'G328_B6_clean_robust0.crtf',
                                              2: 'G328_B6_clean_robust0.crtf',
                                              3: 'G328_B6_clean_robust0.crtf',
                                              4:'G328_B6_clean_robust0.crtf'}},
                                              
     'G328.25_B6_7M12M_robust-2': {'threshold': {0: '8.0mJy', 1: '2mJy', 2: '1mJy', 3: '0.5mJy',4:'1.5mJy'},
                           # rms:                   6e-4                            3.5e-4
                                 'niter': {0: 1000, 1: 3000, 2: 9000, 3: 18000,4:18000},
                                 'maskname': {0: 'G328_B6_clean_robust0.crtf',
                                              1: 'G328_B6_clean_robust0.crtf',
                                              2: 'G328_B6_clean_robust0.crtf',
                                              3: 'G328_B6_clean_robust0.crtf',
                                              4: 'G328_B6_clean_robust0.crtf'}},

    'G328.25_B6_12M_robust0': {'threshold': {0: '1e-3Jy', 1: '2mJy', 2: '1mJy', 3: '0.5mJy',4:'0.5mJy',5:'0.5mJy'}, # cleaning may be too deep?
# rms 5e-4
                               'niter': {0: 3000, 1: 3000, 2: 9000, 3: 18000,4:18000,5:18000},
                               'maskname': {0: 'G328_B6_clean_12M_robust0_3sigma.crtf',
                                            1: 'G328_B6_clean_robust0.crtf',
                                            2: 'G328_B6_clean_robust0.crtf',
                                            3: 'G328_B6_clean_robust0.crtf',
                                            4: 'G328_B6_clean_robust0.crtf',
                                            5: 'G328_B6_clean_robust0.crtf',

}},

    'G328.25_B6_12M_robust-2': {'threshold': {0: '16e-4Jy', 1: '2mJy', 2: '1mJy', 3: '0.5mJy',4:'0.5mJy',5:'0.5mJy'},
# rms 8e-4
                               'niter': {0: 3000, 1: 3000, 2: 9000, 3: 18000,4:18000,5:18000},
                               'maskname': {0: 'G328_B6_clean_12M_robust0_3sigma.crtf',
                                            1: 'G328_B6_clean_robust0.crtf',
                                            2: 'G328_B6_clean_robust0.crtf',
                                            3: 'G328_B6_clean_robust0.crtf',
                                            4: 'G328_B6_clean_robust0.crtf',
                                            5: 'G328_B6_clean_robust0.crtf'}},

    'G328.25_B6_12M_robust2': {'threshold': {0: '8e-4Jy', 1: '2mJy', 2: '1mJy', 3: '0.5mJy',4:'0.5mJy',5:'0.5mJy'},
# rms : 4e-4

                               'niter': {0: 3000, 1: 3000, 2: 9000, 3: 18000,4:18000,5:18000},
                               'maskname': {0: 'G328_B6_clean_12M_robust0_3sigma.crtf',
                                            1: 'G328_B6_clean_robust0.crtf',
                                            2: 'G328_B6_clean_robust0.crtf',
                                            3: 'G328_B6_clean_robust0.crtf',
                                            4: 'G328_B6_clean_robust0.crtf',
                                            5: 'G328_B6_clean_robust0.crtf'}},


}




for key in imaging_parameters_nondefault:
    if 'bsens' in key:
        check_key = '_'.join(key.split('_')[:-1])
        assert check_key in imaging_parameters
        imaging_parameters[key] = copy.deepcopy(imaging_parameters[check_key])
    else:
        assert key in imaging_parameters
    imaging_parameters[key].update(imaging_parameters_nondefault[key])


"""
Self-calibration parameters are defined here
"""

default_selfcal_pars = {ii: {'solint': 'inf',
                             'gaintype': 'T',
                             'solnorm': True,
                             # 'combine': 'spw', # consider combining across spw bounds
                             'calmode': 'p'}
                        for ii in range(1,5)}

selfcal_pars = {key: copy.deepcopy(default_selfcal_pars)
                for key in imaging_parameters}

time_interval_progression_of_selfcal = {0: 'inf', 1:'60s', 2: '45s', 3:'30s', 4:'15s',5:'10s'}
for ii in range(1,5):
    selfcal_pars['G010.62_B3_7M12M_robust0'][ii]['solint'] = time_interval_progression_of_selfcal[ii]
    selfcal_pars['G010.62_B3_12M_robust0'][ii]['solint'] = time_interval_progression_of_selfcal[ii]
    selfcal_pars['G010.62_B6_7M12M_robust0'][ii]['solint'] = time_interval_progression_of_selfcal[ii]
    selfcal_pars['G010.62_B6_12M_robust0'][ii]['solint'] = time_interval_progression_of_selfcal[ii]


for ii in range(1,5):
    selfcal_pars['W51-IRS2_B6_12M_robust0'][ii].update({'solint': '60s', # this is effectively 'inf'?
                                                        'gaintype': 'T',
                                                        'calmode': 'p',
                                                        'minsnr': 5,
                                                        'combine': '', # do not combine across scans, only within
                                                       })
    selfcal_pars['W51-IRS2_B6_7M12M_robust0'][ii].update({'solint': 'inf',
                                                          'gaintype': 'T',
                                                          'calmode': 'p',
                                                          'minsnr': 5,
                                                          'combine': '', # do not combine across scans, only within
                                                         })
    selfcal_pars['W51-E_B6_12M_robust0'][ii]['minsnr'] = 5
    selfcal_pars['W51-E_B3_12M_robust0'][ii]['minsnr'] = 5
    selfcal_pars['W51-E_B6_7M12M_robust0'][ii]['minsnr'] = 5
    selfcal_pars['W51-E_B3_7M12M_robust0'][ii]['minsnr'] = 5
    selfcal_pars['W51-E_B6_12M_robust0'][ii]['gaintype'] = 'T'
    selfcal_pars['W51-E_B3_12M_robust0'][ii]['gaintype'] = 'T'
    selfcal_pars['W51-E_B6_7M12M_robust0'][ii]['gaintype'] = 'T'
    selfcal_pars['W51-E_B3_7M12M_robust0'][ii]['gaintype'] = 'T'
for ii in range(5,8):
    selfcal_pars['W51-IRS2_B6_12M_robust0'][ii] = {'solint': '60s', # this is effectively 'inf'?
                                                   'gaintype': 'T',
                                                   'calmode': 'p',
                                                   'minsnr': 5,
                                                   'combine': '', # do not combine across scans, only within
                                                  }
    selfcal_pars['W51-IRS2_B6_7M12M_robust0'][ii] = {'solint': 'inf',
                                                     'gaintype': 'T',
                                                     'calmode': 'ap',
                                                     'minsnr': 5,
                                                     'combine': '', # do not combine across scans, only within
                                                    }
selfcal_pars['W51-IRS2_B6_12M_robust0'][8] = {'solint': 'inf',
                                              'gaintype': 'T',
                                              'calmode': 'ap',
                                              'minsnr': 5,
                                              }


selfcal_pars['W51-E_B6_12M_robust0'][5] = {'solint': 'inf',
                                           'gaintype': 'T',
                                           'calmode': 'ap',
                                           'minsnr': 5,
                                          }
selfcal_pars['W51-E_B6_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'T',
                                           'calmode': 'ap',
                                           'minsnr': 5,
                                          }

selfcal_pars['W51-E_B6_7M12M_robust0'][5] = copy.copy(selfcal_pars['W51-E_B6_7M12M_robust0'][4]) # one extra phase iteration
selfcal_pars['W51-E_B6_7M12M_robust0'][6] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                             'minsnr': 5,
                                            }
selfcal_pars['W51-E_B6_7M12M_robust0'][7] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                             'minsnr': 5,
                                            }

selfcal_pars['W51-E_B3_12M_robust0'][5] = copy.copy(selfcal_pars['W51-E_B3_12M_robust0'][4])
selfcal_pars['W51-E_B3_12M_robust0'][6] = {'solint': 'inf',
                                           'gaintype': 'T',
                                           'calmode': 'ap',
                                           'minsnr': 5,
                                          }
selfcal_pars['W51-E_B3_12M_robust0'][7] = {'solint': 'inf',
                                           'gaintype': 'T',
                                           'calmode': 'ap',
                                            'minsnr': 5,
                                          }
# W43-MM2 B6
   #12M only#
selfcal_pars['W43-MM2_B6_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B6_12M_robust0'][2] = {'solint': '1200',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B6_12M_robust0'][3] = {'solint': '600',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B6_12M_robust0'][4] = {'solint': '300',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B6_12M_robust0'][5] = {'solint': 'int',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
   #7m12m
selfcal_pars['W43-MM2_B6_7M12M_robust0'][1] = {'solint': 'inf',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM2_B6_7M12M_robust0'][2] = {'solint': '500',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM2_B6_7M12M_robust0'][3] = {'solint': 'int',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM2_B6_7M12M_robust0'][4] = {'solint': 'int',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }

# W43-MM3 B6
   #12M only
selfcal_pars['W43-MM3_B6_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B6_12M_robust0'][2] = {'solint': '1200',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B6_12M_robust0'][3] = {'solint': '600',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B6_12M_robust0'][4] = {'solint': '300',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B6_12M_robust0'][5] = {'solint': 'int',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
   #7m12m
selfcal_pars['W43-MM3_B6_7M12M_robust0'][1] = {'solint': 'inf',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM3_B6_7M12M_robust0'][2] = {'solint': '500',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM3_B6_7M12M_robust0'][3] = {'solint': 'int',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }
selfcal_pars['W43-MM3_B6_7M12M_robust0'][4] = {'solint': 'int',
                                               'gaintype': 'G',
                                               'calmode': 'p',
                                              }

# W43-MM1 B3
   #12M only
selfcal_pars['W43-MM1_B3_12M_robust0'][1] = {'solint': '300',
                                             'gaintype': 'G',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM1_B3_12M_robust0'][2] = {'solint': '300',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM1_B3_12M_robust0'][3] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM1_B3_12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
# W43-MM2 B3
   #12M only
selfcal_pars['W43-MM2_B3_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_12M_robust0'][2] = {'solint': '300',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_12M_robust0'][3] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
   #7m12m 
selfcal_pars['W43-MM2_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_7M12M_robust0'][2] = {'solint': '300',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_7M12M_robust0'][3] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM2_B3_7M12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }

# W43-MM3 B3
   #12M only
selfcal_pars['W43-MM3_B3_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_12M_robust0'][2] = {'solint': '600',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_12M_robust0'][3] = {'solint': '200',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
   #7m12m 
selfcal_pars['W43-MM3_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_7M12M_robust0'][2] = {'solint': '300',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_7M12M_robust0'][3] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['W43-MM3_B3_7M12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }

##### G333.60 ######
# B3 12M CLEANEST CONTINUUM #
selfcal_pars['G333.60_B3_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_12M_robust0'][2] = {'solint': '15s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_12M_robust0'][3] = {'solint': '5s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_12M_robust0'][5] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                             'solnorm': True,
                                            }
# B3 7M12M CLEANEST CONTINUUM #
selfcal_pars['G333.60_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_7M12M_robust0'][2] = {'solint': '15s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_7M12M_robust0'][3] = {'solint': '5s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_7M12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                            }
selfcal_pars['G333.60_B3_7M12M_robust0'][5] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                             'solnorm': True,
                                            }
# B6 12M CLEANEST CONTINUUM #
selfcal_pars['G333.60_B6_12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_12M_robust0'][2] = {'solint': '15s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_12M_robust0'][3] = {'solint': '5s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_12M_robust0'][5] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                                                                         'combine': 'spw',
                                             'solnorm': True,
                                            }
# B6 7M12M CLEANEST CONTINUUM #
selfcal_pars['G333.60_B6_7M12M_robust0'][1] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_7M12M_robust0'][2] = {'solint': '15s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_7M12M_robust0'][3] = {'solint': '5s',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_7M12M_robust0'][4] = {'solint': 'int',
                                             'gaintype': 'T',
                                             'calmode': 'p',
                                                                                         'combine': 'spw',
                                            }
selfcal_pars['G333.60_B6_7M12M_robust0'][5] = {'solint': 'inf',
                                             'gaintype': 'T',
                                             'calmode': 'ap',
                                                                                         'combine': 'spw',
                                             'solnorm': True,
                                            }

#####  ######

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
selfcal_pars['G338.93_B3_12M_robust0'][1] = {'solint': 'inf',
                                            'gaintype': 'T',
                                            'calmode': 'p',
                                            'solnorm': True,
                                            'combine':'scan'
                                          }
selfcal_pars['G338.93_B3_12M_robust0'][2] = {'solint': '60s',
                                            'gaintype': 'T',
                                            'calmode': 'p',
                                            'solnorm': True,
                                            'combine': 'scan'
                                            }
del selfcal_pars['G338.93_B3_12M_robust0'][3]
del selfcal_pars['G338.93_B3_12M_robust0'][4]
selfcal_pars['G338.93_B3_12M_robust0_bsens'][1] = {'solint': 'inf',
                                            'gaintype': 'T',
                                            'calmode': 'p',
                                            'solnorm': True,
                                            'combine':'scan'
                                          }
del selfcal_pars['G338.93_B3_12M_robust0_bsens'][2]
del selfcal_pars['G338.93_B3_12M_robust0_bsens'][3]
del selfcal_pars['G338.93_B3_12M_robust0_bsens'][4]
selfcal_pars['G338.93_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                            'gaintype': 'T',
                                            'calmode': 'p',
                                            'solnorm': True
                                          }
selfcal_pars['G338.93_B3_7M12M_robust0'][2] = {'solint': '60s',
                                            'gaintype': 'T',
                                            'calmode': 'p',
                                            'solnorm': True,
                                            'combine':'scan'
                                            }
del selfcal_pars['G338.93_B3_7M12M_robust0'][3]
del selfcal_pars['G338.93_B3_7M12M_robust0'][4]

# G327.29
# B3 12M
selfcal_pars['G327.29_B3_12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B3_12M_robust0'][2] = {'solint': '60s',
                                           'gaintype': 'T',
                                           'calmode': 'p',
                                           'solnorm': True,
                                           }
del selfcal_pars['G327.29_B3_12M_robust0'][3]
del selfcal_pars['G327.29_B3_12M_robust0'][4]
# B3 7M12M
selfcal_pars['G327.29_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'T',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
del selfcal_pars['G327.29_B3_7M12M_robust0'][2]
del selfcal_pars['G327.29_B3_7M12M_robust0'][3]
del selfcal_pars['G327.29_B3_7M12M_robust0'][4]
# B6 12M
selfcal_pars['G327.29_B6_12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B6_12M_robust0'][2] = {'solint': '60s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B6_12M_robust0'][3] = {'solint': '20s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B6_12M_robust0'][4] = {'solint': '10s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B6_12M_robust0'][5] = {'solint': '5s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
# B6 7M12M
selfcal_pars['G327.29_B6_7M12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True}
selfcal_pars['G327.29_B6_7M12M_robust0'][2] = {'solint': '60s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          } 
selfcal_pars['G327.29_B6_7M12M_robust0'][3] = {'solint': '20s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          } 
selfcal_pars['G327.29_B6_7M12M_robust0'][4] = {'solint': '10s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }
selfcal_pars['G327.29_B6_7M12M_robust0'][5] = {'solint': '5s',
                                           'gaintype': 'G',
                                           'calmode': 'p',
                                           'solnorm': True
                                          }


selfcal_pars['G012.80_B3_12M_robust0'][1] = {'solint': 'inf',
                                          'gaintype':'T',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }

selfcal_pars['G012.80_B3_12M_robust0'][2] = {'solint': '1200s',
                                          'gaintype':'T',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }

selfcal_pars['G012.80_B3_12M_robust0'][3] = {'solint': '300s',
                                          'gaintype':'T',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }


selfcal_pars['G012.80_B3_12M_robust0'][4] = {'solint': '300s',
                                          'gaintype':'T',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }


selfcal_pars['G012.80_B3_12M_robust0'][5] = {'solint': 'inf',
                                          'gaintype':'T',
                                          'calmode':'a',
                                          'minsnr':5,
                                          }

# G351.77
selfcal_pars['G351.77_B3_12M_robust0'][1]={'solint':'inf','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_12M_robust0'][2]={'solint':'90s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_12M_robust0'][3]={'solint':'60s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_12M_robust0'][4]={'solint':'30s','gaintype':'T','minsnr':2,'calmode':'p'}

selfcal_pars['G351.77_B3_7M12M_robust0'][1]={'solint':'inf','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_7M12M_robust0'][2]={'solint':'90s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_7M12M_robust0'][3]={'solint':'60s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B3_7M12M_robust0'][4]={'solint':'30s','gaintype':'T','minsnr':2,'calmode':'p'}


selfcal_pars['G351.77_B6_12M_robust0'][1]={'solint':'inf','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B6_12M_robust0'][2]={'solint':'150s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B6_12M_robust0'][3]={'solint':'60s','gaintype':'T','minsnr':2,'calmode':'p'}
selfcal_pars['G351.77_B6_12M_robust0'][4]={'solint':'30s','gaintype':'T','minsnr':2,'calmode':'p'}

selfcal_pars['G351.77_B6_7M_robust0'][1]={'solint':'inf','gaintype':'T','minsnr':3,'calmode':'p'}
selfcal_pars['G351.77_B6_7M_robust0'][2]={'solint':'inf','gaintype':'T','minsnr':3,'calmode':'p'}#int
selfcal_pars['G351.77_B6_7M_robust0'][3]={'solint':'100s','gaintype':'T','minsnr':3,'calmode':'p'}
selfcal_pars['G351.77_B6_7M_robust0'][4]={'solint':'60s','gaintype':'T','minsnr':3,'calmode':'p'}


selfcal_pars['G351.77_B6_7M12M_robust0'][1]={'solint':'inf','gaintype':'T','minsnr':3,'calmode':'p'}
selfcal_pars['G351.77_B6_7M12M_robust0'][2]={'solint':'300','gaintype':'T','minsnr':3,'calmode':'p'}#int
selfcal_pars['G351.77_B6_7M12M_robust0'][3]={'solint':'150s','gaintype':'T','minsnr':3,'calmode':'p'}
selfcal_pars['G351.77_B6_7M12M_robust0'][4]={'solint':'60s','gaintype':'T','minsnr':3,'calmode':'p'}

# This works by selecting the central field for self-calibration
selfcal_pars['G328.25_B3_7M12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'T','combine':'scan','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3#,'field':'9'
                                          }

selfcal_pars['G328.25_B3_7M12M_robust0'][2] = {'solint': 'inf',
                                           'gaintype': 'T','combine':'scan','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3
                                          }



selfcal_pars['G328.25_B3_12M_robust0'][1] = {'solint': 'inf',
                                           'gaintype': 'T','combine':'scan','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3#,'field':'9'
                                          }

selfcal_pars['G328.25_B3_12M_robust0'][2] = {'solint': 'int',
                                           'gaintype': 'T','combine':'scan','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3#,'field':'9'
                                          }


selfcal_pars['G328.25_B3_12M_robust0'][3] = {'solint': '60s',
                                           'gaintype': 'T','combine':'spw','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3#,'field':'9',
                                          }

selfcal_pars['G328.25_B3_12M_robust0'][4] = {'solint': '30s',
                                           'gaintype': 'T','combine':'spw','refant':'DV01',
                                           'calmode': 'p','minsnr':2,'minblperant':3#,'field':'9',
                                          }



# G328.25 B6
selfcal_pars['G328.25_B6_12M_robust0'][1] = {'gaintype': 'T','solint': 'inf','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_12M_robust0'][2] = {'gaintype': 'T','solint': '300','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_12M_robust0'][3] = {'gaintype': 'T','solint': '90s','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_12M_robust0'][4] = {'gaintype': 'T','solint': '60s','combine':'scan','calmode': 'p'}
#selfcal_pars['G328.25_B6_12M_robust0'][5] = {'gaintype': 'T','solint': '30s','combine':'scan','calmode': 'p'}

selfcal_pars['G328.25_B6_7M12M_robust0'][1] = {'gaintype': 'T','solint': 'inf','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_7M12M_robust0'][2] = {'gaintype': 'T','solint': '300','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_7M12M_robust0'][3] = {'gaintype': 'T','solint': '90s','combine':'scan','calmode': 'p'}
selfcal_pars['G328.25_B6_7M12M_robust0'][4] = {'gaintype': 'T','solint': '60s','combine':'scan','calmode': 'p'}
#selfcal_pars['G328.25_B6_12M_robust0'][5] = {'gaintype': 'T','solint': '30s','combine':'scan','calmode': 'p'}


selfcal_pars['G012.80_B6_12M_robust0'][1] = {'solint': 'inf',
                                          'gaintype':'G',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }
selfcal_pars['G012.80_B6_12M_robust0'][2] = {'solint': 'inf',
                                          'gaintype':'G',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }
selfcal_pars['G012.80_B6_12M_robust0'][3] = {'solint': '1200s',
                                          'gaintype':'G',
                                          'calmode':'p',
                                          'minsnr':5,
                                          }
selfcal_pars['G012.80_B6_12M_robust0'][4] = {'solint': '600s',
                                          'gaintype':'G',
                                          'calmode':'p',
                                          'minsnr':4,
                                          }
selfcal_pars['G012.80_B6_12M_robust0'][5] = {'solint': 'inf',
                                          'gaintype':'G',
                                          'calmode':'a',
                                          'minsnr':5,
                                          }



line_imaging_parameters = {"{0}_{1}_{2}_robust{3}{4}".format(field, band, array, robust, contsub):
                           {
                            'niter': 100000, # start with a light cleaning...
                            'robust': robust,
                            'weighting': 'briggs',
                            'scales': [0,3,9,27,81],
                            'gridder': 'mosaic',
                            'specmode': 'cube',
                            'deconvolver': 'multiscale',
                            'outframe': 'LSRK',
                            'veltype': 'radio',
                            'sidelobethreshold': 2.0,
                            'noisethreshold': 5.0,
                            'usemask': 'auto-multithresh',
                            'threshold': '5sigma',
                            'interactive': False,
                            'pblimit': 0.2,
                            'nterms': 1
                           }
                           for field in allfields
                           for band in ('B3','B6')
                           for array in ('12M', '7M12M', '7M')
                           #for robust in (0,)
                                                   for robust in (-2,0,2)
                           for contsub in ("","_contsub")
                          }

line_imaging_parameters['G337.92_B3_12M_robust0']['usemask'] = 'auto-multithresh'
line_imaging_parameters['G337.92_B3_12M_robust0_contsub']['usemask'] = 'auto-multithresh'

default_lines = {'n2hp': '93.173700GHz',
                 'sio': '217.104984GHz',
                 'h2co303': '218.222195GHz',
                 '12co': '230.538GHz',
                 'h30a': '231.900928GHz',
                 'h41a': '92.034434GHz',
                 'c18o': '219.560358GHz',
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
line_parameters['G010.62']['h41a']['cubewidth'] = '120km/s'
line_parameters['G338.93']['sio']['cubewidth'] = '120km/s'

# line_parameters for H41a
line_parameters['G008.67']['h41a']['vlsr'] = '44km/s'
line_parameters['G008.67']['h41a']['cubewidth'] = '100km/s'
line_parameters['G010.62']['h41a']['vlsr'] = '0km/s'
line_parameters['G010.62']['h41a']['cubewidth'] = '100km/s'
line_parameters['G012.80']['h41a']['vlsr'] = '32km/s'
line_parameters['G012.80']['h41a']['cubewidth'] = '100km/s'
line_parameters['G327.29']['h41a']['vlsr'] = '-42km/s'
line_parameters['G327.29']['h41a']['cubewidth'] = '60km/s'
line_parameters['G328.25']['h41a']['vlsr'] = '-37km/s'
line_parameters['G328.25']['h41a']['cubewidth'] = '60km/s'

line_parameters['G333.60']['h41a']['vlsr'] = '-44km/s'
line_parameters['G333.60']['h41a']['cubewidth'] = '100km/s'
line_parameters['G333.60']['h41a']['width'] = '2km/s'

line_imaging_parameters['G333.60_B3_12M_robust0']['niter'] = 500000
line_imaging_parameters['G333.60_B3_12M_robust0']['scales'] = [0,3,9,27]
line_imaging_parameters['G333.60_B3_12M_robust0_contsub']['niter'] = 500000
line_imaging_parameters['G333.60_B3_12M_robust0_contsub']['scales'] = [0,3,9,27]


line_parameters['G337.92']['h41a']['vlsr'] = '-36km/s'
line_parameters['G337.92']['h41a']['cubewidth'] = '80km/s'
line_parameters['G338.93']['h41a']['vlsr'] = '-63km/s'
line_parameters['G338.93']['h41a']['cubewidth'] = '60km/s'
line_parameters['G353.41']['h41a']['vlsr'] = '-17km/s'
line_parameters['G353.41']['h41a']['cubewidth'] = '80km/s'
line_parameters['W43-MM1']['h41a']['vlsr'] = '100km/s'
line_parameters['W43-MM1']['h41a']['cubewidth'] = '80km/s'
line_parameters['W43-MM2']['h41a']['vlsr'] = '103km/s'
line_parameters['W43-MM2']['h41a']['cubewidth'] = '60km/s'
line_parameters['W43-MM3']['h41a']['vlsr'] = '90km/s'
line_parameters['W43-MM3']['h41a']['cubewidth'] = '100km/s'
line_parameters['W51-E']['h41a']['vlsr'] = '59km/s'
line_parameters['W51-E']['h41a']['cubewidth'] = '100km/s'
line_parameters['W51-IRS2']['h41a']['vlsr'] = '56km/s'
line_parameters['W51-IRS2']['h41a']['cubewidth'] = '100km/s'






for field in allfields:
    line_parameters[field]['12co']['cubewidth'] = '150km/s'

# use the continuum image as the startmodel for the non-contsub'd data
# (nice idea, didn't work)
#line_imaging_parameters['W51-E_B6_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust0_selfcal7.model.tt0'
#line_imaging_parameters['W51-E_B3_12M_robust0']['startmodel'] = 'imaging_results/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7.model.tt0'
