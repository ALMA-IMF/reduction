from astroquery.alma import Alma
import six
import runpy

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = six.moves.input("Username: ")
alma.login(username)

results = Alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

mask = results['Source name'] == 'W51-E'

data = alma.retrieve_data_from_uid(results['Member ous id'][mask])

for filename in data:
    print(filename)
    if 'tar.gz' == filename[-6:] or 'tgz' == filename[-3:] or 'tar' == filename[-3:]:
        with tarfile.open(logfile) as tf:
            tf.extractall('.')


for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if "scriptForPI.py" == fn:
            curdir = os.getcwd()

            os.chdir(dirpath)

            runpy.run_path(fn, init_globals=globals())

            os.chdir(curdir)
