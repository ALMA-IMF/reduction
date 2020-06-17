import pylab as pl
import numpy as np
import json
from pathlib import Path
from astropy import units as u
from astropy import log


# copy-pasted from parse_contdotdat
def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)

lines_to_overplot = {
    "n2hp": "93.173700GHz",
    "sio": "217.104984GHz",
    "h2co303": "218.222195GHz",
    "12co": "230.538GHz",
    "h30a": "231.900928GHz",
    "h41a": "92.034434GHz",
    "c18o": "219.560358GHz",
    #"ch3ccn": "92.26144GHz",
    #"ch3cch": "102.547983GHz",
}
field_vlsr = {
    "W51-E": "55km/s",
    "W51-IRS2": "55km/s",
    "G010.62": "-2km/s",
    "G353.41": "-18km/s",
    "W43-MM1": "97km/s",
    "W43-MM2": "97km/s",
    "W43-MM3": "97km/s",
    "G337.92": "-40km/s",
    "G338.93": "-62km/s",
    "G328.25": "-43km/s",
    "G327.29": "-45km/s",
    "G333.60": "-47km/s",
    "G008.67": "37.60km/s",
    "G012.80": "37.00km/s",
    "G351.77": "-3.00km/s",
}

frequency_coverage = {
    'B3': {
           1: (93.0931359128077, 93.21807487765145, 2048),
           0: (91.6824842830137, 92.6819960017637, 2048),
           2: (102.08163478365731, 103.08114650240731, 2048),
           3: (104.48007228365731, 105.47958400240731, 2048),
          },
    'B6': {
        0: (216.058164552243, 216.2924174819305, 1920),
        1: (217.008115724118, 217.242246583493, 960),
        2: (218.08794227907555, 218.32219520876305, 1920),
        3: (219.47637001345055, 219.59343544313805, 960),
        4: (219.86137977907555, 219.97832313845055, 480),
        5: (230.26977356280713, 230.73754700030713, 480),
        6: (231.01931579913526, 231.48782165851026, 1920),
        7: (231.48238541765087, 233.35640885515087, 1920),
    }
}

basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L')
with open(basepath / 'contdatfiles.json', 'r') as fh:
    contdatfiles = json.load(fh)
with open(basepath / 'metadata.json', 'r') as fh:
    metadata = json.load(fh)

configmap = {'7M': 0,
             '12Mshort': 1,
             '12Mlong': 2}
nconfigs = len(configmap)

