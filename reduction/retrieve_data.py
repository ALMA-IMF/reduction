from astroquery.alma import Alma

alma = Alma()
alma.cache_location = Alma.cache_location = '.'
username = input("Username: ")
alma.login(username)

results = Alma.query(payload=dict(project_code='2017.1.01355.L'), public=False, cache=False)

band3 = results['Band'] == 3
band6 = results['Band'] == 6

alma.retrieve_data_from_uid(results['Member ous id'][band3])
alma.retrieve_data_from_uid(results['Member ous id'][band6])
