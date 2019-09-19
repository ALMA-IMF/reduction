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
import sys
import runpy

if os.getenv('ALMAIMF_ROOTDIR') is None:
    try:
        import metadata_tools
        os.environ['ALMAIMF_ROOTDIR'] = os.path.split(metadata_tools.__file__)[0]
    except ImportError:
        raise ValueError("metadata_tools not found on path; make sure to "
                         "specify ALMAIMF_ROOTDIR environment variable "
                         "or your PYTHONPATH variable to include the directory"
                         " containing the ALMAIMF code.")
else:
    sys.path.append(os.getenv('ALMAIMF_ROOTDIR'))

from metadata_tools import logprint


runonce = bool(os.environ.get('RUNONCE'))

# to do diagnostic plotting, we need the MS, not just the science-only calibrated MS
SPACESAVING = 1
DOSPLIT = True

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if "scriptForPI.py" == fn[-14:]:
            curdir = os.getcwd()

            if os.path.exists(os.path.join(dirpath,'../calibrated')):
                logprint("Skipping script {0} in {1} because calibrated "
                         "exists".format(fn, dirpath), origin='pipeline_runner')
            elif os.path.exists(os.path.join(dirpath,'../calibration')):
                os.chdir(dirpath)

                logprint("Running script {0} in {1}".format(fn, dirpath),
                         origin='pipeline_runner')

                result = runpy.run_path(fn, init_globals=globals())
                #logprint("result = {0}".format(result),
                #         origin='pipeline_runner')

                logprint("Done running script {0} in {1}".format(fn, dirpath),
                         origin='pipeline_runner')

                os.chdir(curdir)

                if runonce:
                    sys.exit(0)
            else:
                raise ValueError("Landed in the wrong directory.")
