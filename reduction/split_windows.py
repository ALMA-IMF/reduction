"""
Find all .split.cal files in the current directory and subdirectories, and split
each out into one MS per spectral window.  Also, dump metadata files that will
instruct the imaging script how to merge these single-window MSes into a final
cube.

.split.cal files are produced by running the CASA pipeline with ``DOSPLIT=True``.
If you ran the pipeline _without_ that flag, you can still use this script, but
you must first symbolically link the calibrated .ms files to the same filename
with .split.cal appended, e.g.:

    $ ln -s my_calibrated_measurement_set.ms my_calibrated_measurement_set.ms.split.cal

In order to run this code, you need to be able to import ``parse_contdotdat``,
which means to need to add the directory that contains that file to your path.
You can do this in two ways

    (1) In python:
        import sys
        sys.path.append('/path/that/contains/this/file/')
    (2) From the command line (if you're using a BASH-like shell):
        export ALMAIMF_ROOTDIR='/path/that/contains/this/file/'

   cd to the directory containing the untarred data (i.e., 2017.1.01355.L)

   Start CASA, then run this file with (DO NOT copy and paste!):
       >>> %run -i ./path/to/reduction/split_windows.py

You can set the following environmental variables for this script:
    FIELD_ID=<name>
        If this parameter is set, filter out the imaging targets and only split
        fields with this name (e.g., "W43-MM1", "W51-E", etc.).
        Metadata will still be collected for *all* available MSes.


cont.dat files
--------------
By default, the ALMA-pipeline-derived cont.dat file will be used.  However, you
can specify an override by creating a file "{field}.{band}.cont.dat"
ALMAIMF_ROOTDIR directory.  For example, if you wanted to override the cont.dat
file for field "ORION" in band 9, you would create a file called
ORION.B9.cont.dat. Note that the names are case sensitive.
"""
import os
import json
import numpy as np

import sys

try:
    # If run from command line
    aux = os.path.dirname(os.path.realpath(sys.argv[2]))
    if os.path.isdir(aux):
        almaimf_rootdir = aux
except:
    pass

if 'almaimf_rootdir' in locals():
    os.environ['ALMAIMF_ROOTDIR'] = almaimf_rootdir
if os.getenv('ALMAIMF_ROOTDIR') is None:
    try:
        import metadata_tools
        os.environ['ALMAIMF_ROOTDIR'] = os.path.split(metadata_tools.__file__)[0]
    except ImportError:
        raise ValueError("metadata_tools not found on path; make sure to "
                         "specify ALMAIMF_ROOTDIR environment variable "
                         "or your PYTHONPATH variable to include the directory"
                         " containing the ALMAIMF code.")
else:
    sys.path.append(os.getenv('ALMAIMF_ROOTDIR'))


from getversion import git_date, git_version

from taskinit import casalog
from taskinit import msmdtool
from taskinit import mstool, tbtool
from tasks import split, flagmanager, flagdata, rmtables, concat

from parse_contdotdat import parse_contdotdat, contchannels_to_linechannels

