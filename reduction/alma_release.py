"""
Script to update a release for delivery to ALMA
"""
from parse_weblog import get_mous_to_sb_mapping
from astroquery.alma import Alma
from astropy import units as u
from astropy.io import fits
import os
import shutil

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
    gous, obsid, sbname = mous_to_gous(mousids[0])
    if len(mousids) > 0:
        with fits.open(filename, mode='update') as fh:
            for ii, mid in enumerate(mousids):
                fh[0].header[f'MOUSID{ii}'] = mid
            fh[0].header['GOUSID'] = gous
            fh[0].header['OBSID'] = obsid
            fh[0].header['SBNAME'] = sbname

def mous_to_gous(mous):
    rslt = Alma.query_tap(f"select top 100 * from ivoa.ObsCore where member_ous_uid = '{mous}'")
    tbl = rslt.to_table()
    gous = set(tbl['group_ous_uid'])
    if len(gous) != 1:
        raise ValueError("oupsy gousy")
    gous = list(gous)[0]
    obsid = tbl['obs_id'][0]
    sbname = tbl['schedblock_name'][0]
    return gous, obsid, sbname

def get_band(hdr):
    frq = u.Quantity(hdr['CRVAL3'], u.Hz)
    band = 'B3' if frq < 115*u.GHz else 'B6'
    return band

if __name__ == "__main__":
    import glob
    import shutil

    s_to_m = get_sb_to_mous_mapping()
    s_to_m.update(get_sb_to_mous_mapping(programid='2013.1.01365.S'))
    print(s_to_m)
    print(get_sb_to_mous_mapping(['TM1', 'TM2', 'TM'], programid='2013.1.01365.S'))
    assert ('W43-MM1', 'B6') in s_to_m

    readmeheader = "Project Code: 2017.1.01355.L\n"
    readmedata = {}

    os.chdir('/orange/adamginsburg/web/secure/ALMA-IMF/ContinuumDataArchiveDelivery')

    for suffix in ('image.tt0.pbcor.fits', 'model.tt0.fits',
            'model.tt1.fits', 'residual.tt0.fits', 'residual.tt1.fits',
            'image.tt0.fits', 'image.tt1.fits', 'psf.tt0.fits',
            'psf.tt1.fits'):

        for fn in glob.glob(f'/orange/adamginsburg/web/secure/ALMA-IMF/June2021FlatRelease/*.{suffix}'):
            hdr = fits.getheader(fn)
            field = hdr['OBJECT'].strip()
            band = get_band(hdr)
            mousids = s_to_m[(field, band)]
            gous, obsid, sbname = mous_to_gous(mousids[0])
            print(f"Field={field}, gous={gous}, obsid={obsid}, mousids={mousids}, sbname={sbname}")

            gous_ = gous.replace(":","_").replace("/","_")
            dir = f'{gous_}.lp_2017.1.01355.L.motte'
            if not os.path.exists(dir):
                os.mkdir(dir)
            new_fn = f'{gous_}.lp_2017.1.01355.L.motte.{suffix}'
            if not os.path.exists(f'{dir}/{new_fn}'):
                shutil.copy(fn, f'{dir}/{new_fn}')

            add_to_hdr(f'{dir}/{new_fn}', field, band, s_to_m)

            with fits.open(f'{dir}/{new_fn}', mode='update') as fh:
                fh[0].header['FILENAME'] = fn
                fh[0].header['BAND'] = band
                fh[0].header['FIELD'] = field

            if gous in readmedata:
                readmedata[gous_].append(new_fn)
            else:
                readmedata[gous_] = [new_fn]

    for dir in glob.glob("*.motte"):
        gous_ = dir.split(".")[0]
        with open(f'{dir}/README', 'w') as fh:
            fh.write(readmeheader)
            fh.write(f'GOUS: {gous_}')
            for row in readmedata[gous_]:
                fh.write(f"{row}\n")
