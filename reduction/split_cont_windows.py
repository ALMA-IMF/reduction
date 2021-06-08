import os
import json
import time
import numpy as np

import sys

from taskinit import casalog
from taskinit import msmdtool
from taskinit import mstool, tbtool
from tasks import split, flagmanager, flagdata, rmtables, concat

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

from parse_contdotdat import parse_contdotdat, contchannels_to_linechannels # noqa: E402

msmd = msmdtool()
ms = mstool()
tb = tbtool()

# band name : frequency range (GHz)
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def logprint(string):
    casalog.post(string, origin='split_cont_windows')
    print(string)

logprint("ALMAIMF_ROOTDIR directory set to {0}".format(os.getenv('ALMAIMF_ROOTDIR')))

with open('metadata.json', 'r') as fh:
    metadata = json.load(fh)

with open('contdatfiles.json', 'r') as fh:
    contdat_files = json.load(fh)

# extract the fields from the metadata
all_fields = set(str(x) for x in metadata['B3']) | set(str(x) for x in metadata['B6'])

logprint("all_fields include: {0}".format(all_fields))

if os.getenv('FIELD_ID'):
    fields = all_fields & {os.getenv('FIELD_ID')}
else:
    fields = all_fields

logprint("fields include: {0}".format(fields))

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

            # force strings (not unicode) for CASA's benefit
            path = str(path)
            vis = str(vis)
            muid = str(muid)

            t0 = time.time()
            contfile = mymd['cont.dat'][muid]

            if not os.path.exists(contfile):
                logprint("****** No cont.dat file found for {0} = {1}:{2}.  "
                         .format(path, band, field))
                if field + band + muid in contdat_files:
                    # raise ValueError("Going to use a different cont.dat for this config?")
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
            contdat_files[field + band + muid] = contfile

            visfile = str(os.path.join(path, vis))
            contvis = str(os.path.join(path, "continuum_"+vis+".cont"))
            contvis_bestsens = str(os.path.join(path, "continuum_"+vis+"_bsens.cont"))

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
                # values interpolated by Roberto from
                # https://science.nrao.edu/facilities/vla/docs/manuals/oss2016A/performance/fov/bw-smearing
                PB_HPBW = 21. * (300. / bands[band][0]) # PB HPBW at lowest band freq
                # targetwidth = 10e6 # 10 MHz
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
                    datacolumn = 'corrected'
                else:
                    datacolumn = 'data'
                tb.close()


            if os.path.exists(contvis):
                logprint("Continuum: Skipping {0} because it's done".format(contvis),)
            elif os.path.exists(contvis_bestsens+".working"):
                logprint("Continuum: Skipping {0} because it's in progress in another thread".format(contvis),)
            elif field not in fields:
                logprint("Skipping {0} because it is not one of the "
                         "selected fields (but its metadata is being "
                         "collected in continuum_mses.txt)".format(contvis))
            else:
                logprint("Flagging and splitting {0} to {1} for continuum"
                         .format(visfile, contvis),)
                logprint("contfile is {0}".format(contfile))

                touch(contvis+".working")


                linechannels, linefracs = contchannels_to_linechannels(cont_channel_selection,
                                                            freqs,
                                                            return_fractions=True)
                logprint("Line fractions are: {0}".format(linefracs))
                logprint("Cont channels are: {0}".format(cont_channel_selection))
                logprint("Line channels are: {0}".format(linechannels))


                flagmanager(vis=visfile, mode='save',
                            versionname='before_cont_flags')

                # not clear why this is done in other imaging scripts, but it
                # seems to achieve the wrong effect.
                # initweights(vis=visfile, wtmode='weight', dowtsp=True)


                flagdata(vis=visfile, mode='manual', spw=linechannels,
                         flagbackup=False)


                flagmanager(vis=visfile, mode='save',
                            versionname='line_channel_flags')

                rmtables(contvis)
                os.system('rm -rf ' + contvis + '.flagversions')


                # Average the channels within spws
                # (assert here checks that this completes successfully)
                assert split(vis=visfile,
                             spw=",".join(map(str, spws)),
                             field=field,
                             outputvis=contvis,
                             width=widths,
                             datacolumn=datacolumn), "Split failed!"

                if not os.path.exists(contvis):
                    raise IOError("Split failed for {0}".format(contvis))

                # If you flagged any line channels, restore the previous flags
                flagmanager(vis=visfile, mode='restore',
                            versionname='before_cont_flags')

                # flag out the autocorres
                flagdata(vis=contvis, mode='manual', autocorr=True)

                os.remove(contvis+".working")


            if os.path.exists(contvis_bestsens):
                logprint("Skipping {0} because it's done".format(contvis_bestsens),)
            elif os.path.exists(contvis_bestsens+".working"):
                logprint("Skipping {0} because it's in progress in another thread".format(contvis_bestsens),)
            elif field not in fields:
                logprint("Skipping {0} because it is not one of the "
                         "selected fields (but its metadata is being "
                         "collected in continuum_mses.txt)".format(contvis_bestsens))
            else:
                logprint("Splitting 'best-sensitivity' {0} to {1} for continuum"
                         .format(visfile, contvis_bestsens),)

                touch(contvis_bestsens+".working")

                # Average the channels within spws for the "best sensitivity"
                # continuum, in which nothing is flagged out
                assert split(vis=visfile,
                             spw=",".join(map(str, spws)),
                             field=field,
                             outputvis=contvis_bestsens,
                             width=widths,
                             datacolumn=datacolumn), "Split Failed 2"
                flagdata(vis=contvis_bestsens, mode='manual', autocorr=True)

                os.remove(contvis_bestsens+".working")

            logprint("Finished splitting for {0} to {1}, {2}:{3} in {4} seconds"
                     .format(visfile, contvis, band, field, time.time() - t0))


        member_uid = str(path.split("member.")[-1].split("/")[0])
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

            assert concat(vis=cont_to_merge[band][field],
                          concatvis=merged_continuum_fn,)
            flagdata(vis=merged_continuum_fn, mode='manual', autocorr=True)
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
        elif field not in fields:
            logprint("Skipping {0} because it is not one of the "
                     "selected fields (but its metadata is being "
                     "collected in continuum_mses.txt)".format(merged_continuum_bsens_fn))
        else:
            logprint("Merging bsens continuum for {0} {1} into {2}"
                     .format(merged_continuum_bsens_fn, field, band),)

            # Note this search-and-replace pattern: we use this instead
            # of separately storing the continuum bsens MS names
            assert concat(vis=[x.replace(".cont", "_bsens.cont")
                               for x in cont_to_merge[band][field]],
                          concatvis=merged_continuum_bsens_fn,)
            flagdata(vis=merged_continuum_fn, mode='manual', autocorr=True)

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

logprint("Completed split_cont_windows")
