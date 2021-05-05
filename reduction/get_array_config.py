import os
from astropy.table import Table, vstack
from astropy.io import ascii
from astropy.time import Time

try:
    from casatools import msmetadata
    msmd = msmetadata()
except ImportError:
    from taskinit import msmdtool
    msmd = msmdtool()


def array_config_table(filename='config_table.csv'):
    import requests
    from bs4 import BeautifulSoup

    if not os.path.exists(filename):
        url = "https://almascience.eso.org/observing/observing-configuration-schedule/prior-cycle-observing-and-configuration-schedule"

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text)
        tables = soup.findAll('table', class_="grid listing")

        def clean_lines(soup, badrows=['Long Baseline Campaign',
                                       'February Maintenance Period',
                                       'End of Cycle',
                                       'Engineering/Software',
                                       'Engineering/Software Time',
                                      ]):
            for tr in soup('tr'):
                if any(bad in str(tr) for bad in badrows):
                    _ = tr.extract()
            return soup

        tables = soup.findAll('table', class_="grid listing")
        tables = [ascii.read(str(clean_lines(tbl)), format='html') for tbl in tables]

        # this is to clean up some bad formatting in the tables
        tables[3] = tables[3][:-1]
        tables[3]['Block'] = tables[3]['Block'].astype('int')
        tables[4]['maximumrecoverablescale2(")'] = tables[4]['maximumrecoverablescale2(")'].astype('str')

        stacked = vstack(tables)

        stacked.write(filename)
    else:
        stacked = Table.read(filename)

    return stacked

def get_array_config(vis, filename='config_table.csv'):
    stacked = array_config_table(filename=filename)

    start_times = Time(stacked['Start date'])
    end_times = Time(stacked['End date'])

    msmd.open(vis)
    obstime = Time(msmd.timerangeforobs(0)['begin']['m0']['value'], format='mjd')
    antennadiameter = msmd.antennadiameter()['0']['value']
    msmd.close()

    if antennadiameter == 12:
        array_config = stacked[(obstime > start_times) & (obstime < end_times)]['Approx\xa0Config.'][0]
        return obstime, array_config
    else:
        return obstime, '7m'

def get_array_config(vis):
    msmd.open(vis)
    obstime = Time(msmd.timerangeforobs(0)['begin']['m0']['value'], format='mjd')
    try:
        antennadiameter = msmd.antennadiameter()['0']['value']
    except RuntimeError:
        antennadiameter = msmd.antennadiameter(0)['value']
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

    return obstime.datetime, configname