imaging_parameter = {
    'W51-E_B6_12M_robust0': {'threshold': '2mJy', # RMS ~ 0.5-0.6 mJy
                             'pblimit': 0.1,
                             'niter': 10000,
                             'robust': 0,
                             'weighting': 'briggs',
                             'scales': [0,3,9,27,81],
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
                            }
}
