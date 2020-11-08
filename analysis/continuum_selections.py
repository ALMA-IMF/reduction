import os
import pylab as pl
import numpy as np
import json
from pathlib import Path
from astropy import units as u
from astropy import constants
from astropy import log
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
from pathlib import Path


# copy-pasted from parse_contdotdat
def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)

xlabel_offset = {
    3: 0.00,
    6: 0.20,
}

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

vlsrs = u.Quantity(list(map(u.Quantity, field_vlsr.values())))
vmin = vlsrs.min()
vmax = vlsrs.max()
zmin = 1-(vmax/constants.c).decompose()
zmax = 1+np.abs(vmin/constants.c).decompose()
dzm = 1+((vmax-vmin)/constants.c).decompose()


# these are basically just notes that get overwritten below
frequency_coverage = {
    'B3': {
           1: (93.0931359128077, 93.21807487765145,    2048),
           0: (91.6824842830137, 92.6819960017637,     2048),
           2: (102.08163478365731, 103.08114650240731, 2048),
           3: (104.48007228365731, 105.47958400240731, 2048),
          },
    'B6': {
        0: (216.058164552243,   216.2924174819305,  1920),
        1: (217.008115724118,   217.242246583493,   960),
        2: (218.08794227907555, 218.32219520876305, 1920),
        3: (219.47637001345055, 219.59343544313805, 960),
        4: (219.86137977907555, 219.97832313845055, 480),
        5: (230.26977356280713, 230.73754700030713, 480),
        6: (231.01931579913526, 231.48782165851026, 1920),
        7: (231.48238541765087, 233.35640885515087, 1920),
    }
}
total_bw = {band: sum(entry[1]-entry[0] for entry in flist.values()) for band,flist in frequency_coverage.items()}

basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L')
with open(basepath / 'contdatfiles.json', 'r') as fh:
    contdatfiles = json.load(fh)
with open(basepath / 'metadata.json', 'r') as fh:
    metadata = json.load(fh)


frange = {band: np.array((np.min([np.array(metadata[band][field]['freqs']).min(axis=0) for field in metadata[band]], axis=0)[:,0],
                          np.max([np.array(metadata[band][field]['freqs']).max(axis=0) for field in metadata[band]], axis=0)[:,1])).T/1e9
          for band in metadata}
sorted_inds = {band: np.argsort(frange[band][:,0]) for band in frange}
frequency_coverage = {band:
                      {ind: tuple(frange[band][ind,:]) +
                       (int(frequency_coverage[band][ind][2] *
                            (frange[band][ind,1]-frange[band][ind,0]) /
                            (frequency_coverage[band][ind][1]-frequency_coverage[band][ind][0])),)
                       for ind in sorted_inds[band]} for band in frange}


configmap = {'7M': 0,
             '12Mshort': 1,
             '12Mlong': 2}
nconfigs = len(configmap)