msmd = msmdtool()
ms = mstool()
tb = tbtool()

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

            antnames = msmd.antennanames()
            if any('PM' in nm for nm in antnames):
                if len(antnames) <= 4:
                    with open(os.path.join(dirpath, "{0}_{1}_TP".format(field, band)), 'w') as fh:
                        fh.write("{0}".format(antnames))
                    logprint("Skipping total power MS {0}".format(fn))
                    msmd.close()
                    continue
                else:
                    logprint("WARNING: MS {0} contains PM antennae but is apparently not a TP data set".format(fn))

            try:
                summary = msmd.summary()
            except RuntimeError:
                logprint("Skipping FAILED MS {0}".format(fn))
                msmd.close()
                continue

            fieldnames = np.array(msmd.fieldnames())
            field = fieldnames[msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')]
            assert len(np.unique(field)) == 1,"ERROR: field={0} fieldnames={1}".format(field, fieldnames)
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
            # this is how DOSPLIT in scriptForPI decides to split
            spws = [int(ss) for ss in spws if (ss in targetspws) and (msmd.nchan(ss) > 4)]

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
                fh.write("{0}".format(antnames))


            msmd.close()

with open('metadata.json', 'w') as fh:
    json.dump(metadata, fh)

logprint("Completed metadata assembly")

# extract the fields from the metadata
all_fields = set(str(x) for x in metadata['B3']) | set(str(x) for x in metadata['B6'])

if os.getenv('FIELD_ID'):
    fields = all_fields & {os.getenv('FIELD_ID')}
else:
    fields = all_fields

to_image = {}

for band in bands:
    to_image[band] = {}
    for field in all_fields:

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
                elif field not in fields:
                    logprint("Skipping {0} because it is not one of the "
                             "selected fields (but its metadata is being "
                             "collected in to_image.json)".format(outvis))
                else:
                    logprint("Splitting {0}'s spw {2} to {1}".format(vis,
                                                                     outvis,
                                                                     spws[newid]),)

                    tb.open(invis)
                    if 'CORRECTED_DATA' in tb.colnames():
                        datacolumn='corrected'
                    else:
                        datacolumn='data'
                    tb.close()
                    assert split(vis=invis,
                                 spw=spws[newid],
                                 field=field,
                                 outputvis=outvis,
                                 # there is no corrected_data column because we're
                                 # splitting from split MSes
                                 datacolumn=datacolumn,
                                )

                if outvis in to_image[band][field][newid]:
                    raise ValueError()

                to_image[band][field][newid].append(outvis)


with open('to_image.json', 'w') as fh:
    json.dump(to_image, fh)

logprint("Completed line ms splitting.  Moving on to continuum splitting")

cont_mses = []
cont_mses_unconcat = []

# split the continuum data
cont_to_merge = {}
for band in bands:
    for field in all_fields:

        cont_to_merge[band] = {field: []}

        if field not in metadata[band]:
            logprint("Skipping {0}:{1} because it has no metadata"
                     .format(band, field))
            continue

        mymd = metadata[band][field]

        for path, vis, spws in zip(mymd['path'], mymd['vis'], mymd['spws']):

            if os.path.exists(os.path.join(os.getenv('ALMAIMF_ROOTDIR'), "{field}.{band}.cont.dat")):
                contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'), "{field}.{band}.cont.dat")
            else:
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
            contvis_bestsens = os.path.join(path, "continuum_"+vis+"_bsens.cont")

            cont_to_merge[band][field].append(contvis)

            if os.path.exists(contvis) and os.path.exists(contvis_bestsens):
                logprint("Skipping width determination for {0} because "
                         "it's done (both for bsens & cont)".format(contvis),)
            else:
                logprint("Determining widths for {0} to {1}"
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
                logprint("Determining smoothing widths for continuum data.  "
                         "PB_HPBW = {0}, targetwidth = {1}".format(PB_HPBW, targetwidth))
                for spw in spws:
                    chwid = np.abs(np.mean(msmd.chanwidths(spw)))
                    wid = int(targetwidth/chwid)
                    if wid <= 0:
                        logprint("Failure at chwid = {0}, wid = {1}.  ".format(chwid, wid))
                        raise ValueError("The channel width is greater than "
                                         "the target line width for spw {0} "
                                         "in ms {1}".format(spw, visfile))
                    if wid > msmd.nchan(spw) / 2:
                        # CASA *cannot* handle wid > nchan
                        # This one also insists that there will be at least 2
                        # output channels in all cases
                        wid = int(msmd.nchan(spw) / 2)
                    widths.append(wid)
                    # these are TOPO freqs: freqs[spw] = msmd.chanfreqs(spw)
                    try:
                        freqs[spw] = ms.cvelfreqs(spwid=[spw], outframe='LSRK')
                    except TypeError:
                        freqs[spw] = ms.cvelfreqs(spwids=[spw], outframe='LSRK')

                msmd.close()
                ms.close()


            if not os.path.exists(contvis) or not os.path.exists(contvis_bestsens):
                tb.open(invis)
                if 'CORRECTED_DATA' in tb.colnames():
                    datacolumn='corrected'
                else:
                    datacolumn='data'
                tb.close()


            if os.path.exists(contvis):
                logprint("Skipping {0} because it's done".format(contvis),)
            elif field not in fields:
                logprint("Skipping {0} because it is not one of the "
                         "selected fields (but its metadata is being "
                         "collected in continuum_mses.txt)".format(contvis))
            else:
                logprint("Flagging and splitting {0} to {1} for continuum"
                         .format(visfile, contvis),)


                linechannels = contchannels_to_linechannels(cont_channel_selection,
                                                            freqs)


                flagmanager(vis=visfile, mode='save',
                            versionname='before_cont_flags')

                # not clear why this is done in other imaging scripts, but it
                # seems to achieve the wrong effect.
                #initweights(vis=visfile, wtmode='weight', dowtsp=True)


                flagdata(vis=visfile, mode='manual', spw=linechannels,
                         flagbackup=False)


                flagmanager(vis=visfile, mode='save',
                            versionname='line_channel_flags')

                rmtables(contvis)
                os.system('rm -rf ' + contvis + '.flagversions')


                # Average the channels within spws
                # (assert here checks that this completes successfully)
                assert split(vis=visfile,
                             spw=",".join(map(str,spws)),
                             field=field,
                             outputvis=contvis,
                             width=widths,
                             datacolumn=datacolumn), "Split failed!"


                # If you flagged any line channels, restore the previous flags
                flagmanager(vis=visfile, mode='restore',
                            versionname='before_cont_flags')



            if os.path.exists(contvis_bestsens):
                logprint("Skipping {0} because it's done".format(contvis_bestsens),)
            elif field not in fields:
                logprint("Skipping {0} because it is not one of the "
                         "selected fields (but its metadata is being "
                         "collected in continuum_mses.txt)".format(contvis_bestsens))
            else:
                logprint("Splitting 'best-sensitivity' {0} to {1} for continuum"
                         .format(visfile, contvis_bestsens),)

                # Average the channels within spws for the "best sensitivity"
                # continuum, in which nothing is flagged out
                assert split(vis=visfile,
                             spw=",".join(map(str,spws)),
                             field=field,
                             outputvis=contvis_bestsens,
                             width=widths,
                             datacolumn=datacolumn)


        member_uid = path.split("member.")[-1].split("/")[0]
        merged_continuum_fn = os.path.join(path,
                                           "{field}_{band}_{muid}_continuum_merged.cal.ms"
                                           .format(field=field,
                                                   band=band,
                                                   muid=member_uid)
                                          )

        # merge the continuum measurement sets to ease bookkeeping
        if os.path.exists(merged_continuum_fn):
            logprint("Skipping merged continuum {0} because it's done"
                     .format(merged_continuum_fn),)
        elif field not in fields:
            logprint("Skipping {0} because it is not one of the "
                     "selected fields (but its metadata is being "
                     "collected in continuum_mses.txt)".format(merged_continuum_fn))
        else:
            logprint("Merging continuum for {0} {1} into {2}"
                     .format(merged_continuum_fn, field, band),)

            concat(vis=cont_to_merge[band][field],
                   concatvis=merged_continuum_fn,)
        cont_mses.append(merged_continuum_fn)


        # merge the best sensitivity continuum too
        merged_continuum_bsens_fn = os.path.join(
            path,
            "{field}_{band}_{muid}_continuum_merged_bsens.cal.ms"
            .format(field=field, band=band, muid=member_uid)
        )

        if os.path.exists(merged_continuum_bsens_fn):
            logprint("Skipping merged continuum bsens {0} because it's done"
                     .format(merged_continuum_bsens_fn),)
        else:
            logprint("Merging bsens continuum for {0} {1} into {2}"
                     .format(merged_continuum_bsens_fn, field, band),)

            # Note this search-and-replace pattern: we use this instead
            # of separately storing the continuum bsens MS names
            concat(vis=[x.replace(".cont", "_bsens.cont")
                        for x in cont_to_merge[band][field]],
                   concatvis=merged_continuum_bsens_fn,)

        # for debug purposes, we also track the split, unmerged MSes
        cont_mses_unconcat.append(cont_to_merge[band][field])

with open('continuum_mses.txt', 'w') as fh:
    for line in cont_mses:
        fh.write(line+'\n')

with open('continuum_mses_unconcat.txt', 'w') as fh:
    for line in cont_mses:
        fh.write(line+'\n')

with open('cont_metadata.json', 'w') as fh:
    json.dump(cont_to_merge, fh)
