import shutil
import glob
import numpy as np
import tarfile
from astroquery.alma import Alma
import os

alma = Alma()
alma.cache_location = Alma.cache_location = '.'

# try the ESO servers?
#alma.archive_url = 'https://almascience.eso.org'

username = input("Username: ")
alma.login(username)

results = alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

band3 = results['Band'] == 3
band6 = results['Band'] == 6

existing_tarballs = glob.glob("2017.1.01355.L/weblog_tarballs/*weblog.tgz")
mouses = results['Member ous id']
mouses_filtered = [x for x in mouses
                   if not any([x[6:].replace("/","_") in y
                               for y in existing_tarballs])]

print("Found {0} new files out of {1}".format(len(mouses_filtered), len(mouses)))

# band3files = alma.stage_data(results['Member ous id'][band3])
# band6files = alma.stage_data(results['Member ous id'][band6])
files = alma.stage_data(mouses_filtered)

#band3product_mask = np.array(['asdm' not in row['URL'] for row in band3files])
#band6product_mask = np.array(['asdm' not in row['URL'] for row in band6files])
product_mask = np.array(['asdm' not in row['URL'] for row in files])

#band3product = band3files[band3product_mask]
#band6product = band6files[band6product_mask]
product = files[product_mask]
print(product)

#band3tarballs = alma.download_files(band3product['URL'])
#band6tarballs = alma.download_files(band6product['URL'])
tarballs = alma.download_files(product['URL'])

#weblogs_band3 = alma.get_files_from_tarballs(band3tarballs,
#                                             path='.',
#                                             regex=r'.*\.weblog.tgz')
#
#weblogs_band6 = alma.get_files_from_tarballs(band6tarballs,
#                                             path='.',
#                                             regex=r'.*\.weblog.tgz')
weblogs = alma.get_files_from_tarballs(tarballs,
                                       path='.',
                                       regex=r'.*\.weblog.tgz')

if not os.path.exists('2017.1.01355.L'):
    os.mkdir('2017.1.01355.L')
if not os.path.exists('2017.1.01355.L/weblog_tarballs'):
    os.mkdir('2017.1.01355.L/weblog_tarballs')

#weblogs = weblogs_band3+weblogs_band6
for logfile in weblogs:
    print(logfile)
    with tarfile.open(logfile) as tf:
        tf.extractall('2017.1.01355.L')

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if "weblog.tgz" in fn:
            shutil.move(os.path.join(dirpath, fn),
                        os.path.join('2017.1.01355.L/weblog_tarballs', fn))