fields = sorted("G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split())
nfields = len(fields)
fields_and_numbers = list(enumerate(fields))

included_bw = {}

lb_threshold = {3: 750,
                6: 780,}

for fignum,band in enumerate((3,6)):
    bandname = f'B{band}'
    pl.close(fignum)
    fig = pl.figure(fignum, figsize=(12,6))


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
            baseline_lengths = metadata[bandname][field]['max_bl']
            muid_to_bl = {k:int(v) for k,v in baseline_lengths.items()}
            muid_configs = {muid: '7M' if muid_to_bl[muid] < 100
                            else '12Mshort' if muid_to_bl[muid] < lb_threshold[band]
                            else '12Mlong' if muid_to_bl[muid] > lb_threshold[band]
                            else None
                            for muid in muid_to_bl
                           }
            muid_configs.update({val:key for key,val in metadata[bandname][field]['muid_configs'].items()})
            print(band, field, muid_configs)

            for muid in muids:

                cdid = f'{field}B{band}{muid}'
                config = muid_configs[muid]
                if cdid not in contdatfiles:
                    log.error(f"Missing {cdid}  {field} B{band} {muid}")
                    if config is not None:
                        included_bw[band][spw][field][config] = np.nan
                    continue
                if 'notfound' in contdatfiles[cdid]:
                    log.error(f"Missing {cdid}  {field} B{band} {muid}: {contdatfiles[cdid]}")
                    if config is not None:
                        included_bw[band][spw][field][config] = np.nan
                    continue

                contdat = parse_contdotdat(contdatfiles[cdid])
                if config is None:
                    log.error(f"muid={muid} cdid={cdid}, contdat={contdatfiles[cdid]} but config={config}")
                    continue

                configid = configmap[config]

                muid_ind = metadata[bandname][field]['muid'].index(muid)
                frqrange_covered_perspw = metadata[bandname][field]['freqs'][muid_ind]*u.Hz
                for freq_ind,(fmin,fmax) in enumerate(frqrange_covered_perspw):
                    if fmax > frqarr[nfrqs//2] > fmin:
                        break
                covered_freqs = (frqarr > fmin) & (frqarr < fmax)

                # 2 = all covered frequencies
                # 1 = continuum frequencies
                frqmask[fieldnum*nconfigs + configid, covered_freqs] = 2

                for frqline in contdat.split(";"):
                    fsplit = frqline.split("~")
                    f2 = u.Quantity(fsplit[1])
                    f1 = u.Quantity(float(fsplit[0]), f2.unit)

                    if f1 == f2:
                        continue
                    assert f1 < f2

                    sel = (frqarr > f1) & (frqarr < f2)
                    frqmask[fieldnum*nconfigs + configid, sel] = 1

                frqmasks[spw] = frqmask

                # 1 = included
                # 2 = covered
                included_bw[band][spw][field][config] = (frqmask[fieldnum*nconfigs+configid,:] == 1).sum() * dnu

                robust = 0 # hard-code.... yike.
                specname = basepath / f'imaging_results/spectra/{field}_{"12M" if "12M" in config else "7M"}_B{band}_spw{spw}_robust{robust}_lines.image_mean.fits'
                if os.path.exists(specname):
                    print(specname)
                    pl.figure(4).clf()
                    fh = fits.open(specname)
                    ww = WCS(fh[0].header)
                    specfrq = ww.wcs_pix2world(np.arange(fh[0].data.squeeze().size), 0)[0] / 1e9
                    pl.plot(specfrq, fh[0].data.squeeze())
                    axlims = pl.axis()
                    pl.plot(frqarr, frqmask[fieldnum*nconfigs + configid]-1)
                    pl.axis(axlims)
                    pl.xlabel("Frequency")
                    pl.ylabel("Flux [Jy/beam]")
                    pl.title(os.path.split(specname)[-1].replace(".fits", ""))
                    pl.savefig(basepath / f'imaging_results/spectra/pngs/{field}_{"12M" if "12M" in config else "7M"}_B{band}_spw{spw}_robust{robust}_lines.image_mean.coverage.png',
                               bbox_inches='tight')


                if muid == 'member.uid___A001_X1296_X127':
                    assert not np.isnan(included_bw[band][spw][field][config])
                    log.info(f"Success for muid {muid}")

            if 1 in included_bw[3]:
                if 'G012.80' in included_bw[3][1]:
                    assert included_bw[3][1]['G012.80']['12Mlong'] is not None

        # insanity checks
        if 6 in included_bw:
            assert not np.isnan(included_bw[6][0]['W43-MM3']['12Mshort'])

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

        # gnuplot: 
        # black -> zero
        # red -> 1 (included)
        # yellow -> 2 (covered, not-continuum)
        ax.imshow(frqmask, extent=[minfrq, maxfrq, nfields*nconfigs, 0],
                  interpolation='nearest', cmap='gnuplot')
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

    fig.text(0.5, xlabel_offset[band], 'Frequency (GHz)', ha='center')

    pl.savefig(f"continuum_selection_regions_band{band}.png", bbox_inches='tight')
    pl.savefig(f"continuum_selection_regions_band{band}.pdf", bbox_inches='tight')

#print({k:v.sum(axis=1)/v.shape[1] for k,v in frqmasks.items()})
#print(included_bw)

included_bw_byband = {band:
                      {field:
                       {config:
                        sum(included_bw[band][spw][field][config]
                            for spw in included_bw[band]
                            if included_bw[band][spw][field][config] is not None
                           )
                        for config in included_bw[band][0][field]
                       }
                       for field in fields if field in included_bw[band][0]}
                      for band in (3,6)}
#print(included_bw_byband)

bandfrac = {band: {field: {config: included_bw_byband[band][field][config]/total_bw[f"B{band}"] for config in included_bw_byband[band][field]} for field in included_bw_byband[band]} for band in (3,6)}
bandfrac_tbl = np.empty([len(bandfrac) * nconfigs, nfields]) * np.nan
bandfrac_flat = []
for ibb, band in enumerate([3,6]):
    for iff, field in enumerate(fields):
        for icc, config in enumerate(bandfrac[band][field]):
            bandfrac_tbl[ibb*nconfigs + icc, iff] = bandfrac[band][field][config]
            bandfrac_flat.append({'field': field, 'band': band, 'config': config, 'bwfrac': bandfrac[band][field][config]})

# sum(()) = 0, so for fields with zeros, nan 'em
bandfrac_tbl[bandfrac_tbl==0]=np.nan



fig = pl.figure(2)
fig.clf()
ax = fig.gca()
pl.imshow(bandfrac_tbl.T, interpolation='nearest', cmap='viridis', vmin=0, vmax=1)
ax.set_xticks(list(range(6)),)
ax.set_xticklabels(['7m-B3','12m-short-B3', '12m-long-B3', '7m-B6','12m-short-B6', '12m-long-B6'])
pl.xticks(rotation='vertical')
ax.set_yticks(list(range(len(fields))))
ax.set_yticklabels(fields)
ax.set_ylim(-0.5,len(fields)-0.5)
cb = pl.colorbar()
cb.set_label("Fraction of bandwidth in 'cleanest' continuum")
pl.savefig("continuum_selection_fraction.png", bbox_inches='tight')
pl.savefig("continuum_selection_fraction.pdf", bbox_inches='tight')


bandfrac_table = Table(bandfrac_flat)
#print(bandfrac_table)

bandfrac_table.write

tbldir = Path('/bio/web/secure/adamginsburg/ALMA-IMF/tables')
bandfrac_table.write(tbldir / 'bandpass_fraction.ecsv', overwrite=True)
bandfrac_table.write(tbldir / 'bandpass_fraction.ipac', format='ascii.ipac', overwrite=True)
bandfrac_table.write(tbldir / 'bandpass_fraction.html', format='ascii.html', overwrite=True)
bandfrac_table.write(tbldir / 'bandpass_fraction.tex', overwrite=True)
bandfrac_table.write(tbldir / 'bandpass_fraction.js.html', format='jsviewer')
