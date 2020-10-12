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
import glob

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

rootdir = os.environ['ALMAIMF_ROOTDIR']

from metadata_tools import logprint

import shutil
import os

try:
    from taskinit import casalog
except ImportError:
    from casatasks import casalog

if os.getenv('LOGFILENAME'):
    casalog.setlogfile(os.path.join(os.getcwd(), os.getenv('LOGFILENAME')))
print("CASA log file name is {0}".format(casalog.logfile()))


runonce = bool(os.environ.get('RUNONCE'))

# to do diagnostic plotting, we need the MS, not just the science-only calibrated MS
SPACESAVING = 1
DOSPLIT = True

# only walk the science goal directories
science_goal_dirs = glob.glob("science_goal*")

for scigoal in science_goal_dirs:
    for group in glob.glob(scigoal+"/*"):
        for member in glob.glob(os.path.join(group, "*")):
            dirpath = member
            scriptsforpi = glob.glob(os.path.join(dirpath, "script/*scriptForPI.py"))

            if len(scriptsforpi) == 1:
                scriptforpi = scriptsforpi[0]
            elif len(scriptsforpi) > 1:
                raise ValueError("Too many scripts for PI in {0}".format(dirpath))
            elif len(scriptsforpi) == 0:
                logprint("Skipping directory {0} because it has no scriptForPI"
                         .format(dirpath))
                continue

            curdir = os.getcwd()

            if os.path.exists(os.path.join(dirpath, 'calibrated')):
                logprint("Skipping script {0} in {1} because calibrated "
                         "exists".format(scriptforpi, dirpath), origin='pipeline_runner')
            elif os.path.exists(os.path.join(dirpath, 'calibration')):
                os.chdir(os.path.join(dirpath, 'script'))

                # check for custom scripts
                sdms = glob.glob(os.path.join(dirpath, "raw/*.asdm.sdm"))
                # reset this each loop so we can search for the custom version
                local_scriptForPI = None
                for sdmfn in sdms:
                    sdm = sdmfn.split(".")[0]
                    # custom version has to follow this precise name scheme
                    scriptpath = ("{rootdir}/reduction/pipeline_scripts/{sdm}.ms.scriptForCalibration.py"
                                  .format(rootdir=rootdir, sdm=sdm))
                    if os.path.exists(scriptpath):
                        shutil.copy(scriptpath, '.')
                        local_scriptForPI = os.path.split(scriptpath)[-1]

                if local_scriptForPI is None:
                    local_scriptforPI = os.path.basename(scriptforpi)

                logprint("Running script {0} in {1}".format(local_scriptforPI, dirpath),
                         origin='pipeline_runner')

                result = runpy.run_path(local_scriptforPI, init_globals=globals())
                #logprint("result = {0}".format(result),
                #         origin='pipeline_runner')

                logprint("Done running script {0} in {1}".format(local_scriptforPI, dirpath),
                         origin='pipeline_runner')

                os.chdir(curdir)

                if runonce:
                    sys.exit(0)
            else:
                raise ValueError("Landed in the wrong directory.")

logprint("Completed run_pipeline.py")
