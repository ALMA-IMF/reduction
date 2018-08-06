"""
Make an imaging script based on a template assuming that all .split.cal files
in the current directory have some science targets in them
"""
import glob
import json

from taskinit import casalog
from taskinit import msmdtool
from task_split import split

msmd = msmdtool()

# list all fields you want to make imaging scripts for here
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


metadata = {b:{} for b in bands}

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in dirnames:
        if fn[-10:] == ".split.cal":

            print(fn)

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

                casalog.post("Splitting {0}'s spw {2} to {1}".format(vis, outvis,
                                                                     spws[newid]),
                             origin='make_imaging_scripts',
                            )

                split(vis=invis,
                      spw=spws[newid],
                      outputvis=outvis,
                      datacolumn='corrected')

                if outvis in to_image[band][field][newid]:
                    raise ValueError()

                to_image[band][field][newid].append(outvis)
            

with open('to_image.json', 'w') as fh:
    json.dump(to_image, fh)
