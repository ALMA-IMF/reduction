import os
import numpy as np
from astropy import table

def get_human_readable_name(weblog):

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

    return "{0}_a_{1:02d}_{2}M".format(source_name, band, antenna_size, )

def weblog_names(list_of_weblogs):
    return {get_human_readable_name(weblog): weblog
            for weblog in list_of_weblogs}

def make_links(weblog_maps):
    reverse_map = {v:k for k,v in weblog_maps.items()}
    assert len(reverse_map) == len(weblog_maps)

    for k,v in weblog_maps.items():
        os.symlink('../{0}'.format(v), 'humanreadable/{0}'.format(k))
