import os
from astropy import units as u, coordinates

import numpy as np
from astropy import units as u
import sys
import glob
sys.path.append("/orange/adamginsburg/ALMA_IMF/reduction/reduction")
sys.path.append("/orange/adamginsburg/ALMA_IMF/reduction/analysis")
import imp, diagnostic_images
from spectral_cube import SpectralCube
import selfcal_heuristics
import spectral_cube
import os

from casatools import table
tb = table()

from casatools import ms as mstool
ms = mstool()

from casatools import msmetadata as msmdtool
msmd = msmdtool()

def getcrd(field, ms):
    casacrd = ms.getfielddirmeas(fieldid=field)
    if casacrd['refer'].lower() == 'j2000':
        frame = 'fk5'
    else:
        frame = casacrd['refer'].lower()
    return coordinates.SkyCoord(casacrd['m0']['value'], casacrd['m1']['value'], frame=frame, unit=(casacrd['m0']['unit'], casacrd['m1']['unit']))

def find_closest_cal(band, field, verbose=False):
    row = md[band][field]
    for vis, path in zip(row['vis'], row['path']):
        msname = os.path.join(path, vis)

        tb.open(f'{msname}/ANTENNA')
        diam = tb.getcol('DISH_DIAMETER')
        if diam.min() < 10:
            continue

        caltabname = glob.glob(f'{field}_{band}*phase1*.cal')[0]
        msmd.open(msname)
        ms.open(msname)
        ii = msmd.fieldsforintent('CALIBRATE_PHASE#ON_SOURCE')[0]
        separations = u.Quantity([getcrd(ii, ms).separation( getcrd(jj, ms) )
                                  for jj in msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')])

        timefield = ms.getdata(['time', 'field_id'])
        if 'time' not in timefield:
            tb.open(f'{msname}')
            datadescid = tb.getcol('DATA_DESC_ID')
            #print(datadescid)
            tb.close()
            ms.open(msname)
            ms.selectinit(datadescid[0])
            timefield = ms.getdata(['time', 'field_id'])
            if 'time' not in timefield:
                print(f"FAILURE for {band} {field} {vis} {path}")
                continue
        tdiff = np.diff(timefield['time'][timefield['field_id'] == ii])
        tb.open(caltabname)
        good, bad = selfcal_heuristics.goodenough_field_solutions(caltabname)
        times_good = np.unique(timefield['time'][np.isin(timefield['field_id'], good)])
        #print(f"good, bad, & tgt fields: {good, bad, msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')}")

        md[band][field]['selfcal_maxsep'] = {}

        for tgt_id in msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE'):
            times_tgt = np.unique(timefield['time'][timefield['field_id'] == tgt_id])
            indices = np.searchsorted(times_good, times_tgt, side='left')

            if np.all(indices == len(times_good)):
                # the cal scans are not in range; usually
                # indicates 7m data matching to 12m?
                md[band][field]['selfcal_maxsep'][tgt_id] = np.inf
            else:
                try:
                    b4 = times_tgt - times_good[indices]
                except IndexError:
                    b4 = None

                try:
                    after = times_good[indices+1] - times_tgt
                except IndexError:
                    after = None

                if b4 is None and after is not None:
                    mx = after.max()
                elif after is None and b4 is not None:
                    mx = b4.max()
                else:
                    tdiff_selfcal = np.max([after, b4], axis=0)
                    mx = tdiff_selfcal.max()
                md[band][field]['selfcal_maxsep'][tgt_id] = int(round(mx))

        md[band][field]['cal_separations'] = separations
        md[band][field]['cal_time_separations'] = tdiff.max()
        if verbose:
            print(f"{field:12s} {band}: "
                  f"{msmd.fieldnames()[ii]:14s}, "
                  f"{separations.mean():25s}, "
                  f"{separations.max():25s},"
                  f" timediff: {int(tdiff.max()):10d},"
                  f" selfcaltdiff: {md[band][field]['selfcal_maxsep']}")
        selfcal_closer = [md[band][field]['selfcal_maxsep'][key] < md[band][field]['cal_time_separations']
                          for key in md[band][field]['selfcal_maxsep']]
        selfcal_further = [md[band][field]['selfcal_maxsep'][key] > md[band][field]['cal_time_separations']
                          for key in md[band][field]['selfcal_maxsep']]
        print(f"{field:12s} {band}:  Selfcal was closer in time for {sum(selfcal_closer)} and further for {sum(selfcal_further)}; "
              f"{100*sum(selfcal_closer) / len(md[band][field]['selfcal_maxsep']):0.1f}% were closer")


        ms.close()
        msmd.close()


if __name__ == "__main__":
    import pylab as pl
    pl.rcParams['figure.figsize'] = (16,8)
    os.chdir("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/")

    import json

    with open('metadata_updated.json', 'r') as fh:
        md = json.load(fh)


    for band in md:
        for field in md[band]:
            find_closest_cal(band, field, verbose=False)