fields = sorted("G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split())
nfields = len(fields)
fields_and_numbers = list(enumerate(fields))

included_bw = {}

lb_threshold = {3: 1000,
                6: 501,}

for fignum,band in enumerate((3,6)):
    bandname = f'B{band}'
    pl.close(fignum)
    pl.figure(fignum, figsize=(12,6))


    frqmasks = {}

    fcov = frequency_coverage[bandname]

    nspw = len(fcov)

    included_bw[band] = {}

    for spwn,(spw,(minfrq, maxfrq, nfrqs)) in enumerate(fcov.items()):
        frqmask = np.zeros([nfields * nconfigs, nfrqs], dtype='int8')

        included_bw[band][spw] = {}

        for fieldnum,field in fields_and_numbers:
            frqarr = np.linspace(minfrq, maxfrq, nfrqs)*u.GHz
            dnu = (maxfrq-minfrq)/nfrqs

            included_bw[band][spw][field] = {config: None for config in configmap}

            if field not in metadata[bandname]:
            #if f'{field}B{band}' not in contdatfiles:
                print(f"Skipping field {field} band {band} for lack of contdotdat.")
                continue

            muids = set(metadata[bandname][field]['muid'])
            baseline_lengths = list(map(int, metadata[bandname][field]['cont.dat']))
            muid_to_bl = {muid: list(map(int, [key for key, contnm in metadata[bandname][field]['cont.dat'].items() if muid in contnm])) for muid in muids}
            muid_configs = {muid: '7M' if any(x < 100 for x in muid_to_bl[muid])
                            else '12Mshort' if any(x < lb_threshold[band] for x in muid_to_bl[muid])
                            else '12Mlong' if any(x > lb_threshold[band] for x in muid_to_bl[muid])
                            else None
                            for muid in muid_to_bl
                           }
            print(band, field, muid_configs)

            for muid in muids:
                cdid = f'{field}B{band}{muid}'
                if cdid not in contdatfiles:
                    log.error(f"Missing {cdid}  {field} B{band} {muid}")
                    for config in range(nconfigs):
                        included_bw[band][spw][field][config] = np.nan
                    continue

                contdat = parse_contdotdat(contdatfiles[cdid])
                config = muid_configs[muid]
                configid = configmap[config]

                frqmask[fieldnum*nconfigs + configid, :] = 2

                for frqline in contdat.split(";"):
                    fsplit = frqline.split("~")
                    f2 = u.Quantity(fsplit[1])
                    f1 = u.Quantity(float(fsplit[0]), f2.unit)

                    assert f1 < f2

                    sel = (frqarr > f1) & (frqarr < f2)
                    frqmask[fieldnum*nconfigs + configid, sel] = 1

                frqmasks[spw] = frqmask

                included_bw[band][spw][field][config] = (~frqmask[fieldnum*nconfigs+configid,:]).sum() * dnu


        assert frqmask.sum() > 0

        #if band == 6:
        #    # W41-MM1 B6 doesn't exist
        #    assert not np.any(frqmask[10,:])

        ax = pl.subplot(1, nspw, spwn+1)
        #print(ax,spwn)
        yticklocs = (np.arange(nfields*nconfigs) + np.arange(1, nfields*nconfigs+1))/2.
        tick_maps = list(zip(yticklocs, fields))
        #print(tick_maps)
        if spwn == 0:
            ax.set_yticks(yticklocs[nconfigs//2::nconfigs])
            ax.set_yticklabels(fields)
        else:
            ax.set_yticks([])

        ax.set_xticks([minfrq, (minfrq+maxfrq)/2, maxfrq])
        ax.set_xticklabels([f"{frq:0.2f}" for frq in ax.get_xticks()])
        if spwn % 2 == 1:
            ax.xaxis.set_ticks_position('top')

        ax.imshow(frqmask, extent=[minfrq, maxfrq, nfields*nconfigs, 0],
                  interpolation='none', cmap='gnuplot')
        ax.set_aspect((maxfrq-minfrq)*2 / (nfields*nconfigs))

        xmin, xmax = ax.get_xlim()
        ax.hlines(np.arange(nfields)*3, xmin, xmax, color='w', linestyle='-')

        for linename,linefrq in lines_to_overplot.items():
            linefrq = u.Quantity(linefrq).to(u.GHz)
            linefrqval = linefrq.value
            if (minfrq < linefrqval) & (maxfrq > linefrqval):
                for fieldnum,field in fields_and_numbers:
                    vlsr = u.Quantity(field_vlsr[field])
                    shifted_frq = vlsr.to(u.GHz, u.doppler_radio(linefrq)).value
                    if (minfrq < shifted_frq) & (maxfrq > shifted_frq):
                        ax.vlines(shifted_frq, fieldnum*nconfigs,
                                  (fieldnum+1)*nconfigs, color='b')


    pl.tight_layout()
    pl.subplots_adjust(wspace=0.05, hspace=0)

    pl.savefig(f"continuum_selection_regions_band{band}.png", bbox_inches='tight')
    pl.savefig(f"continuum_selection_regions_band{band}.pdf", bbox_inches='tight')

#print({k:v.sum(axis=1)/v.shape[1] for k,v in frqmasks.items()})
#print(included_bw)

included_bw_byband = {band: {field: {config: sum(x[config] for x in included_bw[band][field].values())}
                             for field in fields if field in included_bw[band][0]}
                      for band in (3,6)}
#print(included_bw_byband)
total_bw = {band: sum(entry[1]-entry[0] for entry in flist.values()) for band,flist in frequency_coverage.items()}

bandfrac = {band: {field: included_bw_byband[band][field]/total_bw[f"B{band}"] for field in included_bw_byband[band]} for band in (3,6)}
