import os
import numpy as np
from astropy import table
from astropy import units as u
import re

def get_human_readable_name(weblog):

    for directory, dirnames, filenames in os.walk(weblog):
        if 't2-1_details.html' in filenames:
            #print("Found {0}:{1}".format(directory, "t2-1_details.html"))
            with open(os.path.join(directory, 't2-1_details.html')) as fh:
                txt = fh.read()

            max_baseline = re.compile("<th>Max Baseline</th>\s*<td>([0-9a-z\. ]*)</td>").search(txt).groups()[0]
            max_baseline = u.Quantity(max_baseline)

            array_name = ('7MorTP' if max_baseline < 100*u.m else 'TM2'
                          if max_baseline < 1000*u.m else 'TM1')
            #print("array_name = {0}".format(array_name))
            break
    
    for directory, dirnames, filenames in os.walk(weblog):
        if 't2-2-3.html' in filenames:
            with open(os.path.join(directory, 't2-2-3.html')) as fh:
                txt = fh.read()
            array_table = table.Table.read(txt, format='ascii.html')
            antenna_size, = map(int, set(array_table['Diameter']))
            break

    for directory, dirnames, filenames in os.walk(weblog):
        if 't2-2-2.html' in filenames:
            with open(os.path.join(directory, 't2-2-2.html')) as fh:
                txt = fh.read()
    
            array_table = table.Table.read(txt, format='ascii.html')
            band_string, = set(array_table['Band'])
            band = int(band_string.split()[-1])
            break

    for directory, dirnames, filenames in os.walk(weblog):
        if 't2-2-1.html' in filenames:
            with open(os.path.join(directory, 't2-2-1.html')) as fh:
                txt = fh.read()
    
            array_table = table.Table.read(txt, format='ascii.html')
            mask = np.array(['TARGET' in intent for intent in array_table['Intent']], dtype='bool')
            source_name, = set(array_table[mask]['Source Name'])
            break

    if array_name == '7MorTP':
        if antenna_size == 7:
            array_name = '7M'
        elif antenna_size == 12:
            array_name = 'TP'
        else:
            raise

    sbname = "{0}_a_{1:02d}_{2}".format(source_name, band, array_name, )

    print(sbname, max_baseline)

    return sbname

def weblog_names(list_of_weblogs):
    return {get_human_readable_name(weblog): weblog
            for weblog in list_of_weblogs}

def make_links(weblog_maps):
    reverse_map = {v:k for k,v in weblog_maps.items()}
    assert len(reverse_map) == len(weblog_maps)

    for k,v in weblog_maps.items():
        try:
            os.symlink('../{0}'.format(v), 'humanreadable/{0}'.format(k))
        except FileExistsError:
            pass
