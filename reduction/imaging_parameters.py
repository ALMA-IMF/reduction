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
from astropy import units as u

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
        "threshold": {0: "0.8mJy", 1: "0.8mJy", 2: "0.4mJy", 3: "0.2mJy", 4: "0.1mJy", 5: "0.07mJy", 6: "0.07mJy"},
        "niter": {0: 3000, 1: 3000, 2: 10000, 3: 30000, 4: 90000, 5: 90000, 6: 90000},
        "maskname": {
            0: "mask_G333_B3_12m_0.1.crtf",
            1: "mask_G333_B3_12m_0.1.crtf",
            2: "mask_G333_B3_12m_0.03.crtf",
            3: "mask_G333_B3_12m_0.01.crtf",
            4: "mask_G333_B3_12m_0.003.crtf",
            5: "mask_G333_B3_12m_0.0015.crtf",
            6: "mask_G333_B3_12m_0.0015.crtf",
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
            6: "0.15 mJy",
            "final": "0.15 mJy",
        },
        "niter": {0: 3000, 1: 3000, 2: 6000, 3: 12000, 4: 24000, 5: 48000, 6: 70000, "final": 70000},
        "maskname": {
            0: "mask_G333_B6_12m_0.1.crtf",
            1: "mask_G333_B6_12m_0.1.crtf",
            2: "mask_G333_B6_12m_0.03.crtf",
            3: "mask_G333_B6_12m_0.03.crtf",
            4: "mask_G333_B6_12m_0.01.crtf",
            5: "mask_G333_B6_12m_0.01.crtf",
            6: "mask_G333_B6_12m_final.crtf",
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
        "threshold": {
            0: "10.0mJy",
            1: "10mJy",
            2: "5mJy",
            3: "3mJy",
            4: "1mJy",
            5: "0.25mJy",
            6: "0.25mJy",
            7: "0.25mJy",
        },
        "niter": {0: 500, 1: 100, 2: 1000, 3: 3000, 4: 5000, 5: 7000, 6: 7000, 7: 7000},
    },
    "G012.80_B6_12M_robust0": {
        "threshold": {0: "3.0mJy", 1: "2mJy", 2: "1.5mJy", 3: "1mJy", 4: "1mJy", 5: "0.25mJy", 6: "0.25mJy"},
        "niter": {0: 500, 1: 1500, 2: 3000, 3: 5000, 4: 15000, 5: 30000, 6: 30000},
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
            9: "0.2mJy",
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
        "scales": {
            0: [0, 3, 9, 27],
            1: [3, 9, 27],  # force larger scales to avoid pointillism in northern HII region
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            5: [0, 3, 9, 27],
            6: [0, 3, 9, 27],
            7: [0, 3, 9, 27],
        },
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
    "W43-MM1_B6_12M_robust0": {
        "threshold": {0: "10.0mJy", 1: "10.0mJy", 2: "8mJy", 3: "5mJy", 4: "3mJy", "final": "1mJy"},
        "niter": {0: 1000, 1: 5000, 2: 5000, 3: 5000, 4: 5000, "final": 10000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 54],
        },
        "maskname": {
            0: "W43-MM1_B6_dirty_12M.crtf",
            1: "W43-MM1_B6_early-iter_12M.crtf",
            2: "W43-MM1_B6_early-iter_12M.crtf",
            3: "W43-MM1_B6_late-iter_12M.crtf",
            4: "W43-MM1_B6_last-iter_12M.crtf",
            "final": "W43-MM1_B6_final_12M.crtf",
        },
    },
    "W43-MM1_B6_12M_robust0_bsens": {
        "threshold": {0: "10.0mJy", 1: "10.0mJy", 2: "8mJy", 3: "5mJy", 4: "3mJy", "final": "1mJy"},
        "niter": {0: 1000, 1: 5000, 2: 5000, 3: 5000, 4: 5000, "final": 10000},
        "scales": {
            0: [0, 3, 9, 27],
            1: [0, 3, 9, 27],
            2: [0, 3, 9, 27],
            3: [0, 3, 9, 27],
            4: [0, 3, 9, 27],
            "final": [0, 3, 9, 27, 54],
        },
        "maskname": {
            0: "W43-MM1_B6_dirty_12M.crtf",
            1: "W43-MM1_B6_early-iter_12M.crtf",
            2: "W43-MM1_B6_early-iter_12M.crtf",
            3: "W43-MM1_B6_late-iter_12M.crtf",
            4: "W43-MM1_B6_last-iter_12M.crtf",
            "final": "W43-MM1_B6_final_12M.crtf",
        },
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
            7: "0.25mJy",
            8: "0.25mJy",
            9: "0.25mJy",
        },
        "niter": {0: 700, 1: 1300, 2: 2500, 3: 5000, 4: 10000, 5: 10000, 6: 15000, 7: 15000, 8: 15000, 9: 15000},
        "maskname": {
            0: "G010.62_centralBox_50_30.crtf",
            1: "G010.62_B3_50mJy.crtf",
            2: "G010.62_B3_15mJy.crtf",
            3: "G010.62_B3_05mJy.crtf",
            4: "G010.62_B3_03mJy.crtf",
            5: "G010.62_B3_01mJy.crtf",
            6: "G010.62_B3_iter6.crtf",
            7: "G010.62_B3_iter7.crtf",
            8: "G010.62_B3_iter7.crtf",
            9: "G010.62_B3_iter7.crtf",
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
        7: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        8: {"calmode": "ap", "gaintype": "T", "solint": "inf", "solnorm": False},
        9: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
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
        5: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
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
        6: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        7: {"calmode": "a", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
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
        6: {"calmode": "ap", "gaintype": "G", "minsnr": 5, "solint": "inf", "solnorm": False},
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
        5: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        6: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
        5: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        6: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_7M12M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_7M12M_robust0": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "gaintype": "T", "solint": "int", "solnorm": False},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_7M12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B3_7M_robust-2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
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
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B6_12M_robust0": {
        1: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
        2: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "15s", "solnorm": False},
        3: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "5s", "solnorm": False},
        4: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "int", "solnorm": False},
        5: {"calmode": "p", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
        6: {"calmode": "a", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
    },
    "G333.60_B6_12M_robust2": {
        1: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        2: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        3: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        4: {"calmode": "p", "gaintype": "T", "solint": "inf", "solnorm": True},
        5: {"calmode": "a", "gaintype": "T", "solint": "inf", "solnorm": False},
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
        5: {"calmode": "a", "combine": "spw", "gaintype": "T", "solint": "inf", "solnorm": False},
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
        8: {"calmode": "p", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
        9: {"calmode": "a", "gaintype": "T", "minsnr": 5, "solint": "inf", "solnorm": False},
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
        "weighting": "briggsbwtaper",
        "deconvolver": "multiscale",
        "scales": [0, 5, 15],
        "smallscalebias": 0.5,
        "gridder": "mosaic",
        "specmode": "cube",
        "outframe": "LSRK",
        "veltype": "radio",
        "usemask": "pb",
        "pblimit": 0.05,
        "pbmask": 0.1,
        "perchanweightdensity": True,
        "interactive": 0,  # returns a dict (False doesn't...)
        "mask_out_endchannels": 2,  # this may be something to remove, it continually confuses people.
        "cyclefactor": 2.0,  # higher cyclefactor = more major cycles
    }
    for field in allfields
    for band in ("B3", "B6")
    for array in ("12M", "7M12M", "7M")
    for robust in (-2, 0, 2)
    for contsub in ("", "_contsub")
}


for key in list(line_imaging_parameters_default.keys()):
    if "7M12M" in key:
        line_imaging_parameters_default[key]["scales"] = [0, 5, 15, 45]
        line_imaging_parameters_default[key]["threshold"] = "10sigma"
        line_imaging_parameters_default[key]["niter"] = 5000
        # TODO: change pblimit?
    if "B6" in key:
        # set defaults for 12CO to have higher cyclefactor and higher threshold (12CO is scary)
        line_imaging_parameters_default[key + "_12co"] = {}
        line_imaging_parameters_default[key + "_12co"].update(line_imaging_parameters_default[key])
        line_imaging_parameters_default[key + "_12co"]["cyclefactor"] = 3.0
        line_imaging_parameters_default[key + "_12co"]["threshold"] = "5sigma"
        # spw5 is the 12CO SPW
        line_imaging_parameters_default[key + "_spw5"] = {}
        line_imaging_parameters_default[key + "_spw5"].update(line_imaging_parameters_default[key])
        line_imaging_parameters_default[key + "_spw5"]["cyclefactor"] = 3.0
        line_imaging_parameters_default[key + "_spw5"]["threshold"] = "5sigma"


line_imaging_parameters = copy.deepcopy(line_imaging_parameters_default)

line_imaging_parameters_custom = {
    "G008.67_B3_12M_robust0": {
        "threshold": "8mJy",
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B3_12M_robust0_h41a": {
        "threshold": "8.5mJy",  # noise ~ 2.5mJy in channels off line peak.
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 5, 10, 20, 40],  # 4.9pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 4.4 arcsec
        "gain": 0.08,
    },
    "G008.67_B6_12M_robust0": {
        "threshold": "33mJy",  # "28mJy",#estimated noise: 9-11 mJy, from sio-only cube
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_sio": {
        "threshold": "33mJy",  # typical rms is 9-11 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G010.62_B3_12M_robust0_h41a": {
        "threshold": "8mJy",  # noise ~ 2mJy in channels off line peak.
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32],  # 3.5pix per sqrt(bmaj*bmean), pix=0.14 arcsec, max scale ~ 4.5 arcsec
        "gain": 0.08,
    },
    "G010.62_B6_12M_robust0": {
        "threshold": "30mJy",  # estimated noise: 2.8-3.2 mJy, from sio-only cube.  ~5 to 6 mJy, from full cube spw4.  bumped to 5-sigma
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
        "perchanweightdensity": True,  # change Mar 12, 2021, based on some old suggestions from Ryan Loomis and Jan-Willem Steeb
    },
    "G010.62_B6_12M_robust0_sio": {
        "threshold": "9.6mJy",  # typical rms is 2.8-3.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G012.80_B3_12M_robust0": {
        "threshold": "18mJy",  # ~2-sigma
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G012.80_B3_12M_robust0_h41a": {
        "threshold": "16mJy",  # noise ~ 4.0mJy in channels off line peak.
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 5, 10, 20],  # 5pix per sqrt(bmaj*bmean), pix=0.35 arcsec, max scale ~ 7 arcsec
        "gain": 0.08,
    },
    "G012.80_B6_12M_robust0": {
        "threshold": "39mJy",  # "24mJy", #estimated noise: 13 mJy, from sio-only cube
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_sio": {
        "threshold": "39mJy",  # typical rms values are 10-13 mJy, using 3sigma as threshold (14 Dec. 2020)
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G327.29_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B3_12M_robust0_h41a": {
        "threshold": "8.5mJy",  # noise ~ 2.5mJy in channels off line peak.
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.9pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 7 arcsec
        "gain": 0.08,
    },
    "G327.29_B6_12M_robust0": {
        "threshold": "34.5mJy",  # "6mJy", #estimated noise: 9.5-11.5 mJy, from sio-only cube
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_sio": {
        "threshold": "50mJy",  # typical rms is 10-12.5 mJy, using 5sigma of lowest value for threshold (22 October 2021)
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G328.25_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B3_12M_robust0_h41a": {
        "threshold": "14mJy",  # noise ~ 3.5mJy in channels off line peak.
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 5, 10, 20, 40],  # 5.6pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 4.4 arcsec
        "gain": 0.08,
    },
    "G328.25_B6_12M_robust0": {
        "threshold": "63mJy",  # "6mJy", #estimated noise: 15-21 mJy, from sio-only cube
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_sio": {
        "threshold": "90mJy",  # typical rms is 18-22 mJy, using 5sigma of 18 mJy for threshold (03 November 2021)
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G333.60_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B3_12M_robust0_h41a": {
        "threshold": "8mJy",  # noise ~ 2mJy in channels off line peak.
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 4.6pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 7arcsec
        "gain": 0.08,
    },
    "G333.60_B6_12M_robust0": {
        "threshold": "15.6mJy",  # "6mJy",#estimated noise: 4.3-5.2 mJy, from sio-only cube
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_sio": {
        "threshold": "10.4mJy",  # typical rms is 4.3-5.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G337.92_B3_12M_robust0": {
        "threshold": "5mJy",
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B3_12M_robust0_h41a": {
        "threshold": "9mJy",  # noise ~ 2mJy in channels off line peak.
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.7pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 7arcsec
        "gain": 0.08,
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
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B3_12M_robust0_h41a": {
        "threshold": "10mJy",  # noise ~ 2mJy in channels off line peak.
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32],  # 4.2pix per sqrt(bmaj*bmean), pix=0.11 arcsec, max scale ~ 3.5arcsec
        "gain": 0.08,
    },
    "G338.93_B3_12M_robust0_n2hp": {
        "threshold": "5mJy",
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B6_12M_robust0": {
        "threshold": "18mJy",  # "6mJy", #estimated noise: 5-6 mJy, from sio-only cube
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_sio": {
        "threshold": "22.5mJy",  # rms is 4.5-5.5 mJy, using 5sigma for threshold (02 Nov 2021)
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
        # This mask is not available
        # "usemask": "user",
        # "mask": "G338.93_B6_spw1_12M_sio.image_2sigma_e2_d8.mask",
    },
    "G351.77_B3_12M_robust0": {
        "threshold": "30mJy",
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B3_12M_robust0_h41a": {
        "threshold": "16mJy",  # noise ~ 4mJy in channels off line peak.
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 5, 10, 20],  # 5pix per sqrt(bmaj*bmean), pix=0.35 arcsec, max scale ~7arcsec
        "gain": 0.08,
    },
    "G351.77_B6_12M_robust0": {
        "threshold": "80mJy",  # "6mJy",#estimated noise: 12-16 mJy, from sio-only cube
        "perchanweightdensity": True,
        "smallscalebias": 0.5,  # bias toward smaller scales; the large scales cause divergence
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_sio": {
        "threshold": "60mJy",  # typical rms is 12-16 mJy, using 5sigma for threshold (02 Nov 2021)
        "cyclefactor": 2.0,
        "interactive": 0,
        "fastnoise": False,
        # "nsigma": 3,
        "smallscalebias": 0.5,  # bias toward smaller scales; the large scales cause divergence
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G353.41_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B3_12M_robust0_h41a": {
        "threshold": "14mJy",  # noise ~4mJy in channels off line peak.
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 5, 10, 20],  # 4.8pix per sqrt(bmaj*bmean), pix= 0.35arcsec, max scale ~7arcsec
        "gain": 0.08,
    },
    "G353.41_B3_7M12M_robust0": {
        "niter": 5000000,
        "threshold": "2sigma",
        "deconvolver": "multiscale",
        "scales": [0, 6, 12, 24],
        "pblimit": 0.18,
        "pbmask": 0.1,
        "cyclefactor": 2.0,
    },
    "G353.41_B6_12M_robust0": {
        "threshold": "48mJy",  # "6mJy", #estimated noise: 12.5-16 mJy, from sio-only cube
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_sio": {
        "threshold": "48mJy",  # typical rms is 12.5-16 mJy, using 3sigma for threshold (14 Dec. 2020)
        "cyclefactor": 2.0,
        "interactive": 0,
        "fastnoise": False,
        # "nsigma": 3,
        "smallscalebias": 0.5,  # bias toward smaller scales; the large scales cause divergence
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "W43-MM1_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM1_B3_12M_robust0_h41a": {
        "threshold": "3.5mJy",  # noise ~1mJy in channels off line peak.
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32],  # 4.1pix per sqrt(bmaj*bmean), pix= 0.11arcsec, max scale ~3.5arcsec
        "gain": 0.08,
    },
    # W43-MM1 SiO 12m-only threshold: 15mJy (5 sigma of rms, rms is 3.0-3.7 mJy)
    "W43-MM2_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_h41a": {
        "threshold": "4mJy",  # noise ~1mJy in channels off line peak.
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.7pix per sqrt(bmaj*bmean), pix= 0.08arcsec, max scale ~5.1arcsec
        "gain": 0.08,
    },
    "W43-MM2_B3_12M_robust0_13cs_2-1": {
        "threshold": "3mJy",  # sigma in brighter channel ~ 1mJy
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 12, 36],  # >~ 4 pixels per bmaj, not too extended emission
    },
    "W43-MM2_B3_12M_robust0_13cs_2-1_contsub": {"threshold": "4mJy", "deconvolver": "multiscale", "scales": [0, 4, 13]},
    "W43-MM2_B3_12M_robust0_h2cs_322-221": {
        "threshold": "3.5mJy",  # sigma in brighter channel ~ 1mJy
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 12, 36],  # 4 pixels per bmaj, not too extended emission
    },
    "W43-MM2_B3_12M_robust0_h2cs_312-211": {
        "threshold": "4mJy",  # sigma in brighter channel ~ 1.3mJy
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 12, 36],  # 4 pixels per bmaj, not too extended emission
    },
    "W43-MM2_B6_12M_robust0": {
        "threshold": "8.1mJy",  # "6mJy", #estimated noise: 2.7 mJy, from sio-only cube
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [1372, 1372],
    },
    "W43-MM2_B6_12M_robust0_12co": {
        "threshold": "8.5mJy",  # sig 1.5-2 mJy
        "scales": [0, 6, 18, 54],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [1372, 1372],
        # "usemask": "pb",
        # "mask": "imaging_results/W43-MM2_B6_spw5_12M_12co_multi_2.5sigma_e2_d5.mask"
    },
    "W43-MM2_B6_12M_robust0_sio": {
        "threshold": "10mJy",  # rms is 2-3 mJy, using 5 sigma (02 Nov 2021)
        "deconvolver": "multiscale",
        "scales": [0, 6, 18, 36],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [1372, 1372],
    },
    "W43-MM2_B6_12M_robust0_contsub": {
        "threshold": "8.5mJy",
        "deconvolver": "multiscale",
        "scales": [0, 6, 18, 36],
        "imsize": [1372, 1372],
    },
    "W43-MM2_B6_7M12M_robust0": {
        "threshold": "13mJy",
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "pbmask": 0.2,
        "imsize": [1372, 1372],
    },
    "W43-MM2_B6_7M12M_robust2": {
        "threshold": "13mJy",
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "pbmask": 0.2,
        "imsize": [1372, 1372],
    },
    "W43-MM2_B6_12M_robust0_c18o": {
        "threshold": "17.5mJy",  # sigma in empty channel ~ 5mJy
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 7, 22, 67],  # 7.5 pixels per beam, extended emission
        "imsize": [1500, 1500],  # automatic imsize was too small
    },
    "W43-MM2_B6_12M_robust0_ocs_19-18": {
        "threshold": "8.4mJy",
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 7, 21],
        "imsize": [1344, 1344],
    },
    "W43-MM2_B6_12M_robust0_oc33s_18-17": {
        "threshold": "9mJy",  # sigma ~ 2.8mJy
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 7, 21, 63],  # 7 pixels per sqrt(bmaj*bmin), not too extended emission
        "imsize": [1500, 1500],  # automatic imsize was too small
    },
    "W43-MM2_B6_12M_robust0_13cs_5-4": {
        "threshold": "8.4mJy",  # sigma ~ 2.8mJy
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 7, 21],  # 7 pixels per bmaj, not too extended emission
    },
    "W43-MM2_B6_12M_robust0_so_6-5": {
        "threshold": "11.5mJy",  # sigma  ~ 3.8 mJy in bright channel
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 7, 22, 67],  # 7 pixels per sqrt(bmaj*bmin), extended emission
        "imsize": [1500, 1500],  # automatic imsize was too small
    },
    "W43-MM3_B3_12M_robust0": {
        "threshold": "6mJy",
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0_h41a": {
        "threshold": "4mJy",  # noise ~1mJy in channels off line peak.
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.6pix per sqrt(bmaj*bmean), pix= 0.11arcsec, max scale ~7arcsec
        "gain": 0.08,
    },
    "W43-MM3_B6_12M_robust0": {
        "threshold": "10mJy",
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [960, 960],
    },
    "W43-MM3_B6_12M_robust0_12co": {
        "threshold": "6mJy",  # estimated noise: 2 mJy
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [960, 960],
        "deconvolver": "multiscale",
        "scales": [0, 4, 12, 24],
    },
    "W43-MM3_B6_12M_robust0_sio": {
        "threshold": "13mJy",  # typical rms is 2.6-3.3 mJy, using 5 sigma (02 Nov 2021)
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
        "imsize": [960, 960],
        "deconvolver": "multiscale",
        "scales": [0, 4, 12],
    },
    "W51-E_B3_12M_robust0": {
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
        "threshold": "4mJy",  # sigma is ~0.8 mJy
        "pblimit": 0.05,  # per Nov 6 telecon
    },
    "W51-E_B3_12M_robust0_h41a": {
        "threshold": "6mJy",  # noise ~1mJy in channels off line peak.
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.8pix per sqrt(bmaj*bmean), pix= 0.08arcsec, max scale ~5arcsec
        "gain": 0.08,
    },
    "W51-E_B6_12M_robust0": {
        "pblimit": 0.1,
        "threshold": "16mJy",  # sigma is ~ 4 mJy  (from sio cube, noise is 3.3-4.1 mJy)
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_sio": {
        "threshold": "16.5mJy",  # typical rms is 3.3-3.9 mJy, using 5sigma for threshold (02 Nov 2021)
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
    "W51-IRS2_B3_12M_robust0_h41a": {
        "threshold": "4mJy",  # noise ~1mJy in channels off line peak.
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
        "deconvolver": "multiscale",
        "scales": [0, 4, 8, 16, 32, 64],  # 3.8pix per sqrt(bmaj*bmean), pix= 0.08arcsec, max scale ~5arcsec
        "gain": 0.08,
    },
    "W51-IRS2_B6_12M_robust0": {
        "threshold": "9.6mJy",  # "6mJy", #estimated noise: 3.2 mJy, from sio-only cube
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_sio": {
        "threshold": "6.4mJy",  # typical rms is 2.7-3.2 mJy, using 3sigma for threshold (14 Dec. 2020)
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G008.67_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 9, 18, 36, 54, 72, 90],
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G012.80_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 8, 16, 32],
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G327.29_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 8, 16, 32, 48, 64, 80, 96],
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G328.25_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 12, 24, 48, 72, 96],
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G333.60_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 9, 28, 85],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B3_7M12M_robust0_n2hp": {
        "threshold": "5sigma",
        "imsize": [4096, 4096],
        "cell": ["0.08arcsec", "0.08arcsec"],
        "scales": [0, 9, 28, 85],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G337.92_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 8, 16, 32, 48, 64, 80, 96],
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G338.93_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28, 42, 56, 70, 84, 98],
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G351.77_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28],
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G353.41_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28],
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "W43-MM1_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 36, 48, 60, 72, 84, 96],
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104],
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM3_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 36, 48, 60, 72, 84, 96],
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W51-E_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104],
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-IRS2_B3_12M_robust0_n2hp": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G008.67_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28, 56],
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G008.67_B3_uid___A001_X1296_X1c1_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G008.67_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G008.67_B6_uid___A001_X1296_X1b7_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G010.62_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G010.62_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G010.62_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "G010.62_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G010.62_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G010.62_B6_uid___A001_X1296_X1db_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G012.80_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G012.80_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G012.80_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G012.80_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G012.80_B3_uid___A001_X1296_X1fb_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "G012.80_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G012.80_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G012.80_B6_uid___A001_X1296_X1ef_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G327.29_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G327.29_B3_uid___A001_X1296_X17d_continuum_merged_12M_robust0_selfcal2_finaliter",
    },
    "G327.29_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G327.29_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G327.29_B6_uid___A001_X1296_X175_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "G328.25_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28, 56],
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G328.25_B3_uid___A001_X1296_X16d_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G328.25_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G328.25_B6_uid___A001_X1296_X163_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G333.60_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28, 56],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G333.60_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G333.60_B6_uid___A001_X1296_X19b_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G337.92_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G337.92_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G337.92_B6_uid___A001_X1296_X13b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G338.93_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B3_uid___A001_X1296_X159_continuum_merged_12M_robust0_selfcal3_finaliter",
    },
    "G338.93_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G338.93_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G351.77_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G351.77_B3_uid___A001_X1296_X209_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw0": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 4, 8, 16],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw1": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 4, 8, 16],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw2": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 4, 8, 16],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw3": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 4, 8, 16],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw4": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 4, 8, 16],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw5": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw6": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G351.77_B6_12M_robust0_spw7": {
        "threshold": "10sigma",
        "pblimit": 0.2,
        "pbmask": 0.25,
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G351.77_B6_uid___A001_X1296_X201_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "G353.41_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20],
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8],
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 5, 10],
        "startmodel": "G353.41_B3_uid___A001_X1296_X1d5_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "G353.41_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24],
        "startmodel": "G353.41_B6_uid___A001_X1296_X1c9_continuum_merged_12M_robust0_selfcal6_finaliter",
    },
    "W43-MM1_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM1_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM1_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM1_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM1_B3_uid___A001_X1296_X1af_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B3_uid___A001_X1296_X11b_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 5, 10, 20, 40],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 7, 14, 28, 56],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM2_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 6, 12, 24, 48],
        "startmodel": "W43-MM2_B6_uid___A001_X1296_X113_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W43-MM3_B3_uid___A001_X1296_X12f_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W43-MM3_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W43-MM3_B6_uid___A001_X1296_X129_continuum_merged_12M_robust0_selfcal5_finaliter",
    },
    "W51-E_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-E_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0_selfcal7_finaliter",
    },
    "W51-IRS2_B3_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W51-IRS2_B3_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32, 64],
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W51-IRS2_B3_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W51-IRS2_B3_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 3, 6, 12, 24, 48],
        "startmodel": "W51-IRS2_B3_uid___A001_X1296_X18f_continuum_merged_12M_robust0_selfcal4_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw0": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw1": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw2": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw3": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw4": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw5": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw6": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
    "W51-IRS2_B6_12M_robust0_spw7": {
        "threshold": "5sigma",
        "scales": [0, 4, 8, 16, 32],
        "startmodel": "W51-IRS2_B6_uid___A001_X1296_X187_continuum_merged_12M_robust0_selfcal9_finaliter",
    },
}


