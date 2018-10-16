"""
Find all .split.cal files in the current directory and subdirectory, and split
each out into one MS per spectral window.  Also, dump metadata files that will
instruct the imaging script how to merge these single-window MSes into a final
cube.

In order to run this code, you need to be able to import ``parse_contdotdat``,
which means to need to add the directory that contains that file to your path.
You can do this in two ways:

    (1) In python:
        import sys
        sys.path.append('/path/that/contains/file/')
    (2) From the command line (if you're using a BASH-like shell):
        export SCRIPT_DIR='/path/that/contains/file/'
        export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

"""
import os
import json
import numpy as np

from taskinit import casalog
from taskinit import msmdtool
from tasks import split, flagmanager, flagdata, rmtables, concat

from parse_contdotdat import parse_contdotdat, contchannels_to_linechannels

msmd = msmdtool()

# band name : frequency range (GHz)
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }

def logprint(string):
    casalog.post(string, origin='make_imaging_scripts')
    print(string)

metadata = {b:{} for b in bands}

for dirpath, dirnames, filenames in os.walk('.'):
    for fn in dirnames:
        if fn[-10:] == ".split.cal":

            logprint("Collecting metadata for {0}".format(fn))

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
                metadata[band][field]['path'].append(os.path.abspath(dirpath)),
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

logprint("Completed metadata assembly")

# extract the fields from the metadata
fields = set(x for x in metadata['B3']) | set(x for x in metadata['B6'])

to_image = {}

for band in bands:
    to_image[band] = {}
    for field in fields:

        if field not in metadata[band]:
            logprint("Skipping {0}:{1} because it has no metadata"
                     .format(band, field))
            continue
        mymd = metadata[band][field]

        window_lens = [len(x) for x in mymd['spws']]
        # all SPW sets must have the same length
        if len(set(window_lens)) != 1:
            raise ValueError("There are spectral windows with different "
                             "lengths, which we can't handle.  Field={0}, "
                             "band={1}".format(field, band))
        nspws = len(mymd['spws'][0])

        to_image[band][field] = {}

        # do the individual window splits
        for newid in range(nspws):
            to_image[band][field][newid] = []
            for path, vis, spws in zip(mymd['path'], mymd['vis'], mymd['spws']):
                base_uid = vis.split(".")[0]
                invis = os.path.join(path, vis)
                outvis = os.path.join(path,
                                      "{base_uid}_{field}_{band}_spw{spw}.split"
                                      .format(band=band, field=field,
                                              spw=newid, base_uid=base_uid))

                if os.path.exists(outvis):
                    logprint("Skipping {0} because it's done".format(outvis))
                else:
                    logprint("Splitting {0}'s spw {2} to {1}".format(vis,
                                                                     outvis,
                                                                     spws[newid]),)

                    split(vis=invis,
                          spw=spws[newid],
                          field=field,
                          outputvis=outvis,
                          # there is no corrected_data column because we're
                          # splitting from split MSes
                          datacolumn='data',
                         )

                if outvis in to_image[band][field][newid]:
                    raise ValueError()

                to_image[band][field][newid].append(outvis)


with open('to_image.json', 'w') as fh:
    json.dump(to_image, fh)

logprint("Completed line ms splitting.  Moving on to continuum splitting")

cont_mses = []

# split the continuum data
cont_to_merge = {}
for band in bands:
    for field in fields:

        cont_to_merge[band] = {field: []}

        if field not in metadata[band]:
            logprint("Skipping {0}:{1} because it has no metadata"
                     .format(band, field))
            continue

        mymd = metadata[band][field]

        for path, vis, spws in zip(mymd['path'], mymd['vis'], mymd['spws']):

            # the cont.dat file should be in the calibration/ directory in the
            # same SB folder
            contfile = os.path.join(path, '../calibration/cont.dat')

            if not os.path.exists(contfile):
                logprint("No cont.dat file found for {0}.  Skipping."
                         .format(path))
                continue
            cont_channel_selection = parse_contdotdat(contfile)

            visfile = os.path.join(path, vis)
            contvis = os.path.join(path, "continuum_"+vis+".cont")

            cont_to_merge[band][field].append(contvis)

            if os.path.exists(contvis):
                logprint("Skipping {0} because it's done".format(contvis),)
            else:
                logprint("Flagging and splitting {0} to {1} for continuum"
                         .format(visfile, contvis),)


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

                # not clear why this is done in other imaging scripts, but it
                # seems to achieve the wrong effect.
                #initweights(vis=visfile, wtmode='weight', dowtsp=True)


                flagdata(vis=visfile, mode='manual', spw=linechannels,
                         flagbackup=False)


                # Average the channels within spws
                rmtables(contvis)
                os.system('rm -rf ' + contvis + '.flagversions')

                split(vis=visfile,
                      spw=",".join(map(str,spws)),
                      field=field,
                      outputvis=contvis,
                      width=widths,
                      datacolumn='data')


                # If you flagged any line channels, restore the previous flags
                flagmanager(vis=visfile, mode='restore',
                            versionname='before_cont_flags')

        member_uid = path.split("member.")[-1].split("/")[0]
        merged_continuum_fn = os.path.join(path,
                                           "{field}_{band}_{muid}_continuum_merged.cal.ms"
                                           .format(field=field,
                                                   band=band,
                                                   muid=member_uid)
                                          )

        if os.path.exists(merged_continuum_fn):
            logprint("Skipping merged continuum {0} because it's done"
                     .format(merged_continuum_fn),)
        else:
            logprint("Merging continuum for {0} {1} into {2}"
                     .format(merged_continuum_fn, field, band),)

            concat(vis=cont_to_merge[band][field],
                   concatvis=merged_continuum_fn,)
        cont_mses.append(merged_continuum_fn)

with open('continuum_mses.txt', 'w') as fh:
    for line in cont_mses:
        fh.write(line+'\n')
