"""
Find all .split.cal files in the current directory and subdirectory, and split
each out into one MS per spectral window.  Also, dump metadata files that will
instruct the imaging script how to merge these single-window MSes into a final
cube.
"""
import os
import glob
import json
import numpy as np

from taskinit import casalog
from taskinit import msmdtool
from tasks import split

from parse_contdotdat import parse_contdotdat

msmd = msmdtool()

# list all fields you want to make imaging scripts for here
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


metadata = {b:{} for b in bands}

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in dirnames:
        if fn[-10:] == ".split.cal":

            casalog.post("Collecting metadata for {0}".format(fn),
                         origin='make_imaging_scripts',
                        )

            msmd.open(os.path.join(dirpath, fn))
            summary = msmd.summary()

            fieldnames = np.array(msmd.fieldnames())
            field = fieldnames[msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')]
            assert len(np.unique(field)) == 1
            field = field[0]

            frq0 = msmd.chanfreqs(0)
            for bb,(lo, hi) in bands.items():
                if lo*1e9 < frq0 and hi*1e9 > frq0:
                    band = bb

            spws = msmd.spwsforfield(field)

            if field in metadata[band]:
                metadata[band][field]['path'].append(dirpath),
                metadata[band][field]['vis'].append(fn)
                metadata[band][field]['spws'].append(spws.tolist())
            else:
                metadata[band][field] = {'path': [dirpath],
                                         'vis': [fn],
                                         'spws': [spws.tolist()],
                                        }

            # touch the filename
            with open(os.path.join(dirpath, "{0}_{1}".format(field, band)), 'w') as fh:
                fh.write("")


            msmd.close()

with open('metadata.json', 'w') as fh:
    json.dump(metadata, fh)


fields = set(x for x in metadata['B3'])

to_image = {}

for band in bands:
    for field in fields:

        mymd = metadata[band][field]

        window_lens = [len(x) for x in mymd['spws']]
        # all SPW sets must have the same length
        assert len(set(window_lens)) == 1
        nspws = len(mymd['spws'][0])

        # do the splits
        for newid in range(nspws):
            to_image[band] = {field: {newid: []}}
            for path, vis, spws in zip(mymd['path'], mymd['vis'], mymd['spws']):
                base_uid = vis.split(".")[0]
                invis = os.path.join(path, vis)
                outvis = os.path.join(path,
                                      "{base_uid}_{field}_{band}_spw{spw}.split"
                                      .format(band=band, field=field,
                                              spw=newid, base_uid=base_uid))

                if os.path.exists(outvis):
                    casalog.post("Skipping {0} because it's done".format(outvis),
                                 origin='make_imaging_scripts',
                                )
                else:
                    casalog.post("Splitting {0}'s spw {2} to {1}".format(vis, outvis,
                                                                         spws[newid]),
                                 origin='make_imaging_scripts',
                                )

                    split(vis=invis,
                          spw=spws[newid],
                          outputvis=outvis,
                          datacolumn='data')

                if outvis in to_image[band][field][newid]:
                    raise ValueError()

                to_image[band][field][newid].append(outvis)


with open('to_image.json', 'w') as fh:
    json.dump(to_image, fh)



# split the continuum data

for band in bands:
    for field in fields:

        mymd = metadata[band][field]

        for path, vis, spws in zip(mymd['path'], mymd['vis'], mymd['spws']):

            contfile = os.path.join(path, '../calibration/cont.dat')

            cont_channel_selection = parse_contdotdat(contfile)

            visfile = os.path.join(path, vis)
            contvis = os.path.join(path, "continuum_"+vis+".cont")

            if os.path.exists(contvis):
                casalog.post("Skipping {0} because it's done".format(contvis),
                             origin='make_imaging_scripts',
                            )
            else:
                casalog.post("Flagging and splitting {0} to {1} for continuum"
                             .format(visfile, contvis),
                             origin='make_imaging_scripts',
                            )


                # determine target widths
                msmd.open(visfile)
                targetwidth = 10e6 # 10 MHz
                widths = []
                freqs = {}
                for spw in spws:
                    chwid = np.abs(np.mean(msmd.chanwidths(spw)))
                    widths.append(int(targetwidth/chwid))
                    freqs[spw] = msmd.chanfreqs(spw)

                linechannels = contchannels_to_linechannels(cont_channel_selection,
                                                            freqs)

                msmd.close()

                flagmanager(vis=visfile, mode='save',
                            versionname='before_cont_flags')

                initweights(vis=visfile, wtmode='weight', dowtsp=True)


                flagdata(vis=visfile, mode='manual', spw=linechannels,
                         flagbackup=False)


                # Average the channels within spws
                rmtables(contvis)
                os.system('rm -rf ' + contvis + '.flagversions')

                split(vis=visfile,
                      spw=",".join(map(str,spws)),
                      outputvis=contvis,
                      width=widths,
                      datacolumn='data')


                # If you flagged any line channels, restore the previous flags
                flagmanager(vis=visfile, mode='restore',
                            versionname='before_cont_flags')
