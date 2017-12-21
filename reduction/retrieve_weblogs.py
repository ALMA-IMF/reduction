import numpy as np
import tarfile
from astroquery.alma import Alma
import os

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = input("Username: ")
alma.login(username)

results = Alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

band3 = results['Band'] == 3
band6 = results['Band'] == 6

band3files = alma.stage_data(results['Member ous id'][band3])
band6files = alma.stage_data(results['Member ous id'][band6])

band3product_mask = np.array(['asdm' not in row['URL'] for row in band3files])
band6product_mask = np.array(['asdm' not in row['URL'] for row in band6files])

band3product = band3files[band3product_mask]
band6product = band6files[band6product_mask]

band3tarballs = alma.download_files(band3product['URL'])
band6tarballs = alma.download_files(band6product['URL'])

weblogs_band3 = alma.get_files_from_tarballs(band3tarballs,
                                             path='.',
                                             regex=r'.*\.weblog.tgz')

weblogs_band6 = alma.get_files_from_tarballs(band6tarballs,
                                             path='.',
                                             regex=r'.*\.weblog.tgz')

if not os.path.exists('2017.1.01355.L'):
    os.mkdir('2017.1.01355.L')

weblogs = weblogs_band3+weblogs_band6
for logfile in weblogs:
    tf = tarfile.open(logfile)
    tf.extractall('2017.1.01355.L')
