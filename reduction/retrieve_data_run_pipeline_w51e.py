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

SPACESAVING = 3
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


"""
2018-08-03 16:12:15     INFO    casa::scriptForPI::     *** ALMA scriptForPI ***
2018-08-03 20:21:59     INFO    casa::scriptForPI::     ALMA scriptForPI completed.
"""
