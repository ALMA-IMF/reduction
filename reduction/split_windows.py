"""
Find all .split.cal files in the current directory and subdirectories, and split
each out into one MS per spectral window.  Also, dump metadata files that will
instruct the imaging script how to merge these single-window MSes into a final
cube.

.split.cal files are produced by running the CASA pipeline with ``DOSPLIT=True``.
If you ran the pipeline _without_ that flag, you can still use this script, but
you must first symbolically link the calibrated .ms files to the same filename
with .split.cal appended, e.g.:

    $ ln -s my_calibrated_measurement_set.ms my_calibrated_measurement_set.ms.split.cal

In order to run this code, you need to be able to import ``parse_contdotdat``,
which means to need to add the directory that contains that file to your path.
You can do this in two ways

    (1) In python:
        import sys
        sys.path.append('/path/that/contains/this/file/')
    (2) From the command line (if you're using a BASH-like shell):
        export ALMAIMF_ROOTDIR='/path/that/contains/this/file/'

   cd to the directory containing the untarred data (i.e., 2017.1.01355.L)

   Start CASA, then run this file with (DO NOT copy and paste!):
       >>> %run -i ./path/to/reduction/split_windows.py

You can set the following environmental variables for this script:
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only split
        fields with this name (e.g., "W43-MM1", "W51-E", etc.).
        Metadata will still be collected for *all* available MSes.


cont.dat files
--------------
By default, the ALMA-pipeline-derived cont.dat file will be used.  However, you
can specify an override by creating a file "{field}.{band}.cont.dat" in the
ALMAIMF_ROOTDIR directory.  For example, if you wanted to override the cont.dat
file for field "ORION" in band 9, you would create a file called
ORION.B9.cont.dat. Note that the names are case sensitive.
"""
import os
import time

import sys

import runpy

# If run from command line
if len(sys.argv) > 2:
    aux = os.path.dirname(sys.argv[2])
    if os.path.isdir(aux):
        almaimf_rootdir = aux


if 'almaimf_rootdir' in locals():
    os.environ['ALMAIMF_ROOTDIR'] = almaimf_rootdir
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


try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

scripts = [
           'assemble_split_metadata.py',
           'split_line_windows.py',
           'split_cont_windows.py',
          ]

for scriptname in scripts:
    t0 = time.time()
    fullpath = os.path.join(script_dir, scriptname)
    print("script={scriptname}, fullpath={fullpath}".format(scriptname=scriptname, fullpath=fullpath))
    try:
        runpy.run_path(fullpath, run_name="__main__")
    except Exception as ex:
        print(ex)
    print("script {scriptname} took ".format(scriptname=scriptname),
          (time.time() - t0)/3600," hours")
