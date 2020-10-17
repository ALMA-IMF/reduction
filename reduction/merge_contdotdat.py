"""
This is purely a diagnostic script for use with diagnostic_spectra.py

Nothing in this file is intended to be used in any sort of production code
"""
import os
import json

def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)


data = {}

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in filenames:
        if fn == 'cont.dat':
            contfn = os.path.join(dirpath, fn)
            with open(contfn, 'r') as readfh:
                field = readfh.readline().split()[1]
            if field in data:
                data[field] += ";" + parse_contdotdat(contfn)
            else:
                data[field] = parse_contdotdat(contfn)

with open('merged_cont.dat.json', 'w') as fh:
    json.dump(data, fh)
