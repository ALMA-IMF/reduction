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
can specify an override by creating a file "{field}.{band}.cont.dat" in the
ALMAIMF_ROOTDIR directory.  For example, if you wanted to override the cont.dat
file for field "ORION" in band 9, you would create a file called
ORION.B9.cont.dat. Note that the names are case sensitive.
"""
import os
import glob
import json
import numpy as np

import sys

from_cmd = False
# If run from command line
if len(sys.argv) > 2:
    aux = os.path.dirname(sys.argv[2])
    if os.path.isdir(aux):
        almaimf_rootdir = aux
        from_cmd = True


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

logprint("ALMAIMF_ROOTDIR directory set to {0}".format(os.getenv('ALMAIMF_ROOTDIR')))

metadata = {b:{} for b in bands}
contdat_files = {}

science_goals = glob.glob("science_goal*")

for sg in science_goals:
    # walk only the science goals: walking other directories can be extremely
    # inefficient
    for dirpath, dirnames, filenames in os.walk(sg):
        if dirpath.count(os.path.sep) >= 5:
            # skip over things below the sci/gro/mou/<blah>/* level
            continue
        for fn in dirnames:
            if fn[-10:] == ".split.cal":

                logprint("Collecting metadata for {0} in {1}".format(fn, dirpath))

                filename = os.path.join(dirpath, fn)
                msmd.open(filename)

                antnames = msmd.antennanames()
                fieldnames = np.array(msmd.fieldnames())
                field = fieldnames[msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')]
                assert len(np.unique(field)) == 1,"ERROR: field={0} fieldnames={1}".format(field, fieldnames)
                field = field[0]

                frq0 = msmd.chanfreqs(0)
                for bb,(lo, hi) in bands.items():
                    try:
                        if lo*1e9 < frq0 and hi*1e9 > frq0:
                            band = bb
                    except ValueError:
                        if lo*1e9 < np.min(frq0) and hi*1e9 > np.max(frq0):
                            band = bb


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

                spws = msmd.spwsforfield(field)
                targetspws = msmd.spwsforintent('OBSERVE_TARGET*')
                # this is how DOSPLIT in scriptForPI decides to split
                spws = [int(ss) for ss in spws if (ss in targetspws) and (msmd.nchan(ss) > 4)]

                # muid is 1 level above calibrated
                muid = dirpath.split("/")[-2]

                frqs = [msmd.chanfreqs(spw) for spw in spws]
                frqslims = [(frq.min(), frq.max()) for frq in frqs]

                if field in metadata[band]:
                    metadata[band][field]['path'].append(os.path.abspath(dirpath)),
                    metadata[band][field]['vis'].append(fn)
                    metadata[band][field]['spws'].append(spws)
                    metadata[band][field]['freqs'].append(frqslims)
                    metadata[band][field]['muid'].append(muid)
                else:
                    metadata[band][field] = {'path': [os.path.abspath(dirpath)],
                                             'vis': [fn],
                                             'spws': [spws],
                                             'freqs': [frqslims],
                                             'muid': [muid],
                                            }

                ran_findcont = False
                pipescript = glob.glob("../script/*casa_pipescript.py")
                if len(pipescript) > 0:
                    for pscr in pipescript:
                        with open(pscr, 'r') as fh:
                            txt = fh.read()
                        if 'findcont' in txt:
                            ran_findcont = True
                ran_findcont = "ran_findcont" if ran_findcont else "did_not_run_findcont"

                tb.open(filename+"/ANTENNA")
                positions = tb.getcol('POSITION')
                tb.close()
                baseline_lengths = (((positions[None,:,:]-positions.T[:,:,None])**2).sum(axis=1)**0.5)
                max_bl = int(np.max(baseline_lengths))

                lb_threshold = {'B3': 750,
                                'B6': 780,}
                array_config = ('7M' if max_bl < 100
                                else '12Mshort' if max_bl < lb_threshold[band]
                                else '12Mlong')

                if 'muid_configs' in metadata[band][field]:
                    metadata[band][field]['muid_configs'][array_config] = muid
                else:
                    metadata[band][field]['muid_configs'] = {array_config: muid}

                contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                        "{field}.{band}.{array}.cont.dat".format(field=field, band=band, array=array_config.lower()))
                if os.path.exists(contfile):
                    logprint("##### Found manually-created cont.dat file {0}".format(contfile))
                else:
                    contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                            "{field}.{band}.cont.dat".format(field=field, band=band))
                    if os.path.exists(contfile):
                        logprint("##### Found manually-created cont.dat file {0}".format(contfile))
                    else:
                        contfile = os.path.join(dirpath, '../calibration/cont.dat')

                if os.path.exists(contfile):
                    contdatpath = os.path.realpath(contfile)
                    contdat_files[field + band + muid] = contdatpath

                    if 'cont.dat' in metadata[band][field]:
                        metadata[band][field]['cont.dat'][max_bl] = contdatpath
                    else:
                        metadata[band][field]['cont.dat'] = {max_bl: contdatpath}
                else:
                    if 'cont.dat' in metadata[band][field]:
                        if max_bl in metadata[band][field]['cont.dat']:
                            logprint("*** Found DUPLICATE KEY={max_bl} in cont.dat metadata for band={band} field={field}"
                                     .format(max_bl=max_bl, band=band, field=field))
                        else:
                            metadata[band][field]['cont.dat'][max_bl] = 'notfound_'+ ran_findcont
                    else:
                        metadata[band][field]['cont.dat'] = {max_bl: 'notfound_'+ ran_findcont}
                    contdat_files[field + band + muid] = 'notfound_'+ ran_findcont

                # touch the filename
                with open(os.path.join(dirpath, "{0}_{1}_{2}".format(field, band, array_config)), 'w') as fh:
                    fh.write("{0}".format(antnames))
                logprint("Acquired metadata for {0} in {1}_{2}_{3} successfully"
                         .format(fn, field, band, array_config))


                msmd.close()

with open('metadata.json', 'w') as fh:
    json.dump(metadata, fh)

with open('contdatfiles.json', 'w') as fh:
    json.dump(contdat_files, fh)

logprint("Completed metadata assembly")

# extract the fields from the metadata
all_fields = set(str(x) for x in metadata['B3']) | set(str(x) for x in metadata['B6'])

logprint("all_fields include: {0}".format(all_fields))

if os.getenv('FIELD_ID'):
    fields = all_fields & {os.getenv('FIELD_ID')}
else:
    fields = all_fields

logprint("Splitting fields {0}".format(fields))

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
    cont_to_merge[band] = {}
    for field in all_fields:

        cont_to_merge[band][field] = []

        if field not in metadata[band]:
            logprint("Skipping {0}:{1} because it has no metadata"
                     .format(band, field))
            continue
        else:
            logprint("Processing continuum for {0}:{1} because it has metadata"
                     .format(band, field))

        mymd = metadata[band][field]

        logprint("Metadata for {0}:{1} is {2}".format(band, field, mymd))

        for path, vis, spws, muid in zip(mymd['path'], mymd['vis'], mymd['spws'], mymd['muid']):

            contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                    "{field}.{band}.cont.dat".format(field=field, band=band))
            if os.path.exists(contfile):
                logprint("##### Found manually-created cont.dat file {0}".format(contfile))
            else:
                # the cont.dat file should be in the calibration/ directory in the
                # same SB folder
                logprint("Did not find a manually-created cont.dat file named {0}; instead using local cont.dat.".format(contfile))
                contfile = os.path.join(path, '../calibration/cont.dat')
                logprint("Using cont.dat file {0} for {1}:{2}".format(contfile,
                                                                      band,
                                                                      field))

            if not os.path.exists(contfile):
                logprint("****** No cont.dat file found for {0} = {1}:{2}.  "
                         .format(path, band, field))
                if field + band + muid in contdat_files:
                    #raise ValueError("Going to use a different cont.dat for this config?")
                    contfile = contdat_files[field + band + muid]
                    if not os.path.exists(contfile):
                        logprint("No cont.dat file: Skipping - this file will not be included in the merged continuum.")
                        continue
                    else:
                        logprint("No cont.dat file: Using {0} instead.".format(contfile))
                else:
                    logprint("No cont.dat file: Skipping - this file will not be included in the merged continuum.")
                    continue
            cont_channel_selection = parse_contdotdat(contfile)
            mymd['cont.dat_file'] = contfile
            contdat_files[field + band + muid] = contdatpath

            visfile = os.path.join(path, vis)
            contvis = os.path.join(path, "continuum_"+vis+".cont")
            contvis_bestsens = os.path.join(path, "continuum_"+vis+"_bsens.cont")

            cont_to_merge[band][field].append(contvis)

            if os.path.exists(contvis) and os.path.exists(contvis_bestsens):
                logprint("Skipping width determination for {0} = {1}:{2} because "
                         "it's done (both for bsens & cont)".format(contvis, band, field),)
            else:
                logprint("Determining widths for {0} to {1}, {2}:{3}"
                         .format(visfile, contvis, band, field),)

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
                tb.open(visfile)
                if 'CORRECTED_DATA' in tb.colnames():
                    datacolumn='corrected'
                else:
                    datacolumn='data'
                tb.close()


            if os.path.exists(contvis):
                logprint("Continuum: Skipping {0} because it's done".format(contvis),)
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

                if not os.path.exists(contvis):
                    raise IOError("Split failed for {0}".format(contvis))

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
        cont_mses_unconcat += cont_to_merge[band][field]

with open('continuum_mses.txt', 'w') as fh:
    for line in cont_mses:
        fh.write(line+'\n')

with open('continuum_mses_unconcat.txt', 'w') as fh:
    for line in cont_mses_unconcat:
        fh.write(line+'\n')

with open('cont_metadata.json', 'w') as fh:
    json.dump(cont_to_merge, fh)

with open('metadata_updated.json', 'w') as fh:
    json.dump(metadata, fh)

with open('contdatfiles_updated.json', 'w') as fh:
    json.dump(contdat_files, fh)

logprint("Completed split_windows")
