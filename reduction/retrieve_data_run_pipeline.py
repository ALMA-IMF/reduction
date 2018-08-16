"""
Instructions:

    Run this script from within a casa-pipeline session, e.g., using casa
    --pipeline -r 5.1.0-74 on an NRAO lustre system, or just using the
    appropriate version of CASA elsewhere.  You'll then need to enter your ALMA
    archive username and password.

    The program will download the full set of raw data products and associated
    calibration products, then it will run the pipeline and produce the MSes,
    including the .ms.split.cal files.

    A sourcename must be specified via the SOURCENAME shell environmental
    variable.  E.g., you could call:

        SOURCENAME="W51-E" casa --pipeline -r 5.1.0-74 -c "execfile('retrieve_data_run_pipeline.py')"

REQUIREMENTS:
    
    This is the tricky part.  You need astroquery installed.  In principle,
    this is straightforward, but there may be significant 'gotchas' along the
    way.

    Start CASA and install astroquery by running these commands:
    (1) Install pip:
        >>> from setuptools.command import easy_install
        >>> easy_install.main(['--user', 'pip'])
    (2) now quit CASA, then reopen it
        >>> import pip
        >>> pip.main(['install', 'astroquery', '--user'])
    (3) now quit CASA, reopen it again.  
    (3)a If CASA loads, try:
        >>> import astroquery
        >>> import keyring
        If that works, continue and you're set!
    (3)b If CASA fails to load with a message about shutil_get_terminal_size,
        see https://github.com/astropy/astroquery/issues/1219.  You will need
        to run the following command using python, /NOT/ using CASA!
        $ python -c "import pip; pip.main(['install', 'backports.shutil_get_terminal_size', '--user'])"
        After this, CASA should load again

MORE NOTES:

    If you run the script and get an error about keyring, try:

        >>> import pip
        >>> pip.main(['install', 'keyrings.alt', '--user'])

    and try again.

"""
from astroquery.alma import Alma
import six
import runpy
import tarfile
from taskinit import casalog

import os

sourcename = os.getenv('SOURCENAME')
if sourcename is None:
    raise ValueError("You must specify a sourcename with the SOURCENAME"
                     " environmental variable.")

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = six.moves.input("Username: ")
alma.login(username)

results = alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

mask = results['Source name'] == sourcename

staged = alma.stage_data(results['Member ous id'][mask])

rawmask = np.array(['tar' == x[-3:] for x in staged['URL']], dtype='bool')
data = alma.download_files(staged['URL'][rawmask], savedir='.')

for filename in data:
    print(filename)
    if 'tar.gz' == filename[-6:] or 'tgz' == filename[-3:] or 'tar' == filename[-3:]:
        with tarfile.open(filename) as tf:
            tf.extractall('.')

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
