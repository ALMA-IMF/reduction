from parse_weblog import (weblog_names, make_links, get_human_readable_name,
                          get_mous_to_sb_mapping, get_all_fluxes, fluxes_to_table)
import glob
import os
import json

mapping = get_mous_to_sb_mapping('2017.1.01355.L')

os.chdir('/home/www.aoc.nrao.edu/homes/aginsbur/alma-imf-weblogs')
weblogs = glob.glob("pipeline*")

weblog_maps = weblog_names(weblogs, mapping)

make_links(weblog_maps)

fluxes = get_all_fluxes(weblogs)

with open('fluxes.json', 'w') as fh:
    json.dump(fluxes, fh)

fluxtbl = fluxes_to_table(fluxes)
for colname in fluxtbl.colnames:
    fluxtbl.rename(colname,
fluxtbl.write('fluxes.ipac', format='ascii.ipac')
