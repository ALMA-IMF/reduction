"""
"table" of automasking parameters from
https://casaguides.nrao.edu/index.php/Automasking_Guide
"""

continuum = {"12m_short": {"sidelobethreshold": 2.0, "noisethreshold": 4.25, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 0.0},
             "12m_long": {"sidelobethreshold": 3.0, "noisethreshold": 5.00, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 0.0},
             "7m": {"sidelobethreshold": 1.25, "noisethreshold": 5.00, "minbeamfrac": 0.1, "lownoisethreshold": 2.0, "negativethreshold": 0.0},
             "7m12m": {"sidelobethreshold": 2.0, "noisethreshold": 4.25, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 0.0},
            }

line = {"12m_short": {"sidelobethreshold": 2.0, "noisethreshold": 4.25, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 15.0},
        "12m_long": {"sidelobethreshold": 3.0, "noisethreshold": 5.00, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 7.0},
        "7m": {"sidelobethreshold": 1.25, "noisethreshold": 5.00, "minbeamfrac": 0.1, "lownoisethreshold": 2.0, "negativethreshold": 0.0},
        "7m12m": {"sidelobethreshold": 2.0, "noisethreshold": 4.25, "minbeamfrac": 0.3, "lownoisethreshold": 1.5, "negativethreshold": 0.0},
       }
