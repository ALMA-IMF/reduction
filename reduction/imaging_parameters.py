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

CONTRIBUTOR NOTE:
    This file is to be formatted with python's "black" formatter:

        black -t py27 -l 120 imaging_parameters.py
"""
import copy

allfields = "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split()

# set up global defaults
imaging_parameters = {
    "{0}_{1}_{2}_robust{3}".format(field, band, array, robust): {
        "threshold": "1mJy",  # RMS ~0.5-0.6 mJy
        "pblimit": 0.1,
        "pbmask": 0.1,
        "niter": 100000,
        "robust": robust,
        "weighting": "briggs",
        "scales": [0, 3, 9],
        "gridder": "mosaic",
        "specmode": "mfs",
        "deconvolver": "mtmfs",
        "usemask": "user",
        "nterms": 2,
    }
    for field in allfields
    for band in ("B3", "B6")
    for array in ("12M", "7M12M", "7M")
    for robust in (-2, 0, 2, -1, 1, -0.5, 0.5)
}

# added for 7M only data: higher threshold
for key in imaging_parameters:
    if "_7M_" in key:
        imaging_parameters[key]["threshold"] = "5mJy"
    if "7M" in key:
        imaging_parameters[key]["scales"] = [0, 3, 9, 27]


imaging_parameters_nondefault = {
    "G008.67_B6_12M_robust0": {
        "threshold": {0: "6.5mJy", 1: "5.5mJy", 2: "4.5mJy", 3: "3.5mJy", 4: "2.9mJy", 5: "0.75mJy"},
        "niter": {0: 1500, 1: 1500, 2: 3000, 3: 5000, 4: 50000, 5: 50000},
        "maskname": {
            0: "mask_G008_B6_0.crtf",
            1: "mask_G008_B6_0.crtf",
            2: "mask_G008_B6_1.crtf",
            3: "mask_G008_B6_4.crtf",
            4: "mask_G008_B6_4.crtf",
            "final": "mask_G008_B6_4_final.crtf",
        },
    },
    "G008.67_B6_12M_robust0_bsens": {
        "threshold": {0: "7.5mJy", 1: "6.5mJy", 2: "5.5mJy", 3: "4.5mJy", 4: "3.25mJy", 5: "0.5mJy"},
        "niter": {0: 1500, 1: 1500, 2: 3000, 3: 5000, 4: 50000, 5: 50000},
        "maskname": {
            0: "mask_G008_B6_0.crtf",
            1: "mask_G008_B6_0.crtf",
            2: "mask_G008_B6_1.crtf",
            3: "mask_G008_B6_1.crtf",
            4: "mask_G008_B6_4.crtf",
            "final": "mask_G008_B6_4_final.crtf",
        },
    },
    "G008.67_B6_7M12M_robust0": {
        "threshold": {0: "6.0mJy", 1: "5.0mJy", 2: "4.0mJy", 3: "3.5mJy", 4: "2.9mJy", 5: "0.75mJy"},
        "niter": {0: 1500, 1: 1500, 2: 3000, 3: 5000, 4: 50000, 5: 50000},
        "maskname": {
            0: "mask_G008_B6_0.crtf",
            1: "mask_G008_B6_0.crtf",
            2: "mask_G008_B6_1.crtf",
            3: "mask_G008_B6_4.crtf",
            4: "mask_G008_B6_4_final.crtf",
            "final": "mask_G008_B6_4_final.crtf",
        },
    },
    "G008.67_B3_12M_robust0": {
        "threshold": {0: "2.5mJy", 1: "2.0mJy", 2: "1.5mJy", 3: "1.0mJy", 4: "0.7mJy", 5: "0.3mJy"},
        "niter": {0: 700, 1: 700, 2: 2000, 3: 5000, 4: 50000, 5: 50000},
        "maskname": {
            0: "mask_G008_B3_1.crtf",
            1: "mask_G008_B3_2.crtf",
            2: "mask_G008_B3_3.crtf",
            3: "mask_G008_B3_3.crtf",
            4: "mask_G008_B3_3.crtf",
            "final": "mask_G008_B3_4.crtf",
        },
    },
    "G008.67_B3_7M12M_robust0": {
        "threshold": {0: "5.0mJy", 1: "4.5mJy", 2: "4.0mJy", 3: "4.5mJy", 4: "2.5mJy", 5: "0.4mJy"},
        "niter": {0: 1000, 1: 1000, 2: 2000, 3: 5000, 4: 25000, 5: 50000},
        "maskname": {
            0: "mask_G008_B3_7M12M_0.crtf",
            1: "mask_G008_B3_7M12M_1.crtf",
            2: "mask_G008_B3_7M12M_2.crtf",
            3: "mask_G008_B3_7M12M_3.crtf",
            4: "mask_G008_B3_7M12M_4.crtf",
            "final": "mask_G008_B3_7M12M_4.crtf",
        },
    },
    "G008.67_B3_12M_robust0_bsens": {
        "threshold": {0: "3.0mJy", 1: "2.5mJy", 2: "1.5mJy", 3: "0.8mJy", 4: "0.3mJy", 5: "0.16mJy"},
        "niter": {0: 1200, 1: 1500, 2: 3000, 3: 5000, 4: 70000, 5: 90000},
        "maskname": {
            0: "mask_G008_B3_1.crtf",
            1: "mask_G008_B3_2.crtf",
            2: "mask_G008_B3_2.crtf",
            3: "mask_G008_B3_2_bsens.crtf",
            4: "mask_G008_B3_2_bsens.crtf",
            5: "mask_G008_B3_final_bsens.crtf",
            "final": "mask_G008_B3_final_bsens.crtf",
        },
    },
    "G010.62_B3_7M12M_robust0": {
        "threshold": {0: "10mJy", 1: "5mJy", 2: "2.5 mJy", 3: "0.8mJy", 4: "0.5mJy", 5: "0.32mJy"},
        "niter": {0: 700, 1: 1300, 2: 2500, 3: 5000, 4: 15000, 5: 15000},
        "maskname": {
            0: "G010.62_55arcsecCircle.crtf",
            1: "G010_ds9_15mJy.crtf",
            2: "G010_ds9_15mJy.crtf",
            3: "G010_ds9_1mJy.crtf",
            4: "G010_ds9_0.5mJy.crtf",
            5: "G010_ds9_0.3mJy.crtf",
        },
    },
    "G333.60_B3_12M_robust0": {
        "threshold": {0: "0.8mJy", 1: "0.8mJy", 2: "0.4mJy", 3: "0.2mJy", 4: "0.1mJy", 5: "0.07mJy"},
        "niter": {0: 3000, 1: 3000, 2: 10000, 3: 30000, 4: 90000, 5: 90000},
        "maskname": {
            0: "mask_G333_B3_12m_0.1.crtf",
            1: "mask_G333_B3_12m_0.1.crtf",
            2: "mask_G333_B3_12m_0.03.crtf",
            3: "mask_G333_B3_12m_0.01.crtf",
            4: "mask_G333_B3_12m_0.003.crtf",
            5: "mask_G333_B3_12m_0.0015.crtf",
        },
        "scales": [0, 3, 9, 27],
    },
    "G333.60_B3_12M_robust2": {
        "threshold": "0.07mJy",
        "niter": 90000,
        "scales": [0, 3, 9],
        "maskname": "mask_G333_B3_12m_0.0015.crtf",
    },
    "G333.60_B3_12M_robust-2": {
        "threshold": "0.07mJy",
        "niter": 90000,
        "scales": [0, 3, 9, 27],
        "maskname": "mask_G333_B3_12m_0.0015.crtf",
    },
    "G333.60_B3_7M12M_robust0": {
        "threshold": {0: "0.8mJy", 1: "0.8mJy", 2: "0.4mJy", 3: "0.2mJy", 4: "0.1mJy", 5: "0.07mJy"},
        "niter": {0: 3000, 1: 3000, 2: 10000, 3: 30000, 4: 90000, 5: 90000},
        "maskname": {
            0: "mask_G333_B3_7m12m_0.1.crtf",
            1: "mask_G333_B3_7m12m_0.1.crtf",
            2: "mask_G333_B3_7m12m_0.05.crtf",
            3: "mask_G333_B3_7m12m_0.01.crtf",
            4: "mask_G333_B3_7m12m_0.002.crtf",
            5: "mask_G333_B3_7m12m_0.0015.crtf",
        },
        "scales": [0, 3, 9, 27],
    },
    "G333.60_B3_7M12M_robust2": {
        "threshold": "0.07mJy",
        "niter": 90000,
        "scales": [0, 3, 9],
        "maskname": "mask_G333_B3_7m12m_0.0015.crtf",
    },
    "G333.60_B3_7M12M_robust-2": {
        "threshold": "0.07mJy",
        "niter": 90000,
        "scales": [0, 3, 9, 27],
        "maskname": "mask_G333_B3_7m12m_0.0015.crtf",
    },
    "G333.60_B6_12M_robust0": {
        "threshold": {
            0: "1.2mJy",
            1: "1.2mJy",
            2: "0.8mJy",
            3: "0.4mJy",
            4: "0.2mJy",
            5: "0.15 mJy",
            "final": "0.15 mJy",
        },
        "niter": {0: 3000, 1: 3000, 2: 6000, 3: 12000, 4: 24000, 5: 48000, "final": 70000},
        "maskname": {
            0: "mask_G333_B6_12m_0.1.crtf",
            1: "mask_G333_B6_12m_0.1.crtf",
            2: "mask_G333_B6_12m_0.03.crtf",
            3: "mask_G333_B6_12m_0.03.crtf",
            4: "mask_G333_B6_12m_0.01.crtf",
            5: "mask_G333_B6_12m_0.01.crtf",
            "final": "mask_G333_B6_12m_final.crtf",
        },
        "scales": [0, 3, 9],
    },
    "G333.60_B6_12M_robust2": {
        "threshold": "0.15mJy",
        "niter": 70000,
        "maskname": "mask_G333_B6_12m_final.crtf",
        "scales": [0, 3, 9],
    },
    "G333.60_B6_12M_robust-2": {
        "threshold": "0.1mJy",
        "niter": 70000,
        "maskname": "mask_G333_B6_12m_final.crtf",
        "scales": [0, 3, 9],
    },
    "G333.60_B6_7M12M_robust0": {
        "threshold": {
            0: "1.2mJy",
            1: "1.2mJy",
            2: "0.8mJy",
            3: "0.4mJy",
            4: "0.2mJy",
            5: "0.15 mJy",
            "final": "0.15 mJy",
        },
        "niter": {0: 3000, 1: 3000, 2: 6000, 3: 12000, 4: 24000, 5: 48000, "final": 70000},
        "maskname": {
            0: "mask_G333_B6_7m12m_0.1.crtf",
            1: "mask_G333_B6_7m12m_0.1.crtf",
            2: "mask_G333_B6_7m12m_0.03.crtf",
            3: "mask_G333_B6_7m12m_0.03.crtf",
            4: "mask_G333_B6_7m12m_0.01.crtf",
            5: "mask_G333_B6_7m12m_0.01.crtf",
            "final": "mask_G333_B6_7m12m_final.crtf",
        },
        "scales": [0, 3, 9, 27],
    },
    "G333.60_B6_7M12M_robust2": {
        "threshold": "0.15mJy",
        "niter": 70000,
        "maskname": "mask_G333_B6_7m12m_final.crtf",
        "scales": [0, 3, 9],
    },
    "G333.60_B6_7M12M_robust-2": {
        "threshold": "0.1mJy",
        "niter": 70000,
        "maskname": "mask_G333_B6_7m12m_final.crtf",
        "scales": [0, 3, 9, 27],
    },
    "G012.80_B3_7M12M_robust0": {
        "threshold": {0: "10.0mJy", 1: "10mJy", 2: "3mJy", 3: "3mJy", 4: "1mJy", 5: "0.25mJy"},
        "niter": {0: 100, 1: 500, 2: 1000, 3: 1500, 4: 3000, 5: 5000},
        "scales": {0: [0, 3, 9, 27, 100]},
    },
    "G012.80_B3_12M_robust0": {
        "threshold": {0: "10.0mJy", 1: "10mJy", 2: "5mJy", 3: "3mJy", 4: "1mJy", 5: "0.25mJy"},
        "niter": {0: 500, 1: 100, 2: 1000, 3: 3000, 4: 5000, 5: 7000},
    },
    "G012.80_B6_12M_robust0": {
        "threshold": {0: "3.0mJy", 1: "2mJy", 2: "1.5mJy", 3: "1mJy", 4: "1mJy", 5: "0.25mJy"},
        "niter": {0: 500, 1: 1500, 2: 3000, 3: 5000, 4: 7000, 5: 10000},
    },
    "G337.92_B3_12M_robust0": {
        "threshold": {0: "10e-4Jy", 1: "10e-4Jy", 2: "5e-4Jy", 3: "4e-4Jy", 4: "2.5e-4Jy", "final": "0.1mJy"},
        "scales": [0, 3, 9],
        "niter": {0: 5000, 1: 8000, 2: 10000, 3: 15000, 4: 30000, "final": 50000},  # rms ~ 1.25e-4 Jy/b.
        "maskname": {
            0: "G337.92_B3_12M_robust0.crtf",
            1: "G337.92_B3_12M_robust0.crtf",
            2: "G337.92_B3_12M_robust0.crtf",
            3: "G337.92_B3_12M_robust0.crtf",
            4: "G337.92_B3_12M_robust0.crtf",
        },
    },
    "G337.92_B3_12M_robust-2": {
        "threshold": {4: "5e-4Jy"},
        "scales": [0, 3, 9, 27],  # rms ~ 2.45e-4 Jy/b.
        "niter": {4: 30000},
        "maskname": {4: "G337.92_B3_12M_robust-2.crtf"},
    },
    "G337.92_B3_12M_robust2": {
        "threshold": {4: "1.5e-4Jy"},  # rms ~ 7.5e-5 Jy/b
        "scales": [0, 3, 9, 27],
        "niter": {4: 30000},
        "maskname": {4: "G337.92_B3_12M_full.crtf"},
    },
    "G337.92_B6_12M_robust0": {
        "threshold": {0: "10e-4Jy", 1: "10e-4Jy", 2: "5e-4Jy", 3: "5e-4Jy", 4: "5e-4Jy"},
        "scales": [0, 3, 9, 27],
        "niter": {0: 5000, 1: 8000, 2: 10000, 3: 15000, 4: 30000},
        "maskname": {
            0: "G337.92_B6_12M_final.crtf",
            1: "G337.92_B6_12M_final.crtf",
            2: "G337.92_B6_12M_final.crtf",
            3: "G337.92_B6_12M_final.crtf",
            4: "G337.92_B6_12M_final.crtf",
        },
    },
    "G337.92_B6_12M_robust-2": {
        "threshold": {4: "6e-4Jy"},
        "scales": [0, 3, 9, 27],
        "niter": {4: 30000},
        "maskname": {4: "G337.92_B6_12M_final.crtf"},
    },
    "G337.92_B6_12M_robust2": {
        "threshold": {4: "4.8e-4Jy"},
        "scales": [0, 3, 9, 27],
        "niter": {4: 30000},
        "maskname": {4: "G337.92_B6_12M_final.crtf"},
    },
    "W51-IRS2_B6_12M_robust0": {
        "threshold": {
            0: "0.3mJy",
            1: "0.25mJy",
            2: "0.25mJy",
            3: "0.25mJy",
            4: "0.25mJy",
            5: "0.25mJy",
            6: "0.2mJy",
            7: "0.2mJy",
            8: "0.2mJy",
        },
        "scales": [0, 3, 9, 27],
    },
    "W51-IRS2_B3_12M_robust0": {
        "threshold": {0: "0.3mJy", 1: "0.2mJy", 2: "0.2mJy", 3: "0.1mJy", 4: "0.08mJy"},
        "scales": [0, 3, 9, 27],
    },
    "W51-IRS2_B3_7M12M_robust0": {
        "threshold": {0: "0.5mJy", 1: "0.3mJy", 2: "0.2mJy", 3: "0.1mJy", 4: "0.08mJy"},
        "scales": [0, 3, 9, 27],
        "cell": ["0.0375arcsec", "0.0375arcsec"],
        "imsize": [4800, 4800],
    },
    "G338.93_B3_12M_robust0": {
        "threshold": {0: "0.36mJy", 1: "0.30mJy", 2: "0.15mJy", 3: "0.15mJy", "final": "0.1mJy"},
        "niter": {0: 10000, 1: 10000, 2: 15000, 3: 20000, "final": 200000},
    },
    "G338.93_B3_12M_robust2": {"threshold": {"final": "0.10mJy"}, "niter": {"final": 200000}},
    "G338.93_B3_12M_robust-2": {"threshold": {"final": "0.30mJy"}, "niter": {"final": 200000}},
    "G338.93_B3_12M_robust0_bsens": {
        "threshold": {0: "0.34mJy", 1: "0.25mJy", 2: "0.15mJy", 3: "0.12mJy", "final": "0.1mJy"},
        "niter": {0: 2000, 1: 2000, 2: 5000, 3: 8000, "final": 200000},
    },
    "G338.93_B3_12M_robust2_bsens": {"threshold": {"final": "0.10mJy"}, "niter": {"final": 200000}},
    "G338.93_B3_12M_robust-2_bsens": {"threshold": {"final": "0.30mJy"}, "niter": {"final": 200000}},
    "G338.93_B3_7M12M_robust0": {
        "threshold": {0: "0.5mJy", 1: "0.4mJy", 2: "0.2mJy", "final": "0.1mJy"},
        "niter": {0: 2000, 1: 5000, 2: 8000, "final": 200000},
        "scales": [0, 3, 9, 27],
    },
    "G338.93_B3_7M12M_robust2": {"threshold": {"final": "0.1mJy"}, "niter": {"final": 200000}},
    "G338.93_B3_7M12M_robust-2": {"threshold": {"final": "0.1mJy"}, "niter": {"final": 200000}},
    "W51-E_B6_12M_robust0": {
        "threshold": {
            0: "0.3mJy",
            1: "0.25mJy",
            2: "0.25mJy",
            3: "0.25mJy",
            4: "0.25mJy",
            5: "0.25mJy",
            6: "0.2mJy",
            7: "0.2mJy",
        },
        "scales": [0, 3, 9, 27],
    },
    "W51-E_B3_12M_robust0": {
        "threshold": {
            0: "0.15mJy",
            1: "0.15mJy",
            2: "0.1mJy",
            3: "0.09mJy",
            4: "0.09mJy",
            5: "0.08mJy",  # TIP: next time, go to 0.08.  0.07 takes _ages_
            6: "0.08mJy",
            7: "0.08mJy",
        },
        "niter": {
            0: 100000,  # limit to 100k for time considerations
            1: 100000,
            2: 100000,
            3: 100000,
            4: 100000,
            5: 100000,
            6: 100000,
            7: 100000,
            "final": 100000,
        },
        "scales": [0, 3, 9, 27],
        "imsize": [4800, 4800],
        "cell": ["0.0375arcsec", "0.0375arcsec"],
    },
    "W51-E_B3_12M_robust2": {"threshold": "0.15mJy", "scales": [0, 3, 9, 27], "imsize": [4800, 4800]},
    "W51-E_B3_12M_robust-2": {"threshold": "0.15mJy", "scales": [0, 3, 9], "imsize": [4800, 4800]},
    "W51-E_B3_12M_robust-0.5": {"threshold": "0.15mJy", "imsize": [4800, 4800]},
    "W51-E_B3_12M_robust0.5": {"threshold": "0.15mJy", "imsize": [4800, 4800]},
    "W51-E_B3_12M_robust1": {"threshold": "0.15mJy", "imsize": [4800, 4800]},
    "W51-E_B3_12M_robust-1": {"threshold": "0.15mJy", "imsize": [4800, 4800]},
    "W51-E_B6_7M12M_robust0": {"threshold": "3mJy", "scales": [0, 3, 9, 27]},
    "W51-E_B3_7M12M_robust0": {
        "threshold": {0: "5mJy", 1: "3mJy", 2: "1mJy", 3: "1mJy"},
        "scales": {0: [9, 27], 1: [3, 9, 27], 2: [0, 3, 9, 27], 3: [0, 3, 9, 27]},
        "cell": ["0.0375arcsec", "0.0375arcsec"],
        "imsize": [4800, 4800],
    },
    "W43-MM2_B6_12M_robust0": {
        "threshold": {
            0: "2.0mJy",
            1: "2.0mJy",
            2: "0.7mJy",
            3: "0.5mJy",
            4: "0.35mJy",
            5: "0.25mJy",
            "final": "0.35mJy",
        },
        "niter": {0: 1000, 1: 3000, 2: 10000, 3: 12000, 4: 15000, 5: 15000, "final": 22000},
        "scales": [0, 3, 9, 27],
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM2_B6_7M12M_robust0": {
        "threshold": {0: "2.0mJy", 1: "2.0mJy", 2: "1.0mJy", 3: "0.5mJy", 4: "0.4mJy", "final": "0.5mJy"},
        "niter": {0: 1000, 1: 5000, 2: 10000, 3: 10000, 4: 10000, "final": 25000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 81],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM3_B6_12M_robust0": {
        "threshold": {
            0: "1.0mJy",
            1: "1.0mJy",
            2: "0.25mJy",
            3: "0.25mJy",
            4: "0.25mJy",
            5: "0.25mJy",
            "final": "0.23mJy",
        },
        "niter": {0: 1000, 1: 3000, 2: 12000, 3: 12000, 4: 12000, 5: 15000, "final": 18000},
        "scales": [0, 3, 9, 27],
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM3_B6_7M12M_robust0": {
        "threshold": {0: "1.0mJy", 1: "1.0mJy", 2: "0.7mJy", 3: "0.35mJy", 4: "0.35mJy", "final": "0.5mJy"},
        "niter": {0: 1000, 1: 5000, 2: 10000, 3: 10000, 4: 10000, "final": 10000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 54],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM1_B3_12M_robust0": {
        "threshold": {0: "0.1mJy", 1: "0.1mJy", 2: "0.1mJy", 3: "0.1mJy", 4: "0.1mJy", "final": "0.1mJy"},
        "niter": {0: 20000, 1: 20000, 2: 20000, 3: 20000, 4: 20000, "final": 25000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 81],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM1_B3_7M12M_robust0": {
        "threshold": {0: "1.0mJy", 1: "1.0mJy", 2: "0.23mJy", 3: "0.15mJy", 4: "0.1mJy", "final": "0.05mJy"},
        "niter": {0: 1000, 1: 9000, 2: 13000, 3: 15000, 4: 17000, "final": 26000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 9, 27, 81, 162],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM2_B3_12M_robust0": {
        "threshold": {0: "0.2mJy", 1: "0.1mJy", 2: "0.1mJy", 3: "0.1mJy", 4: "0.1mJy", "final": "0.12mJy"},
        "niter": {0: 30000, 1: 30000, 2: 30000, 3: 30000, 4: 30000, "final": 30000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 9, 27, 81, 162],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM2_B3_7M12M_robust0": {
        "threshold": {0: "0.5mJy", 1: "1.0mJy", 2: "0.5mJy", 3: "0.2mJy", 4: "0.08mJy", "final": "0.06mJy"},
        "niter": {0: 9000, 1: 10000, 2: 12000, 3: 15000, 4: 20000, 5: 25000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 9, 27, 81, 162],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM3_B3_12M_robust0": {
        "threshold": {0: "0.1mJy", 1: "0.1mJy", 2: "0.1mJy", 3: "0.1mJy", 4: "0.1mJy", 5: "0.1mJy", "final": "0.11mJy"},
        "niter": {0: 20000, 1: 20000, 2: 20000, 3: 20000, 4: 20000, 5: 20000, "final": 24000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            5: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 81],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "W43-MM3_B3_7M12M_robust0": {
        "threshold": {0: "1.0mJy", 1: "1.0mJy", 2: "0.5mJy", 3: "0.2mJy", 4: "0.1mJy", "final": "0.04mJy"},
        "niter": {0: 3000, 1: 8000, 2: 15000, 3: 17000, 4: 20000, "final": 25000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 9, 27, 81, 162],
        },
        "maskname": {"final": ""},
        "usemask": {"final": "pb"},
    },
    "G353.41_B3_12M_robust-2": {"threshold": "0.5mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B3_12M_robust0": {"threshold": "0.36mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B3_12M_robust2": {"threshold": "0.28mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B3_7M12M_robust-2": {"threshold": "0.52mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B3_7M12M_robust0": {"threshold": "0.4mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B3_7M12M_robust2": {"threshold": "0.42mJy", "scales": [0, 3, 9, 27]},
    "G353.41_B6_12M_robust-2": {"threshold": "1.4mJy", "scales": [0, 3, 9]},
    "G353.41_B6_12M_robust0": {"threshold": "1.04mJy", "scales": [0, 3, 9]},
    "G353.41_B6_12M_robust2": {"threshold": "0.74mJy", "scales": [0, 3, 9]},
    "G353.41_B6_7M12M_robust-2": {"threshold": "1.4mJy", "scales": [0, 3, 9]},
    "G353.41_B6_7M12M_robust0": {"threshold": "1.06mJy", "scales": [0, 3, 9]},
    "G353.41_B6_7M12M_robust2": {"threshold": "0.82mJy", "scales": [0, 3, 9]},
    "G327.29_B3_12M_robust0": {
        "threshold": {0: "1.5mJy", 1: "0.6mJy", 2: "0.5mJy", "final": "0.1mJy"},
        "niter": {0: 1000, 1: 2000, 2: 5000, "final": 200000},
        "scales": [0, 3, 9, 27],
    },
    "G327.29_B3_12M_robust-2": {"threshold": {"final": "0.4mJy"}, "niter": {"final": 200000}, "scales": [0, 3, 9, 27]},
    "G327.29_B3_12M_robust2": {"threshold": {"final": "0.4mJy"}, "niter": {"final": 200000}, "scales": [0, 3, 9, 27]},
    "G327.29_B3_7M12M_robust0": {
        "threshold": {0: "2.0mJy", 1: "1.8mJy", "final": "1.5mJy"},
        "niter": {0: 5000, 1: 5000, "final": 200000},
        "scales": [0, 3, 9, 27],
    },
    "G327.29_B3_7M12M_robust-2": {
        "threshold": {"final": "0.5mJy"},
        "niter": {"final": 200000},
        "scales": [0, 3, 9, 27],
    },
    "G327.29_B3_7M12M_robust2": {"threshold": {"final": "0.5mJy"}, "niter": {"final": 100000}, "scales": [0, 3, 9, 27]},
    "G327.29_B6_12M_robust0": {
        "threshold": {0: "2.0mJy", 1: "1.5mJy", 2: "1.0mJy", 3: "1.0mJy", 4: "0.8mJy", 5: "0.5mJy", "final": "0.5mJy"},
        "niter": {0: 1000, 1: 1000, 2: 5000, 3: 8000, 4: 10000, 5: 10000, "final": 20000},
        "scales": [0, 3, 9, 27],
    },
    "G327.29_B6_12M_robust2": {"threshold": {"final": "1.0mJy"}, "niter": {"final": 20000}},
    "G327.29_B6_12M_robust-2": {"threshold": {"final": "1.0mJy"}, "niter": {"final": 20000}},
    "G327.29_B6_7M12M_robust0": {
        "threshold": {0: "2.0mJy", 1: "1.5mJy", 2: "1.0mJy", 3: "0.8mJy", 4: "0.8mJy", 5: "0.5mJy"},
        "niter": {0: 1000, 1: 1000, 2: 5000, 3: 8000, 4: 10000, 5: 200000},
        "scales": [0, 3, 9, 27],
    },
    "G327.29_B6_7M12M_robust2": {"threshold": {5: "1.0mJy"}, "niter": {5: 20000}},
    "G327.29_B6_7M12M_robust-2": {"threshold": {5: "1.0mJy"}, "niter": {5: 20000}},
    "G010.62_B3_12M_robust0": {
        "threshold": {
            0: "10mJy",
            1: "5mJy",
            2: "2.5 mJy",
            3: "1.0mJy",
            4: "0.5mJy",
            5: "0.3mJy",
            6: "0.3mJy",
            7: "0.3mJy",
        },
        "niter": {0: 700, 1: 1300, 2: 2500, 3: 5000, 4: 10000, 5: 10000, 6: 15000, 7: 15000},
        "maskname": {
            0: "G010.62_centralBox_50_30.crtf",
            1: "G010.62_B3_50mJy.crtf",
            2: "G010.62_B3_15mJy.crtf",
            3: "G010.62_B3_05mJy.crtf",
            4: "G010.62_B3_03mJy.crtf",
            5: "G010.62_B3_01mJy.crtf",
            6: "G010.62_B3_iter6.crtf",
            7: "G010.62_B3_iter6.crtf",
        },
    },
    "G010.62_B6_12M_robust0": {
        "threshold": {0: "10mJy", 1: "5mJy", 2: "2.5 mJy", 3: "1.0mJy", 4: "0.5mJy", 5: "0.3mJy"},
        "niter": {0: 700, 1: 2500, 2: 5000, 3: 7500, 4: 10000, 5: 20000},
        "maskname": {
            0: "G010.62_centralBox_50_30.crtf",
            1: "G010.62_B6_early_iterations.crtf",
            2: "G010.62_B6_early_iterations.crtf",
            3: "G010.62_B6_early_iterations.crtf",
            4: "G010.62_B6_late_iterations.crtf",
            5: "G010.62_B6_late_iterations.crtf",
        },
    },
    "G351.77_B6_7M_robust0": {
        "threshold": {0: "12.0mJy", 1: "12mJy", 2: "3mJy", 3: "0.25mJy", 4: "0.25mJy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 25000},
        "scales": [0, 3],
        "maskname": {
            0: "G351.77_B6_7M12M_iter1.crtf",
            1: "G351.77_B6_7M_iter1.crtf",
            2: "G351.77_B6_7M_iter1.crtf",
            3: "G351.77_B6_7M_iter1.crtf",
            4: "G351.77_B6_7M_iter1.crtf",
        },
    },
    "G351.77_B6_7M12M_robust0": {
        "threshold": {0: "10.0mJy", 1: "10.0mJy", 2: "5.0mJy", 3: "1.0mJy", 4: "1.0mJy", "final": "1.0mJy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 25000},
        "scales": [0, 3],
        "maskname": {
            0: "G351.77_B6_7M12M_iter1.crtf",
            1: "G351.77_B6_7M_iter1.crtf",
            2: "G351.77_B6_7M_iter1.crtf",
            3: "G351.77_B6_7M_iter1.crtf",
            4: "G351.77_B6_7M_iter1.crtf",
            "final": "G351.77_B6_7M12M_finaliter.crtf",
        },
    },
    "G351.77_B6_7M12M_robust2": {
        "threshold": {"final": "1.0mJy"},
        "niter": {"final": 25000},
        "scales": [0, 3],
        "maskname": {"final": "G351.77_B6_7M12M_finaliter.crtf"},
    },
    "G351.77_B6_7M12M_robust-2": {
        "threshold": {"final": "1.0mJy"},
        "niter": {"final": 18000},
        "scales": [0, 3],
        "maskname": {"final": "G351.77_B6_7M12M_finaliter.crtf"},
    },
    "G351.77_B6_12M_robust0": {
        "threshold": {0: "12e-4Jy", 1: "12e-4Jy", 2: "12e-4Jy", 3: "12e-4Jy", 4: "12e-4Jy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "maskname": {
            0: "G351.77_B6_12M.crtf",
            1: "G351.77_B6_12M.crtf",
            2: "G351.77_B6_12M.crtf",
            3: "G351.77_B6_12M.crtf",
            4: "G351.77_B6_12M.crtf",
            "final": "G351.77_B6_12M_final.crtf",
        },
    },
    "G351.77_B6_12M_robust2": {
        "threshold": {4: "10e-4Jy"},
        "niter": {4: 18000},
        "maskname": {4: "G351.77_B6_12M_final.crtf"},
    },
    "G351.77_B6_12M_robust-2": {
        "threshold": {0: "14.4e-4Jy", 1: "14.4e-4Jy", 2: "14.4e-4Jy", 3: "14.4e-4Jy", 4: "14.4e-4Jy"},
        "niter": {4: 18000},
        "maskname": {4: "G351.77_B6_12M_final.crtf"},
    },
    "G351.77_B3_12M_robust-2": {
        "threshold": {4: "8e-4Jy"},
        "niter": {4: 18000},
        "maskname": {4: "G351.77_B3_12M_robust2_bsens.crtf"},
    },
    "G351.77_B3_12M_robust2": {
        "threshold": {4: "3e-4Jy"},
        "niter": {4: 18000},
        "maskname": {4: "G351.77_B3_12M_robust2_bsens.crtf"},
    },
    "G351.77_B3_12M_robust0": {
        "threshold": {0: "3e-4Jy", 1: "3e-4Jy", 2: "3e-4Jy", 3: "3e-4Jy", 4: "3e-4Jy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "maskname": {
            0: "G351.77_B3_12M_robust2_bsens.crtf",
            1: "G351.77_B3_12M_robust2_bsens.crtf",
            2: "G351.77_B3_12M_robust2_bsens.crtf",
            3: "G351.77_B3_12M_robust2_bsens.crtf",
            4: "G351.77_B3_12M_robust2_bsens.crtf",
        },
    },
    "G351.77_B3_7M12M_robust-2": {
        "threshold": {4: "3.2e-4Jy"},
        "niter": {4: 18000},
        "scales": [0, 3],
        "maskname": {4: "G351.77_B3_7M12M_robust2_bsens.crtf"},
    },
    "G351.77_B3_7M12M_robust2": {
        "threshold": {4: "1.8e-4Jy"},
        "niter": {4: 18000},
        "scales": [0, 3],
        "maskname": {4: "G351.77_B3_7M12M_robust2_bsens.crtf"},
    },
    "G351.77_B3_7M12M_robust0": {
        "threshold": {0: "2e-4Jy", 1: "2e-4Jy", 2: "2e-4Jy", 3: "2e-4Jy", 4: "2e-4Jy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 9000, 4: 9000},
        "scales": [0, 3],
        "maskname": {
            0: "G351.77_B3_7M12M_robust2_bsens.crtf",
            1: "G351.77_B3_7M12M_robust2_bsens.crtf",
            2: "G351.77_B3_7M12M_robust2_bsens.crtf",
            3: "G351.77_B3_7M12M_robust2_bsens.crtf",
            4: "G351.77_B3_7M12M_robust2_bsens.crtf",
        },
    },
    "G338.93_B6_12M_robust0": {
        "threshold": {
            0: "1.2mJy",
            1: "1.2mJy",
            2: "0.9mJy",
            3: "0.8mJy",
            4: "0.7mJy",
            5: "0.5mJy",
            6: "0.35mJy",
            "final": "0.35mJy",
        },
        "niter": {0: 1000, 1: 1000, 2: 2000, 3: 3000, 4: 4000, 5: 5000, 6: 6000, "final": 50000},
        "scales": [0, 3, 9, 27],
    },
    "G338.93_B6_12M_robust2": {"threshold": {"final": "0.25mJy"}, "niter": {"final": 20000}, "scales": [0, 3, 9, 27]},
    "G338.93_B6_12M_robust-2": {"threshold": {"final": "0.50mJy"}, "niter": {"final": 20000}, "scales": [0, 3, 9]},
    "G338.93_B6_12M_robust0_bsens": {
        "threshold": {
            0: "1.2mJy",
            1: "1.2mJy",
            2: "0.9mJy",
            3: "0.8mJy",
            4: "0.7mJy",
            5: "0.5mJy",
            6: "0.30mJy",
            "final": "0.35mJy",
        },
        "niter": {0: 1000, 1: 1000, 2: 2000, 3: 3000, 4: 4000, 5: 5000, 6: 6000, "final": 50000},
        "scales": [0, 3, 9, 27],
    },
    "G338.93_B6_12M_robust2_bsens": {
        "threshold": {"final": "0.20mJy"},
        "niter": {"final": 20000},
        "scales": [0, 3, 9, 27],
    },
    "G338.93_B6_12M_robust-2_bsens": {
        "threshold": {"final": "0.45mJy"},
        "niter": {"final": 20000},
        "scales": [0, 3, 9],
    },
    "G328.25_B6_7M12M_robust0": {
        "threshold": {0: "6mJy", 1: "4mJy", 2: "4mJy", 3: "4mJy", 4: "1.5mJy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "scales": [0, 3],
        "maskname": {
            0: "G328_B6_7M12M_iter2_n2.crtf",
            1: "G328_B6_7M12M_iter2_n2.crtf",
            2: "G328_B6_7M12M_iter2_n2.crtf",
            3: "G328_B6_7M12M_iter4_n.crtf",
            4: "G328_B6_clean_robust0.crtf",
        },
    },
    "G328.25_B6_7M12M_robust2": {
        "threshold": {4: "1.5mJy"},
        "niter": {4: 18000},
        "scales": [0, 3],
        "maskname": {4: "G328_B6_clean_robust0.crtf"},
    },
    "G328.25_B6_7M12M_robust-2": {
        "threshold": {4: "2mJy"},
        "niter": {4: 18000},
        "scales": [0, 3],
        "maskname": {4: "G328_B6_clean_robust0.crtf"},
    },
    "G328.25_B6_12M_robust0": {
        "threshold": {0: "1e-3Jy", 1: "2mJy", 2: "1mJy", 3: "0.5mJy", 4: "0.5mJy"},
        "niter": {0: 3000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "maskname": {
            0: "G328_B6_clean_12M_robust0_3sigma.crtf",
            1: "G328_B6_clean_robust0.crtf",
            2: "G328_B6_clean_robust0.crtf",
            3: "G328_B6_clean_robust0.crtf",
            4: "G328_B6_clean_robust0.crtf",
        },
    },
    "G328.25_B6_12M_robust-2": {
        "threshold": {0: "16e-4Jy", 1: "2mJy", 2: "1mJy", 3: "0.5mJy", 4: "0.5mJy", 5: "0.5mJy"},
        "niter": {0: 3000, 1: 3000, 2: 9000, 3: 18000, 4: 18000, 5: 18000},
        "maskname": {
            0: "G328_B6_clean_12M_robust0_3sigma.crtf",
            1: "G328_B6_clean_robust0.crtf",
            2: "G328_B6_clean_robust0.crtf",
            3: "G328_B6_clean_robust0.crtf",
            4: "G328_B6_clean_robust0.crtf",
            5: "G328_B6_clean_robust0.crtf",
        },
    },
    "G328.25_B6_12M_robust2": {
        "threshold": {0: "8e-4Jy", 1: "2mJy", 2: "1mJy", 3: "0.5mJy", 4: "0.5mJy", 5: "0.5mJy"},
        "niter": {0: 3000, 1: 3000, 2: 9000, 3: 18000, 4: 18000, 5: 18000},
        "maskname": {
            0: "G328_B6_clean_12M_robust0_3sigma.crtf",
            1: "G328_B6_clean_robust0.crtf",
            2: "G328_B6_clean_robust0.crtf",
            3: "G328_B6_clean_robust0.crtf",
            4: "G328_B6_clean_robust0.crtf",
            5: "G328_B6_clean_robust0.crtf",
        },
    },
    "G328.25_B3_7M12M_robust0": {
        "threshold": {0: "0.6mJy", 1: "0.3mJy", 2: "0.3mJy", 3: "0.3mJy", 4: "0.2mJy"},  # rms = 3e-4 Jy/beam
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "maskname": {
            0: "G328.25_B3_12M_clean_robust2_1stiter_3sigma.crtf",
            1: "G328.25_B3_7M12M_clean_robust0_1stiter_3sigma.crtf",
            2: "G328_B3_mask.crtf",
            3: "G328_B3_mask.crtf",
            4: "G328_B3_mask.crtf",
        },
    },
    "G328.25_B3_7M12M_robust-2": {"threshold": {4: "1mJy"}, "niter": {4: 25000}, "maskname": {4: "G328_B3_mask.crtf"}},
    "G328.25_B3_7M12M_robust2": {"threshold": {4: "1mJy"}, "niter": {4: 25000}, "maskname": {4: "G328_B3_mask.crtf"}},
    "G328.25_B3_12M_robust0": {
        "threshold": {0: "0.30mJy", 1: "0.3mJy", 2: "0.3mJy", 3: "0.3mJy", 4: "0.2mJy"},  # rms = 1e-4 Jy/beam
        "niter": {0: 5000, 1: 9000, 2: 10000, 3: 15000, 4: 20000},
        "maskname": {
            0: "G328.25_B3_12M_clean_robust0_1stiter_3sigma.crtf",
            1: "G328.25_B3_12M_clean_robust0_1stiter_3sigma.crtf",
            2: "G328.25_B3_12M_clean_robust0_1stiter_3sigma.crtf",
            3: "G328.25_B3_12M.crtf",
            4: "G328.25_B3_12M.crtf",
        },
    },
    "G328.25_B3_12M_robust-2": {
        "threshold": {4: "3.2e-4Jy"},  # 2*RMS, RMS =1.6e-4 Jy/beam
        "niter": {4: 15000},
        "maskname": {4: "G328.25_B3_12M.crtf"},
    },  # RMS ~ 1e-4 Jy/beam for BSENS
    "G328.25_B3_12M_robust2": {
        "threshold": {4: "1.9e-4Jy"},  # RMS = 0.95e-4 Jy/beam
        "niter": {4: 15000},
        "maskname": {4: "G328.25_B3_12M.crtf"},
    },  # RMS ~ 1e-4 Jy/beam for BSENS
    "G328.25_B6_7M_robust0": {
        "threshold": {0: "10mJy", 1: "5mJy", 2: "5mJy", 3: "5mJy", 4: "5mJy"},
        "niter": {0: 1000, 1: 3000, 2: 9000, 3: 18000, 4: 18000},
        "scales": [0, 3],
        "maskname": {
            0: "G328_B6_clean_robust0.crtf",
            1: "G328_B6_clean_robust0.crtf",
            2: "G328_B6_clean_robust0.crtf",
            3: "G328_B6_clean_robust0.crtf",
            4: "G328_B6_clean_robust0.crtf",
        },
    },
}


for key in imaging_parameters_nondefault:
    if "bsens" in key:
        check_key = "_".join(key.split("_")[:-1])
        assert check_key in imaging_parameters, "key {0} not in impars!".format(check_key)
        imaging_parameters[key] = copy.deepcopy(imaging_parameters[check_key])
    else:
        assert key in imaging_parameters, "key {0} was not in impars".format(key)
    imaging_parameters[key].update(imaging_parameters_nondefault[key])


# copy robust -2 parameters to robust -1
# copy robust 2 parameters to robust 1
# copy robust 0 parameters to robust 0.5, -0.5
for key in list(imaging_parameters.keys()):
    robustnum = [x for x in key.split("_") if "robust" in x][0]
    if "robust-2" == robustnum:
        imaging_parameters[key.replace("robust-2", "robust-1")] = imaging_parameters[key].copy()
        imaging_parameters[key.replace("robust-2", "robust-1")]["robust"] = -1
    elif "robust2" == robustnum:
        imaging_parameters[key.replace("robust2", "robust1")] = imaging_parameters[key].copy()
        imaging_parameters[key.replace("robust2", "robust1")]["robust"] = 1
    elif "robust0" == robustnum:
        if "robust0.5" in key:
            raise ValueError("This isn't supposed to happen")
        imaging_parameters[key.replace("robust0", "robust0.5")] = imaging_parameters[key].copy()
        imaging_parameters[key.replace("robust0", "robust-0.5")] = imaging_parameters[key].copy()
        imaging_parameters[key.replace("robust0", "robust0.5")]["robust"] = 0.5
        imaging_parameters[key.replace("robust0", "robust-0.5")]["robust"] = -0.5
    elif robustnum in ("robust0.5", "robust-0.5", "robust1", "robust-1"):
        pass
    else:
        raise ValueError("Surprising robust value found")

for key in list(imaging_parameters.keys()):
    robust = [x for x in key.split("_") if "robust" in x][0]
    robustnum = float(robust[6:])
    assert robustnum == imaging_parameters[key]["robust"]


"""
Self-calibration parameters are defined here
"""

default_selfcal_pars = {
    ii: {
        "solint": "inf",
        "gaintype": "T",
        "solnorm": True,
        # 'combine': 'spw', # consider combining across spw bounds
        "calmode": "p",
    }
    for ii in range(1, 5)
}

selfcal_pars_default = {key: copy.deepcopy(default_selfcal_pars) for key in imaging_parameters}

selfcal_pars_custom = {
    "G008.67_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "solint": "200s", "solnorm": False},
    },
    "G008.67_B3_12M_robust0_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "solint": "200s", "solnorm": False},
    },
    "G008.67_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "solint": "200s", "solnorm": False},
    },
    "G008.67_B6_12M_robust0_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "solint": "200s", "solnorm": False},
    },
    "G008.67_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G008.67_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "40s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "25s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "10s", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "solint": "10s", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "solint": "10s", "solnorm": True},
        7: {"calmode": "ap", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G010.62_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "45s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "30s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": True},
    },
    "G010.62_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "40s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "25s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "10s", "solnorm": True},
    },
    "G010.62_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "45s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "30s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": True},
    },
    "G010.62_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G010.62_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "300s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        6: {"calmode": "ap", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
    },
    "G012.80_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "minsnr": 5, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "G", "minsnr": 5, "solint": "inf", "solnorm": False},
        3: {"calmode": "p", "gaintype": "G", "minsnr": 5, "solint": "1200s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "G", "minsnr": 4, "solint": "600s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "G", "minsnr": 5, "solint": "inf", "solnorm": False},
    },
    "G012.80_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G012.80_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "60s", "solnorm": True},
    },
    "G327.29_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_7M12M_robust0": {1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True}},
    "G327.29_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "G", "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "G", "solint": "20s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "G", "solint": "10s", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "5s", "solnorm": True},
    },
    "G327.29_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "G", "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "G", "solint": "20s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "G", "solint": "10s", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "5s", "solnorm": True},
    },
    "G327.29_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G327.29_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_12M_robust0": {
        1: {
            "calmode": "p",
            "combine": "scan,scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
        2: {
            "calmode": "p",
            "combine": "scan,scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
        3: {
            "calmode": "p",
            "combine": "scan,scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
        4: {
            "calmode": "p",
            "combine": "scan,scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
    },
    "G328.25_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M12M_robust0": {
        1: {
            "calmode": "p",
            "combine": "scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
        2: {
            "calmode": "p",
            "combine": "scan",
            "gaintype": "T",
            "minblperant": 3,
            "minsnr": 2,
            "refant": "DV01",
            "solint": "inf",
            "solnorm": False,
        },
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_12M_robust0": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "300s", "solnorm": False},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "90s", "solnorm": False},
        4: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": False},
    },
    "G328.25_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_7M12M_robust0": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "300s", "solnorm": False},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "200s", "solnorm": False},
        4: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "90s", "solnorm": False},
    },
    "G328.25_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G328.25_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "inf", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "100s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "60s", "solnorm": False},
    },
    "G328.25_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
    },
    "G333.60_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
    },
    "G333.60_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_12M_robust0": {
        1: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "int", "solnorm": False},
    },
    "G333.60_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_7M12M_robust0": {
        1: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "int", "solnorm": False},
        # 5: {"calmode": "ap", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G333.60_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_12M_robust0": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "300s", "solnorm": False},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": False},
        4: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "30s", "solnorm": False},
    },
    "G337.92_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_7M12M_robust0": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "int", "solnorm": False},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "90s", "solnorm": False},
        4: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": False},
    },
    "G337.92_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "60s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "30s", "solnorm": True},
    },
    "G337.92_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G337.92_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_12M_robust-2_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_12M_robust0": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": True},
    },
    "G338.93_B3_12M_robust0_bsens": {
        1: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_12M_robust2_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "combine": "scan", "gaintype": "T", "solint": "60s", "solnorm": True},
    },
    "G338.93_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_12M_robust-2_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "G", "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "G", "solint": "30s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "G", "solint": "20s", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "10s", "solnorm": True},
        6: {"calmode": "p", "gaintype": "G", "solint": "5s", "solnorm": True},
    },
    "G338.93_B6_12M_robust0_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "30s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "20s", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "solint": "10s", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "solint": "5s", "solnorm": True},
    },
    "G338.93_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_12M_robust2_bsens": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G338.93_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "90s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "60s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "30s", "solnorm": False},
    },
    "G351.77_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "90s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "60s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "30s", "solnorm": False},
    },
    "G351.77_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "150s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "60s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 2, "solint": "30s", "solnorm": False},
    },
    "G351.77_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "300s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "150s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "60s", "solnorm": False},
    },
    "G351.77_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G351.77_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "inf", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "100s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 3, "solint": "60s", "solnorm": False},
    },
    "G351.77_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        6: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
    },
    "G353.41_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        6: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
    },
    "G353.41_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        6: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
    },
    "G353.41_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "G353.41_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False, "minsnr": 3},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False, "minsnr": 3},
        3: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False, "minsnr": 3},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False, "minsnr": 3},
    },
    "W43-MM1_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM1_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True, "minsnr": 3},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True, "minsnr": 3},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True, "minsnr": 3},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True, "minsnr": 3},
    },
    "W43-MM2_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "G", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "G", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "G", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
    },
    "W43-MM2_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "G", "solint": "500s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
        4: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
    },
    "W43-MM2_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM2_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "200s", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "300s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
    },
    "W43-MM3_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "G", "solint": "1200s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "G", "solint": "600s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "G", "solint": "300s", "solnorm": False},
        5: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
    },
    "W43-MM3_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "G", "solint": "500s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
        4: {"calmode": "p", "gaintype": "G", "solint": "int", "solnorm": False},
    },
    "W43-MM3_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W43-MM3_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "G", "minsnr": 5, "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "int", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "int", "solnorm": True},
        7: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "int", "solnorm": True},
        7: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "int", "solnorm": True},
    },
    "W51-E_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        6: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        7: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-E_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B3_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_12M_robust0": {
        1: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": True},
        2: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": True},
        3: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": True},
        4: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": True},
        5: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": False},
        6: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": False},
        7: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "60s", "solnorm": False},
        8: {"calmode": "ap", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
    },
    "W51-IRS2_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_7M12M_robust0": {
        1: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": True},
        5: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        6: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        7: {"calmode": "p", "combine": "", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
    },
    "W51-IRS2_B6_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_7M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
    "W51-IRS2_B6_7M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
    },
}


selfcal_pars = selfcal_pars_default.copy()
for key in selfcal_pars_custom:
    for iternum in selfcal_pars_custom[key]:
        if iternum in selfcal_pars[key]:
            selfcal_pars[key][iternum].update(selfcal_pars_custom[key][iternum])
        else:
            selfcal_pars[key][iternum] = selfcal_pars_custom[key][iternum]

del selfcal_pars["G338.93_B3_12M_robust0"][4]
del selfcal_pars["G338.93_B3_12M_robust0_bsens"][4]
del selfcal_pars["G338.93_B3_7M12M_robust0"][3]
del selfcal_pars["G338.93_B3_7M12M_robust0"][4]
del selfcal_pars["G327.29_B3_12M_robust0"][3]
del selfcal_pars["G327.29_B3_12M_robust0"][4]
del selfcal_pars["G327.29_B3_7M12M_robust0"][2]
del selfcal_pars["G327.29_B3_7M12M_robust0"][3]
del selfcal_pars["G327.29_B3_7M12M_robust0"][4]


line_imaging_parameters_default = {
    "{0}_{1}_{2}_robust{3}{4}".format(field, band, array, robust, contsub): {
        "niter": 5000000,
        "threshold": "5sigma",
        "robust": robust,
        "weighting": "briggs",
        "deconvolver": "hogbom",
        # "scales": [0, 3, 9, 27, 81],
        # "nterms": 1,
        "gridder": "mosaic",
        "specmode": "cube",
        "outframe": "LSRK",
        "veltype": "radio",
        "usemask": "pb",
        "pblimit": 0.05,
        "pbmask": 0.1,
        "perchanweightdensity": False,
        "interactive": False,
        "mask_out_endchannels": 2,
    }
    for field in allfields
    for band in ("B3", "B6")
    for array in ("12M", "7M12M", "7M")
    # for robust in (0,)
    for robust in (-2, 0, 2)
    for contsub in ("", "_contsub")
}

line_imaging_parameters = copy.deepcopy(line_imaging_parameters_default)

line_imaging_parameters_custom = {
    "G008.67_B3_12M_robust0": {
        "threshold": "8mJy",
        # "startmodel": "G008.67_B3_uid___A001_X1296_X1bf_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1c1 instead of 1bf as of 10/23/2020
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0": {
        "threshold": "33mJy",  # "28mJy",#estimated noise: 9-11 mJy, from sio-only cube
        # "startmodel": "G008.67_B6_uid___A001_X1296_X1b9_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1b9 instead of 1b7 as of 10/14/2020 - this may change
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_sio": {
        "threshold": "33mJy",  # typical rms is 9-11 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B3_12M_robust0": {
        "threshold": "6mJy",
        # "startmodel": "G010.62_B3_uid___A001_X1296_X1e9_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1e9 instead of 1e5 as of 10/14/2020 - this may change
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G010.62_B6_12M_robust0": {
        "threshold": "9.6mJy",  # "6mJy", #estimated noise: 2.8-3.2 mJy, from sio-only cube
        # "startmodel": "G010.62_B6_uid___A001_X1296_X1df_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1db instead of 1df as of 10/16/2020 - this may change
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_sio": {
        "threshold": "9.6mJy",  # typical rms is 2.8-3.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G012.80_B3_12M_robust0": {
        "threshold": "6mJy",
        # "startmodel": "G012.80_B3_uid___A001_X1296_X1f9_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1fb instead of 1f9 as of 10/16/2020 - this may change
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G012.80_B6_12M_robust0": {
        "threshold": "39mJy",  # "24mJy", #estimated noise: 13 mJy, from sio-only cube
        # "startmodel": "G012.80_B6_uid___A001_X1296_X1f1_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 1ef instead of 1f1 as of 10/16/2020 - this may change
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G012.80_B6_12M_robust0_sio": {
        "threshold": "39mJy",  # typical rms values are 10-13 mJy, using 3sigma as threshold (14 Dec. 2020)
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B3_12M_robust0": {
        "threshold": "6mJy",
        # "startmodel": "G327.29_B3_uid___A001_X1296_X17f_continuum_merged_12M_robust0_selfcal2_finaliter",
        # UF machine has 17d instead of 17f as of 10/14/2020 - this may change
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B6_12M_robust0": {
        "threshold": "34.5mJy",  # "6mJy", #estimated noise: 9.5-11.5 mJy, from sio-only cube
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_sio": {
        "threshold": "34.5mJy",  # typical rms 9.5-11.5 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    #   Missing startmodel continuum B3 image
    # 	"G328.25_B3_12M_robust0": {
    # 		"threshold": "6mJy",
    # 		"startmodel": ""
    # 	},
    "G328.25_B6_12M_robust0": {
        "threshold": "63mJy",  # "6mJy", #estimated noise: 15-21 mJy, from sio-only cube
        # "startmodel": "G328.25_B6_uid___A001_X1296_X161_continuum_merged_12M_robust0_selfcal5_finaliter",
        # UF machine has 163 instead of 161 as of 10/14/2020 - this may change
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_sio": {
        "threshold": "63mJy",  # typical rms is 15-21 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G333.60_B3_12M_robust0": {
        "threshold": "6mJy",
        # never correct "startmodel": "G333.60_B3__continuum_merged_12M_robust0_selfcal5_finaliter.image",
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G333.60_B6_12M_robust0": {
        "threshold": "15.6mJy",  # "6mJy",#estimated noise: 4.3-5.2 mJy, from sio-only cube
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G333.60_B6_12M_robust0_sio": {
        "threshold": "15.6mJy",  # typical rms is 4.3-5.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G337.92_B3_12M_robust0": {
        "threshold": "5mJy",
        # "startmodel": "G337.92_B3_uid___A001_X1296_X145_continuum_merged_12M_robust0_selfcal4_finaliter",
        # UF machine has 147 instead of 145 as of 10/14/2020 - this may change
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0": {
        "threshold": "16.8mJy",  # "12mJy", #estimated noise: 4.8-5.6 mJy, from sio-only cube
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_sio": {
        "threshold": "16.8mJy",  # typical rms 4.8-5.6 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G338.93_B3_12M_robust0": {
        "threshold": "5mJy",
        # "startmodel": "G338.93_B3_uid___A001_X1296_X15b_continuum_merged_12M_robust0_selfcal2_finaliter",
        # UF machine has 159 instead of 15b as of 10/16/2020 - this may change
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B3_12M_robust0_n2hp": {
        "threshold": "5mJy",
        # "startmodel": "G338.93_B3_uid___A001_X1296_X15b_continuum_merged_12M_robust0_selfcal2_finaliter",
        # UF machine has 159 instead of 15b as of 10/16/2020 - this may change
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B6_12M_robust0": {
        "threshold": "18mJy",  # "6mJy", #estimated noise: 5-6 mJy, from sio-only cube
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_sio": {
        "threshold": "18mJy",  # typical rms in 5-6 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G351.77_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0": {
        "threshold": "48mJy",  # "6mJy",#estimated noise: 12-16 mJy, from sio-only cube
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_sio": {
        "threshold": "48mJy",  # typical rms is 12-16 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G353.41_B3_12M_robust0": {
        "threshold": "6mJy",
        # UF machine has selfcal 6, not selfcal 3 - this will probably not change
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0": {
        "threshold": "48mJy",  # "6mJy", #estimated noise: 12.5-16 mJy, from sio-only cube
        # "startmodel": "G353.41_B6_uid___A001_X1296_X1cb_continuum_merged_12M_robust0_selfcal3_finaliter",
        # UF machine has 1c9 selfcal6 instead of 1cb selfcal3 as of 10/15/2020 - this may change
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_sio": {
        "threshold": "48mJy",  # typical rms is 12.5-16 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "W43-MM1_B3_12M_robust0": {
        "threshold": "6mJy",
        # "startmodel": "W43-MM1_B3_uid___A001_X1296_X1ad_continuum_merged_12M_robust0_selfcal4_finaliter",
        # UF machine has 1af selfcal4 instead of 1ad selfcal4 as of 11/3/2020 - this may change
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11f_continuum_merged_12M_robust0_selfcal4_finaliter",
        # UF machine has 11b instead of 11f selfcal3 as of 10/15/2020 - this may change
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B6_12M_robust0": {
        "threshold": "8.1mJy",  # "6mJy", #estimated noise: 2.7 mJy, from sio-only cube
        # NOTE: 111/113 name ambiguous
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [1280, 1280],
    },
    "W43-MM2_B6_12M_robust0_contsub": {"imsize": [1280, 1280],},
    "W43-MM2_B6_12M_robust0_sio": {
        "threshold": "8.1mJy",  # typical rms: 2.3-2.7 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0": {
        "threshold": "9.3mJy",  # "6mJy", #estimated noise: 3.1 mJy, from sio-only cube
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [1280, 1280],
    },
    "W43-MM3_B6_12M_robust0_sio": {
        "threshold": "9.3mJy",  # typical rms is 2.7-3.1 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W51-E_B3_12M_robust0": {
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal4",
        "threshold": "4mJy",  # sigma is ~0.8 mJy
        "pblimit": 0.05,  # per Nov 6 telecon
    },
    "W51-E_B6_12M_robust0": {
        "pblimit": 0.1,
        "threshold": "16mJy",  # sigma is ~ 4 mJy  (from sio cube, noise is 3.3-4.1 mJy)
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_sio": {
        "threshold": "12.3mJy",  # typical rms is 3.3-4.1 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw1": {
        "threshold": "12.3mJy",  # typical rms is 3.3-4.1 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-IRS2_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W51-IRS2_B6_12M_robust0": {
        "threshold": "9.6mJy",  # "6mJy", #estimated noise: 3.2 mJy, from sio-only cube
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal8_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_sio": {
        "threshold": "9.6mJy",  # typical rms is 2.7-3.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal8_finaliter",
    },
}


for key in line_imaging_parameters_custom:
    if key in line_imaging_parameters:
        line_imaging_parameters[key].update(line_imaging_parameters_custom[key])
    elif "_".join(key.split(["_"])[:-1]) in line_imaging_parameters:
        # special case - strip off the trailing SiO or N2H+ or whatever
        noline_key = "_".join(key.split(["_"])[:-1])
        line_imaging_parameters[key] = line_imaging_parameters[noline_key]
        line_imaging_parameters[key].update(line_imaging_parameters_custom[key])
    else:
        line_imaging_parameters[key] = line_imaging_parameters_custom[key]


default_lines = {
    "h41a": "92.034434GHz",
    "ch3cnv8=1": "92.26144GHz",
    "13cs_2-1": "92.49430800GHz",
    "n2hp": "93.173700GHz",
    "ch3cch_62-52": "102.547983GHz",
    "h2cs_312-211": "104.617040GHz",
    "oc33s_18-17": "216.14735900GHz",
    "sio": "217.104984GHz",
    "h2co_303-202": "218.222195GHz",
    "c18o": "219.560358GHz",
    "so_6-5": "219.94944200GHz",
    "12co": "230.538GHz",
    "ocs_19-18": "231.06099340GHz",
    "13cs_5-4": "231.22068520GHz",
    "h30a": "231.900928GHz",
}
field_vlsr = {
    "W51-E": "55km/s",
    "W51-IRS2": "55km/s",
    "G010.62": "-2km/s",
    "G353.41": "-18km/s",
    "W43-MM1": "97km/s",
    "W43-MM2": "97km/s",
    "W43-MM3": "97km/s",
    "G337.92": "-40km/s",
    "G338.93": "-62km/s",
    "G328.25": "-43km/s",
    "G327.29": "-45km/s",
    "G333.60": "-47km/s",
    "G008.67": "37.60km/s",
    "G012.80": "37.00km/s",
    "G351.77": "-3.00km/s",
}
# line parameters are converted by line_imaging.py into tclean parameters
line_parameters_default = {
    field: {
        line: {"restfreq": freq, "vlsr": field_vlsr[field], "cubewidth": "50km/s"}
        for line, freq in default_lines.items()
    }
    for field in allfields
}
for field in allfields:
    line_parameters_default[field]["12co"]["cubewidth"] = "150km/s"
    line_parameters_default[field]["ch3cnv8=1"]["cubewidth"] = "150km/s"  # is 150 wide enough?
line_parameters = copy.deepcopy(line_parameters_default)

line_parameters_custom = {
    "G008.67": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "80km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "44km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "44km/s"},
    },
    "G010.62": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "60km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "0km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "0km/s"},
        "n2hp": {"cubewidth": "60km/s"},
    },
    "G012.80": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "60km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "35km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "35km/s"},
    },
    "G327.29": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "70km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-40km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-40km/s"},
    },
    "G328.25": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "70km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-37km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-37km/s"},
    },
    "G333.60": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "60km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-44km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-44km/s"},
    },
    "G337.92": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-36km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-36km/s"},
    },
    "G338.93": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "60km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-63km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-63km/s"},
        "sio": {"cubewidth": "120km/s"},
    },
    "G351.77": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "70km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-3.0km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-3.0km/s"},
    },
    "G353.41": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "-17km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "-17km/s"},
        "n2hp": {"cubewidth": "32km/s"},
    },
    "W43-MM1": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "100km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "100km/s"},
    },
    "W43-MM2": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "103km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "103km/s"},
        "sio": {"cubewidth": "100km/s", "vlsr": "91km/s", "width": "0.37km/s"},
        "13cs_2-1": {"cubewidth": "20km/s"},
    },
    "W43-MM3": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "90km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "90km/s"},
        "sio": {"cubewidth": "100km/s", "vlsr": "93km/s", "width": "0.37km/s"},
    },
    "W51-E": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "59km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "59km/s"},
        "n2hp": {"cubewidth": "60km/s"},
        "sio": {"cubewidth": "120km/s"},
    },
    "W51-IRS2": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "70km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "120km/s", "vlsr": "56km/s"},
        "h30a": {"cubewidth": "120km/s", "vlsr": "56km/s"},
        "sio": {"cubewidth": "120km/s"},
    },
}

for field in line_parameters_custom:
    for line in line_parameters_custom[field]:
        line_parameters[field][line].update(line_parameters_custom[field][line])
