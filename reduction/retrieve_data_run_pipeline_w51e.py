"""
Instructions:

    Run this script from within a casa-pipeline session, e.g., using casa
    --pipeline -r 5.1.0-74 on an NRAO lustre system, or just using the
    appropriate version of CASA elsewhere.  You'll then need to enter your ALMA
    archive username and password.

    The program will download the full set of raw data products and associated
    calibration products, then it will run the pipeline and produce the MSes,
    including the .ms.split.cal files.

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

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = six.moves.input("Username: ")
alma.login(username)

results = alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

mask = results['Source name'] == 'W51-E'

staged = alma.stage_data(results['Member ous id'][mask])

rawmask = np.array(['tar' == x[-3:] for x in staged['URL']], dtype='bool')
data = alma.download_files(staged['URL'][rawmask], savedir='.')
"""
Result in CV: 1.3 TB retrieved in ~8 hours
"""

# Tarfiles extract in 1-2 hours
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

# # assemble the data into the right location
# for dirpath, dirnames, filenames in os.walk('.'):
#     for fn in dirnames:
#         if fn[-10:] == ".split.cal":
#             mspath = os.path.join(dirpath, fn)
# 
#             msmd.open(mspath)
#             fieldnames = np.array(msmd.fieldnames())
#             field = fieldnames[msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')]
#             assert len(np.unique(field)) == 1
#             field = field[0]
#             msmd.close()
# 
#             if not os.path.exists(field):
#                 os.mkdir(field)
# 
#             os.symlink(mspath, field)
#         elif fn in ("cont.dat", ):
# 
#             with open(os.path.join(dirpath, "cont.dat"), 'r') as fh:
#                 firstline = fh.readline()
# 
#             field = firstline.strip().split()[-1]
# 
#             if not os.path.exists(field):
#                 os.mkdir(field)
# 
#             for fn in ("cont.dat", "flux.csv", "antennapos.csv"):
#                 fpath = os.path.join(dirpath, fn)
#                 uid = dirpath.split(".")[-1].split("/")[0]
# 
#                 os.symlink(fpath, os.path.join(field, uid+"_"+fn))


"""
2018-08-03 16:12:15     INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
2018-08-03 20:21:59     INFO    casa::scriptForPI::     ALMA scriptForPI completed.

2018-08-05 16:20:33     INFO    casa::scriptForPI::     ALMA scriptForPI completed.
2018-08-03 20:48:52     INFO    casa::pipeline_runner:: Running script member.uid___A001_X1296_X213.scriptForPI.py in ./science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X213/script
2018-08-05 02:52:55     INFO    casa::pipeline_runner:: Done running script member.uid___A001_X1296_X213.scriptForPI.py in ./science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X213/script
2018-08-05 02:53:13     INFO    casa::pipeline_runner:: Running script member.uid___A001_X1296_X215.scriptForPI.py in ./science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X215/script
2018-08-05 05:15:20     INFO    casa::pipeline_runner:: Done running script member.uid___A001_X1296_X215.scriptForPI.py in ./science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X215/script
2018-08-05 05:16:43     INFO    casa::pipeline_runner:: Running script member.uid___A001_X1296_X107.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X107/script
2018-08-05 12:51:44     INFO    casa::pipeline_runner:: Done running script member.uid___A001_X1296_X107.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X107/script
2018-08-05 12:52:02     INFO    casa::pipeline_runner:: Running script member.uid___A001_X1296_X109.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X109/script
2018-08-05 14:39:11     INFO    casa::pipeline_runner:: Done running script member.uid___A001_X1296_X109.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X109/script
2018-08-05 14:39:49     INFO    casa::pipeline_runner:: Running script member.uid___A001_X1296_X10b.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X10b/script
2018-08-05 16:20:33     INFO    casa::pipeline_runner:: Done running script member.uid___A001_X1296_X10b.scriptForPI.py in ./science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X10b/script
(subtract 24 h)

casa-20180803-160946.log:2018-08-03 16:12:15    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-03 20:21:59    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
casa-20180803-160946.log:2018-08-03 20:48:52    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-05 02:52:55    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
casa-20180803-160946.log:2018-08-05 02:53:13    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-05 05:15:20    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
casa-20180803-160946.log:2018-08-05 05:16:43    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-05 12:51:44    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
casa-20180803-160946.log:2018-08-05 12:52:02    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-05 14:39:11    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
casa-20180803-160946.log:2018-08-05 14:39:49    INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
casa-20180803-160946.log:2018-08-05 16:20:33    INFO    casa::scriptForPI::     ALMA scriptForPI completed.
"""