default_lines = {
    "h41a": "92.034434GHz",
    "ch3cnv8=1": "92.26144GHz",
    "ch3cn": "91.97GHz",  # range from 91.987 to 91.567
    "13cs_2-1": "92.49430800GHz",
    "n2hp": "93.173700GHz",
    "ch3cch_62-52": "102.547983GHz",
    "h2cs_322-221": "103.039927GHz",
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

for key in line_imaging_parameters_custom:
    if key in line_imaging_parameters:
        line_imaging_parameters[key].update(line_imaging_parameters_custom[key])
    else:
        # loop over known lines _plus_ spws
        for linename in tuple(default_lines.keys()) + tuple("spw" + str(ii) for ii in range(7)):
            if linename in key:
                key_noline = key.replace("_" + linename, "")
                line_imaging_parameters[key] = copy.copy(line_imaging_parameters_default[key_noline])
                line_imaging_parameters[key].update(line_imaging_parameters_custom[key])

field_vlsr = {
    "W51-E": "55km/s",
    "W51-IRS2": "55km/s",
    "G010.62": "-2km/s",
    "G353.41": "-18km/s",
    "W43-MM1": "97km/s",
    "W43-MM2": "90km/s",
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
        line: {
            "restfreq": freq,
            "vlsr": field_vlsr[field],
            "cubewidth": "50km/s",
            "band": "B3" if u.Quantity(freq) < 115 * u.GHz else "B6",
        }
        for line, freq in default_lines.items()
    }
    for field in allfields
}
for field in allfields:
    line_parameters_default[field]["12co"]["cubewidth"] = "150km/s"
    # a hack for spw5, which contains 12CO and needs to be special-cased
    # This is tricky, though, as it breaks the generalization: spw5 is lucky in that there is no B3 SPW5!
    # If there were, this would not work and would be a little disastrous.
    # The only fix is to add a "band" specification ...
    line_parameters_default[field]["spw5"] = {
        "restfreq": line_parameters_default[field]["12co"]["restfreq"],
        "vlsr": line_parameters_default[field]["12co"]["vlsr"],
        "band": "B6",
    }
    line_parameters_default[field]["ch3cnv8=1"]["cubewidth"] = "150km/s"  # is 150 wide enough?
    line_parameters_default[field]["ch3cn"]["cubewidth"] = "150km/s"  # is 150 wide enough?
