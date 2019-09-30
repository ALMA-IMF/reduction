import numpy as np
from astroquery.alma import Alma
import six
import runpy
import tarfile
from astropy import log

import os

sourcename = os.getenv('SOURCENAME')
if sourcename is None:
    raise ValueError("You must specify a sourcename with the SOURCENAME"
                     " environmental variable.")

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = os.getenv('USERNAME')
if username is None:
    username = six.moves.input("Username: ")
alma.login(username)

results = alma.query(payload=dict(project_code='2017.1.01355.L'),
                     public=False, cache=False)

log.info("Downloading data for source {sourcename}".format(sourcename=sourcename))

if sourcename == 'all':
    log.setLevel('DEBUG')
    for uid in results['Member ous id']:
        # create a fresh instance per stage
        alma2 = alma()
        alma2.login(username)
        alma2.cache_location = '.'

        staged = alma2.stage_data([uid])
        for row in staged['URL']:
            print(row)
            data = alma2.download_files([row], savedir='.', cache=True,
                                        continuation=True)
    log.setLevel('INFO')

else:
    mask = results['Source name'] == sourcename

    staged = alma.stage_data(results['Member ous id'][mask])

    rawmask = np.array(['tar' == x[-3:] for x in staged['URL']], dtype='bool')

    data = alma.download_files(staged['URL'][rawmask], savedir='.')

    # do a check at the end
    for fn in data:
        if os.path.exists(os.path.basename(fn)):
            print("{fn} is OK".format(fn=fn))
        else:
            print("{fn} is missing".format(fn))
