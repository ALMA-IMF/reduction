from astroquery.alma import Alma
import six

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = six.moves.input("Username: ")
alma.login(username)

results = Alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

data = alma.retrieve_data_from_uid(results['Member ous id'])
