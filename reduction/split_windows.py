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

   cd to the directory containing the untarred data (i.e., 2017.1.01355.L)
   run this file with `%run -i ./path/to/reduction/split_windows.py

You can set the following environmental variables for this script:
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only split
        fields with this name (e.g., "W43-MM1", "W51-E", etc.).
        Metadata will still be collected for *all* available MSes.
"""
import os
import json
import numpy as np

import sys
sys.path.append('.')

from taskinit import casalog
from taskinit import msmdtool
from taskinit import mstool
from tasks import split, flagmanager, flagdata, rmtables, concat

from parse_contdotdat import parse_contdotdat, contchannels_to_linechannels

msmd = msmdtool()
ms = mstool()

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

            # noinspection PyInterpreter
            frq0 = msmd.chanfreqs(0)
            for bb,(lo, hi) in bands.items():
                try:
                    if lo*1e9 < frq0 and hi*1e9 > frq0:
                        band = bb
                except ValueError:
                    if lo*1e9 < np.min(frq0) and hi*1e9 > np.max(frq0):
                        band = bb

            spws = msmd.spwsforfield(field)
            targetspws = msmd.spwsforintent('OBSERVE_TARGET*')
            spws = [ss for ss in spws if ss in targetspws]

            if field in metadata[band]:
                metadata[band][field]['path'].append(os.path.abspath(dirpath)),
                metadata[band][field]['vis'].append(fn)
                metadata[band][field]['spws'].append(spws)
            else:
                metadata[band][field] = {'path': [dirpath],
                                         'vis': [fn],
                                         'spws': [spws],
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

if os.getenv('FIELD_ID'):
    fields = fields & {os.getenv('FIELD_ID')}

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
                ms.open(visfile)
                Synth_HPBW = 0.3 #Smallest synth HPBW among target sample in arcsec
                # values interpolated by Roberto from https://science.nrao.edu/facilities/vla/docs/manuals/oss2016A/performance/fov/bw-smearing
                PB_HPBW = 21. * (300. / bands[band][0]) # PB HPBW at lowest band freq
                #targetwidth = 10e6 # 10 MHz
                targetwidth = 0.25 * (Synth_HPBW / PB_HPBW) * bands[band][0] * 1e9 # 98% BW smearing criterion
                widths = []
                freqs = {}
                for spw in spws:
                    chwid = np.abs(np.mean(msmd.chanwidths(spw)))
                    wid = int(targetwidth/chwid)
                    if wid <= 0:
                        raise ValueError("The channel width is greater than "
                                         "the target line width for spw {0} "
                                         "in ms {1}".format(spw, visfile))
                    widths.append(wid)
                    # these are TOPO freqs: freqs[spw] = msmd.chanfreqs(spw)
                    try:
                        freqs[spw] = ms.cvelfreqs(spwid=[spw], outframe='LSRK')
                    except TypeError:
                        freqs[spw] = ms.cvelfreqs(spwids=[spw], outframe='LSRK')

                linechannels = contchannels_to_linechannels(cont_channel_selection,
                                                            freqs)

                msmd.close()
                ms.close()

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
