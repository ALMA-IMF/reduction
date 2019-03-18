imaging_parameters = {
    'W51-E_B6_12M_robust0': {'threshold': '1mJy', # RMS ~0.5-0.6 mJy
                             'pblimit': 0.1,
                             'niter': 10000,
                             'robust': 0,
                             'weighting': 'briggs',
                             'scales': [0,3,9,27],
                             'gridder': 'mosaic',
                             'specmode': 'mfs',
                             'deconvolver': 'mtmfs',
                             'nterms': 2,
                            },
    'W51-E_B3_12M_robust0': {'threshold': '1mJy', # RMS ~0.25-0.4 mJy
                             'pblimit': 0.1,
                             'niter': 10000,
                             'robust': 0,
                             'weighting': 'briggs',
                             'scales': [0,3,9],
                             'gridder': 'mosaic',
                             'specmode': 'mfs',
                             'deconvolver': 'mtmfs',
                             'nterms': 2,
                            },
    'W51-E_B6_7M12M_robust0': {'threshold': '3mJy', # RMS ~ ??
                               'pblimit': 0.1,
                               'niter': 10000,
                               'robust': 0,
                               'weighting': 'briggs',
                               'scales': [0,3,9,27],
                               'gridder': 'mosaic',
                               'specmode': 'mfs',
                               'deconvolver': 'mtmfs',
                               'nterms': 2,
                              },
    'W51-E_B3_7M12M_robust0': {'threshold': '2mJy', # RMS ~ ??
                               'pblimit': 0.1,
                               'niter': 10000,
                               'robust': 0,
                               'weighting': 'briggs',
                               'scales': [0,3,9,27],
                               'gridder': 'mosaic',
                               'specmode': 'mfs',
                               'deconvolver': 'mtmfs',
                               'nterms': 2,
                              },
}

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
