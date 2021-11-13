"""
Script to update a release for delivery to ALMA
"""
from parse_weblog import get_mous_to_sb_mapping
from astroquery.alma import Alma
from astropy import units as u
from astropy.io import fits

def get_sb_to_mous_mapping(obstypes=['TM1', 'TM2'], programid='2017.1.01355.L'):
    m_to_s = get_mous_to_sb_mapping(programid)
    s_to_m = {}

    for key, val in m_to_s.items():
        field = val.split("_")[0]
        band = val.split("_")[2].replace("0","B")
        if (field, band) in s_to_m:
            s_to_m[(field, band)].append(key)
        else:
            s_to_m[(field, band)] = [key]

    return s_to_m

def add_to_hdr(filename, field, band, s_to_m):
    mousids = s_to_m[(field, band)]
    gous, obsid = mous_to_gous(mousids[0])
    if len(mousids) > 0:
        with fits.open(filename, 'a') as fh:
            for ii, mid in enumerate(mousids):
                fh[0].header[f'MOUSID{ii}'] = mid
            fh[0].header['GOUSID'] = gous
            fh[0].header['OBSID'] = obsid

def mous_to_gous(mous):
    rslt = Alma.query_tap(f"select top 10 * from ivoa.ObsCore where member_ous_uid = '{mous}'")
    tbl = rslt.to_table()
    gous = set(tbl['group_ous_uid'])
    if len(gous) != 1:
        raise ValueError("oopsy gousy")
    gous = list(gous)[0]
    obsid = tbl['obs_id'][0]
    return gous, obsid

def get_band(hdr):
    frq = u.Quantity(hdr['CRVAL3'], u.Hz)
    band = 'B3' if frq < 115*u.GHz else 'B6'
    return band

if __name__ == "__main__":
    import glob

    s_to_m = get_sb_to_mous_mapping()
    s_to_m.update(get_sb_to_mous_mapping(programid='2013.1.01365.S'))
    print(s_to_m)
    print(get_sb_to_mous_mapping(['TM1', 'TM2', 'TM'], programid='2013.1.01365.S'))

    for fn in glob.glob('/orange/adamginsburg/web/secure/ALMA-IMF/June2021FlatRelease/*.image.tt0.pbcor.fits'):
        hdr = fits.getheader(fn)
        field = hdr['OBJECT'].strip()
        band = get_band(hdr)
        mousids = s_to_m[(field, band)]
        gous, obsid = mous_to_gous(mousids[0])
        print(f"Field={field}, gous={gous}, obsid={obsid}, mousids={mousids}")