line_parameters = copy.deepcopy(line_parameters_default)

line_parameters_custom = {
    "G008.67": {
        "spw5": {"mask-ranges": [(20, 34)]},  # km/s units
        "12co": {"cubewidth": "150km/s", "mask-ranges": [(20, 34)]},  # km/s units
        "sio": {"cubewidth": "150km/s", "vlsr": "35km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-22km/s"},  # 43 - 65 = -22km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "44km/s"},
    },
    "G010.62": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-66km/s"},  # -1 - 65 = -66km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "0km/s"},
        "n2hp": {"cubewidth": "60km/s"},
    },
    "G012.80": {
        "spw5": {"mask-ranges": [(31, 36)]},  # km/s units
        "12co": {"cubewidth": "150km/s", "mask-ranges": [(31, 36)]},  # km/s units
        "sio": {"cubewidth": "150km/s", "vlsr": "35.5km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-29km/s"},  # 36 - 65 = -29km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "35km/s"},
    },
    "G327.29": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "150km/s", "vlsr": "-43km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-105km/s"},  # -40 - 65 = -105km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-40km/s"},
    },
    "G328.25": {
        "spw5": {"mask-ranges": [(-48, -51)]},  # km/s units
        "12co": {"cubewidth": "150km/s", "mask-ranges": [(-48, -51)]},  # km/s units
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-108km/s"},  # -43 - 65 = -108km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-43km/s"},
    },
    "G333.60": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "150km/s", "vlsr": "-48km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-110km/s"},  # -45 - 65 = -110km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-45km/s"},
    },
    "G337.92": {
        "sio": {"cubewidth": "150km/s", "vlsr": "-39km/s"},
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-100km/s"},  # -35 - 65 = -100km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-35km/s"},
    },
    "G338.93": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-127km/s"},  # -62 - 65 = -127km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-62km/s"},
        "sio": {"cubewidth": "120km/s"},
    },
    "G351.77": {
        "spw5": {"mask-ranges": [(-11, -2), (-27, -17), (-32, -31)]},  # km/s units
        "12co": {"cubewidth": "150km/s", "mask-ranges": [(-11, -2), (-27, -17), (-32, -31)]},  # km/s units
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-67km/s"},  # -2 - 65 = -67km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-2km/s"},
    },
    "G353.41": {
        "spw5": {"mask-ranges": [(-27, -20)]},  # km/s units
        "12co": {"cubewidth": "150km/s", "mask-ranges": [(-27, -20)]},  # km/s units
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-81km/s"},  # -16 - 65 = -81km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "-16km/s"},
        "n2hp": {"cubewidth": "50km/s"},
    },
    "W43-MM1": {
        "12co": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "35km/s"},  # 100 - 65 = 35km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "100km/s"},
    },
    "W43-MM2": {
        "sio": {"cubewidth": "240km/s", "vlsr": "91km/s", "width": "0.37km/s"},
        "12co": {"cubewidth": "240km/s", "vlsr": "91km/s"},
        # "12co": {"cubewidth": "240km/s", "vlsr": "91km/s", "width": "2km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "35km/s"},  # 100 - 65 = 35km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "100km/s"},
        "c18o": {"cubewidth": "80km/s"},
    },
    "W43-MM3": {
        "sio": {"cubewidth": "190km/s", "vlsr": "93km/s", "width": "0.37km/s"},
        "12co": {"cubewidth": "190km/s", "vlsr": "93km/s"},
        # "12co": {"cubewidth": "190km/s", "vlsr": "93km/s", "width": "2km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "25km/s"},  # 90 - 65 = 25km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "90km/s"},
    },
    "W51-E": {
        "12co": {"cubewidth": "150km/s"},
        "sio": {"cubewidth": "150km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-6km/s"},  # 59 - 65 = -6km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "59km/s"},
        "n2hp": {"cubewidth": "60km/s"},
    },
    "W51-IRS2": {
        "12co": {"cubewidth": "150km/s"},
        "n2hp": {"cubewidth": "80km/s"},
        "sio": {"cubewidth": "150km/s", "vlsr": "60km/s"},
        "ch3cnv8=1": {"cubewidth": "150km/s"},
        "h41a": {"cubewidth": "270km/s", "vlsr": "-9km/s"},  # 56 - 65 = -9km/s to accomodate He and C.
        "h30a": {"cubewidth": "120km/s", "vlsr": "56km/s"},
    },
}

