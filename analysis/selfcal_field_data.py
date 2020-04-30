"""
Assemble information on which fields were included in self-calibration
"""
from astropy import units as u
from astropy.coordinates import SkyCoord
from casatools import table

tb = table()
# G338.93_B6_uid___A001_X1296_X14f_continuum_merged_12M_phase1_inf.cal.fields


def parse_fn(fn):

    basename = os.path.basename(fn)

    split = basename.split("_")

    for entry in split:
        if 'phase' in entry or 'amp' in entry:
            selfcal_entry = entry
    solint = split[-1].split(".")[0]

    selfcaliter = int(selfcal_entry.lstrip("amphse"))

    return {'region': split[0],
            'band': split[1],
            'array': '12Monly' if '12M' in split else '7M12M' if '7M12M' in split else '????',
            'selfcaliter': 'sc'+str(selfcaliter),
            'bsens': 'bsens' in fn.lower(),
           }

def get_field_data(fn):
    with open(fn, 'r') as fh:
        fields = list(map(int, fh.read().split(",")))
    return fields

def get_field_metadata(fn):

    split = fn.split("M_")

    meta = parse_fn(fn)

    if meta['bsens']:
        msname = split[0] + "M_selfcal_bsens.ms"
    else:
        msname = split[0] + "M_selfcal.ms"

    tb.open(msname+"/FIELD")
    phasedir = tb.getcol("PHASE_DIR")
    tb.close()

    field_ids = get_field_data(fn)

    coords = SkyCoord(phasedir[0,0,field_ids]*u.rad, phasedir[1,0,field_ids]*u.rad, frame='fk5')

    return {num:crd for num,crd in zip(field_ids, coords)}

if __name__ == "__main__":
    workingdir = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'
    import glob
    from astropy.table import Table
    files = glob.glob(workingdir+"/*fields")

    data = []
    data_json = []
    for fn in files:
        meta = parse_fn(fn)
        meta['fields'] = get_field_metadata(fn)
        data.append(meta)
        meta_json = meta.copy()
        meta_json['fields'] = {x:str(y) for x,y in meta['fields'].items()}
        data_json.append(meta_json)

    with open(f'{workingdir}/field_summary.json', 'w') as fh:
        json.dump(data_json, fh)

    tbl = Table(data)['region', 'array', 'band', 'bsens', 'selfcaliter', 'fields', ]
    tbl.sort(keys=['region', 'array', 'band', 'bsens', 'selfcaliter', ])
    tbl.write("fields_summary_table.ecsv")

    shutil.copy("fields_summary_table.ecsv", "/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/")
