import numpy as np
import os
import json
from get_array_config import array_config_table
from casatools import msmetadata, table
from astropy.time import Time
from astropy import units as u
import glob

msmd = msmetadata()
tb = table()


stacked = array_config_table()
start_times = Time(stacked['Start date'])
end_times = Time(stacked['End date'])

results = {}

mses = glob.glob('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L_scigoals/*/*/*/calibrated/*.split.cal')

for vis in mses:
    msmd.open(vis)
    
    obstime = Time(msmd.timerangeforobs(0)['begin']['m0']['value'], format='mjd')
    endtime = Time(msmd.timerangeforobs(0)['end']['m0']['value'], format='mjd')
    fieldnames = np.array(msmd.fieldnames())

    fieldnumbers = msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')
    fields = np.unique(fieldnames[fieldnumbers])
    antennadiameter = msmd.antennadiameter()['0']['value']
    freq = msmd.chanfreqs(0)
    integration_time = ((endtime-obstime)).to(u.hour)
    stimes = msmd.timesforscans(msmd.scansforintent('OBSERVE_TARGET#ON_SOURCE'))
    onsource_time = stimes.max() - stimes.min()
    msmd.close()
    
    if antennadiameter == 12:
        if os.path.exists(vis+"/ASDM_EXECBLOCK"):
            tb.open(vis+"/ASDM_EXECBLOCK")
        else:
            tb.open(vis.replace("calibrated","calibrated_pipeline")+"/ASDM_EXECBLOCK")
        mous = tb.getcol('sessionReference')[0].split('"')[1].split("/")[-1]
        configname = str(tb.getcol('configName')[0])
        tb.close()
    else:
        configname = '7M'
        mous = '7M'
    
    if configname == 'TP':
        # skip TP
        continue
    
    band = 'B3' if freq[0] < 150e9 else 'B6'
    
    tb.open(vis+"/ANTENNA")
    positions = tb.getcol('POSITION')
    tb.close()
    baseline_lengths = (((positions[None, :, :]-positions.T[:, :, None])**2).sum(axis=1)**0.5)
    max_bl = int(np.max(baseline_lengths))
    lb_threshold = {'B3': 750,
                    'B6': 780,
                   }

    
    TM = ('TM1' if max_bl < lb_threshold[band] else 'TM2')

    
    if antennadiameter == 12:
        array_config = stacked[(obstime > start_times) & (obstime < end_times)]['Approx\xa0Config.']
    else:
        TM = array_config = '7M'
    key = obstime.strftime('%Y-%m-%d')
    if fields[0] in results:
        # account for
        if key in results[fields[0]]:
            key = key+"_"
        results[fields[0]][key] = {'array': array_config[0],
                                   'TM': TM,
                                   'mous': mous,
                                   'band': band,
                                   'onsource': onsource_time/3600,
                                   'exptime': integration_time.to(u.hour).value}
    else:
        results[fields[0]] = {key: {'array':array_config[0],
                                    'band': band,
                                    'mous': mous,
                                    'TM': TM,
                                    'onsource': onsource_time/3600,
                                    'exptime':integration_time.to(u.hour).value
                                                            }}
    print(fields[0], key, mous, TM, array_config[0], antennadiameter,
          band, f"{integration_time:0.2f}", f"{onsource_time/3600.:0.2f}")# fieldtimes)

        
for field in results:
    mouses = set([results[field][date]['mous'] for date in results[field] if date != 'total'])
    for mous in mouses:
        date = [date for date in results[field] if date != 'total' and results[field][date]['mous'] == mous][0]
        band = results[field][date]['band']
        tm = [results[field][date]['TM'] for date in results[field] if date!='total' and results[field][date]['mous'] == mous][0]
        
        key = band+"_"+mous+"_"+tm
        
        if 'total' not in results[field]:
            results[field]['total'] = {}
            
        #if key not in results[field]['total']:
        #    results[field]['total'][key] = {}
            
        results[field]['total'][key] = sum([results[field][date]['onsource']
                                             for date in results[field]
                                             if ((date != 'total') 
                                                 and (results[field][date]['band'] == band)
                                                 and (results[field][date]['mous'] == mous)
                                                )])
                                   
        print(f"{field} {mous} {band} {TM} \n{results[field]['total']}")
        
with open('/orange/adamginsburg/ALMA_IMF/reduction/array_configurations.json', 'w') as fh:
    json.dump(results, fh)