for field in line_parameters_custom:
    for line in line_parameters_custom[field]:
        line_parameters[field][line].update(line_parameters_custom[field][line])


# Define the maximum number of channels that can be flagged out
# nchan = number of channels
# tolerance = fraction of baselines
# If both nchan & tolerance pass, the imaging will be done
# The convention here is to put both nchan and tolerance just above
# that level so we have a record of how much data is lost
spws = {"B3": ["spw" + str(spw) for spw in [1, 2, 3, 4]], "B6": ["spw" + str(spw) for spw in [1, 2, 3, 4, 5, 6, 7]]}
flag_thresholds_default = {
    "{0}_{1}_{2}_{3}".format(field, band, array, spw): {"nchan": 10, "tolerance": 0.01}
    for field in allfields
    for band in ("B3", "B6")
    for spw in spws[band]
    for array in ("12M", "7M12M", "7M")
}

flag_thresholds_custom = {
    "G012.80_B3_12M_spw0": {"nchan": 20, "tolerance": 0.31},
    "G353.41_B3_12M_spw0": {"nchan": 28, "tolerance": 0.23},
    "G353.41_B3_7M12M_spw0": {"nchan": 28, "tolerance": 0.23},
    "G353.41_B6_12M_spw5": {"nchan": 102, "tolerance": 0.23},  # first 100 channels
    "G337.92_B6_12M_spw7": {"nchan": 51, "tolerance": 1.00},  # maxdiff is ~6x!
    "W51-E_B6_12M_spw3": {"nchan": 18, "tolerance": 2.25},
    "W51-E_B6_12M_spw5": {"nchan": 18, "tolerance": 2.25},
    "W51-E_B6_12M_spw6": {"nchan": 41, "tolerance": 0.25},
    "W51-E_B6_12M_spw7": {"nchan": 51, "tolerance": 0.25},  # again 51 channels in spw7
    "W43-MM2_B6_12M_spw6": {"nchan": 142, "tolerance": 0.01},  # 141 chan with 0.97x diff
    "W43-MM2_B6_12M_spw7": {"nchan": 202, "tolerance": 0.02},  # 201 channels with 1.96x diff?
    "W43-MM3_B6_12M_spw6": {"nchan": 141, "tolerance": 0.01},  # 201 above 1.92x
    "W43-MM3_B6_12M_spw7": {"nchan": 172, "tolerance": 0.02},  # 171 above 0.89x
    "G010.62_B6_12M_spw5": {"nchan": 332, "tolerance": 0.01},  # there are several discrepant EBs.  331 is a LOT.
}
flag_thresholds = flag_thresholds_default.copy()
flag_thresholds.update(flag_thresholds_custom)
