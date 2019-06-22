"""
Pipeline Running Script
-----------------------

This script is intended to run in the 2017.1.01355.L directory, i.e., the
parent directory of all sous/gous/mous/<project stuff> subdirectories extracted
from the ALMA tarballs.

The script will traverse all subdirectories searching for `scriptForPI.py` files
and will run them if no corresponding `calibrated` directory exists.  If the
calibrated directory exists, the pipeline run will be skipped.

"""
import os
import runpy
from taskinit import casalog

# to do diagnostic plotting, we need the MS, not just the science-only calibrated MS
SPACESAVING = 1
DOSPLIT = True

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if "scriptForPI.py" == fn[-14:]:
            curdir = os.getcwd()

            if os.path.exists(os.path.join(dirpath,'../calibrated')):
                casalog.post("Skipping script {0} in {1} because calibrated exists".format(fn, dirpath),
                             origin='pipeline_runner')
            elif os.path.exists(os.path.join(dirpath,'../calibration')):
                os.chdir(dirpath)

                casalog.post("Running script {0} in {1}".format(fn, dirpath),
                             origin='pipeline_runner')

                runpy.run_path(fn, init_globals=globals())

                casalog.post("Done running script {0} in {1}".format(fn, dirpath),
                             origin='pipeline_runner')

                os.chdir(curdir)
            else:
                raise ValueError("Landed in the wrong directory.")
