import numpy as np
from astroquery.alma import Alma
import six

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = six.moves.input("Username: ")
alma.login(username)

results = alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

staged_table = alma.stage_data(results['Member ous id'])

fits_filter = np.array([(('mfs.I.pbcor.fits' in fn) and
                         ('_bp.spw' not in fn) and
                         ('_ph.spw' not in fn)
                         ('_sci.spw' in fn)
                        )
                        for fn in staged_table['URL']])

continuum_images = staged_table[fits_filter]

print("Total size: {0}".format(continuum_images['size'].sum()))

alma.download_files(continuum_images['URL'])
