"""
Script to update a release for delivery to ALMA
"""
from parse_weblogs import get_mous_to_sb_mapping
from astroquery.alma import Alma

def get_sb_to_mous_mapping(obstypes=['TM1', 'TM2']):
    m_to_s = get_mous_to_sb_mapping('2017.1.01355.L')
    s_to_m = {}

    for key, val in m_to_s.items():
        newkey = val.split("_")[0]
        if newkey in s_to_m:
            s_to_m[newkey].append(key)
        else:
            s_to_m[newkey] = [key]

    return s_to_m

def add_to_hdr(filename, field, s_to_m):
    mousids = s_to_m[field]
    if len(mousids) > 0:
        with fits.open(filename, 'a') as fh:
            for ii, mid in enumerate(mousids):
                fh[0].header[f'MOUSID{ii}'] = mid

def mous_to_gous(mous):
    rslt = Alma.query_tap(f"select top 10 * from ivoa.ObsCore where member_ous_uid = '{mous}'")
    tbl = rslt.to_table()
    gous = set(tbl['group_ous_uid'])
    if len(gous) != 1:
        raise ValueError("oopsy gousy")
    gous = list(gous)[0]
    return gous

if __name__ == "__main__":
    pass
