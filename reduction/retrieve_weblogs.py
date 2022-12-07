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

existing_tarballs = glob.glob("2017.1.01355.L/weblog_tarballs/*weblog.tgz")
mouses = results['Member ous id']
mouses_filtered = [x for x in mouses
                   if not any([x[6:].replace("/","_") in y
                               for y in existing_tarballs])]

print("Found {0} new files out of {1}".format(len(mouses_filtered), len(mouses)))

files = alma.stage_data(mouses_filtered)

product_mask = np.array(['asdm' not in row['URL'] for row in files])

product = files[product_mask]
print("Found {0} total product files to download".format(product))
weblog_mask = np.array(['weblog.tgz' in row['URL'] for row in product], dtype='bool')
weblog_files = product[weblog_mask]
print("Found {0} weblogs to download".format(len(weblog_files)))
weblog_fns = [x.split("/")[-1] for x in weblog_files['URL']]
existing_weblog_fns = [x.split("/")[-1] for x in existing_tarballs]
weblog_urls_to_download = [row['URL'] for row,fn in zip(weblog_files, weblog_fns) if fn not in existing_weblog_fns]
print("Found {0} *new* weblogs to download".format(len(weblog_urls_to_download)))

for fn in weblog_urls_to_download:
    if 'tgz' not in fn:
        raise ValueError

weblog_tarballs = alma.download_files(weblog_urls_to_download)

if not os.path.exists('2017.1.01355.L'):
    os.mkdir('2017.1.01355.L')
if not os.path.exists('2017.1.01355.L/weblog_tarballs'):
    os.mkdir('2017.1.01355.L/weblog_tarballs')

#weblogs = weblogs_band3+weblogs_band6
for logfile in weblog_tarballs:
    print(logfile)
    with tarfile.open(logfile) as tf:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf, "2017.1.01355.L")

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if "weblog.tgz" in fn:
            shutil.move(os.path.join(dirpath, fn),
                        os.path.join('2017.1.01355.L/weblog_tarballs', fn))
