import os
import glob
import json
import time
import numpy as np

import sys

try:
    from taskinit import casalog
    from taskinit import msmdtool
    from taskinit import mstool, tbtool
except (ImportError,ModuleNotFoundError):
    # futureproofing: CASA 6 imports this way
    from casatasks import casalog
    from casatools import msmetadata as msmdtool
    from casatoosl import ms as mstool
    from casatools import table as tbtool

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
from get_array_config import get_array_config

msmd = msmdtool()
ms = mstool()
tb = tbtool()

# band name : frequency range (GHz)
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


def logprint(string):
    casalog.post(string, origin='assemble_ms_metadata')
    print(string)

logprint("ALMAIMF_ROOTDIR directory set to {0}".format(os.getenv('ALMAIMF_ROOTDIR')))

metadata = {b: {} for b in bands}
contdat_files = {}

science_goals = glob.glob("science_goal*")

t1 = time.time()

for sg in science_goals:
    # walk only the science goals: walking other directories can be extremely
    # inefficient
    t2 = time.time()
    for dirpath, dirnames, filenames in os.walk(sg):
        if dirpath.count(os.path.sep) >= 5:
            # skip over things below the sci/gro/mou/<blah>/* level
            continue
        for fn in sorted(dirnames):
            if fn[-10:] == ".split.cal":

                logprint("Spent {0} walking paths between metadata collection steps".format(time.time() - t2))

                t0 = time.time()
                logprint("Collecting metadata for {0} in {1}; t0={2}".format(fn, dirpath, t0))

                filename = os.path.join(dirpath, fn)
                msmd.open(filename)

                antnames = msmd.antennanames()
                fieldnames = np.array(msmd.fieldnames())
                field = fieldnames[msmd.fieldsforintent('OBSERVE_TARGET#ON_SOURCE')]
                assert len(np.unique(field)) == 1, "ERROR: field={0} fieldnames={1}".format(field, fieldnames)
                field = field[0]

                frq0 = msmd.chanfreqs(0)
                for bb, (lo, hi) in bands.items():
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
                        logprint("Skipping total power MS {0} [Elapsed: {1}]".format(fn, time.time()-t0))
                        msmd.close()
                        continue
                    else:
                        logprint("WARNING: MS {0} contains PM antennae but is apparently not a TP data set".format(fn))

                try:
                    summary = msmd.summary()
                except RuntimeError:
                    logprint("Skipping FAILED MS {0} [Elapsed: {1}]".format(fn, time.time() - t0))
                    msmd.close()
                    continue

                logprint("NOT skipping ms {0} [Elapsed: {1}]".format(fn, time.time() - t0))
                spws = msmd.spwsforfield(field)
                targetspws = msmd.spwsforintent('OBSERVE_TARGET*')
                # this is how DOSPLIT in scriptForPI decides to split
                spws = [int(ss) for ss in spws if (ss in targetspws) and (msmd.nchan(ss) > 4)]

                # muid is 1 level above calibrated
                muid = dirpath.split("/")[-2]

                # need the full ms to get LSRK frequencies
                ms.open(filename)
                try:
                    frqs = [ms.cvelfreqs(spwid=[spw], outframe='LSRK') for spw in spws]
                    frqdict = {spw: ms.cvelfreqs(spwid=[spw], outframe='LSRK') for spw in spws}
                except TypeError:
                    frqs = [ms.cvelfreqs(spwids=[spw], outframe='LSRK') for spw in spws]
                    frqdict = {spw: ms.cvelfreqs(spwids=[spw], outframe='LSRK') for spw in spws}
                ms.close()

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
                baseline_lengths = (((positions[None, :, :]-positions.T[:, :, None])**2).sum(axis=1)**0.5)
                max_bl = int(np.max(baseline_lengths))

                lb_threshold = {'B3': 750,
                                'B6': 780,
                               }
                array_config = ('7M' if max_bl < 100
                                else '12Mshort' if max_bl < lb_threshold[band]
                                else '12Mlong')

                if 'muid_configs' in metadata[band][field]:
                    metadata[band][field]['muid_configs'][array_config] = muid
                    metadata[band][field]['max_bl'][muid] = max_bl
                else:
                    metadata[band][field]['muid_configs'] = {array_config: muid}
                    metadata[band][field]['max_bl'] = {muid: max_bl}

                # add the named array configurations to the metadata file
                try:
                    obstime, named_array_config = get_array_config(filename)
                    obstime = obstime.strftime('%Y-%m-%d')
                except Exception as ex:
                    print(ex)
                    obstime = 'never'
                    named_array_config = 'unknown'
                if 'array_config_name' in metadata[band][field]:
                    metadata[band][field]['array_config_name'][obstime] = named_array_config
                else:
                    metadata[band][field]['array_config_name'] = {obstime: named_array_config}

                # Custom cont.dat files:
                # <field>.<band>.<array>.cont.dat takes priority; if that exists, it will be used
                # else if
                # <field>.<band>.cont.dat exists, it will be used.
                # we only have 12m and 7m now; everything is otherwise merged
                # (though maybe we'll merge further still)
                arrayname = '12m' if '12M' in array_config else '7m'
                contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                        'contdat',
                                        "{field}.{band}.{array}.cont.dat".format(field=field, band=band,
                                                                                 array=arrayname))
                if os.path.exists(contfile):
                    logprint("##### Found manually-created cont.dat file {0}".format(contfile))
                else:
                    contfile = os.path.join(os.getenv('ALMAIMF_ROOTDIR'),
                                            'contdat',
                                            "{field}.{band}.cont.dat".format(field=field, band=band))
                    if os.path.exists(contfile):
                        logprint("##### Found manually-created cont.dat file {0}".format(contfile))
                    else:
                        contfile = os.path.join(dirpath, '../calibration/cont.dat')

                if os.path.exists(contfile):
                    contdatpath = os.path.realpath(contfile)
                    contdat_files[field + band + muid] = contdatpath

                    cont_channel_selection = parse_contdotdat(contdatpath)
                    _, linefracs = contchannels_to_linechannels(cont_channel_selection,
                                                                frqdict,
                                                                return_fractions=True)


                    if 'cont.dat' in metadata[band][field]:
                        metadata[band][field]['cont.dat'][muid] = contdatpath
                        metadata[band][field]['line_fractions'].append(linefracs)
                    else:
                        metadata[band][field]['cont.dat'] = {muid: contdatpath}
                        metadata[band][field]['line_fractions'] = [linefracs]
                else:
                    if 'cont.dat' in metadata[band][field]:
                        if muid in metadata[band][field]['cont.dat']:
                            logprint("*** Found DUPLICATE KEY={muid},{max_bl}"
                                     " in cont.dat metadata for band={band} field={field}"
                                     .format(max_bl=max_bl, muid=muid,
                                             band=band, field=field))
                        else:
                            metadata[band][field]['cont.dat'][muid] = 'notfound_' + ran_findcont
                    else:
                        metadata[band][field]['cont.dat'] = {muid: 'notfound_' + ran_findcont}
                    contdat_files[field + band + muid] = 'notfound_' + ran_findcont



                # touch the filename
                with open(os.path.join(dirpath, "{0}_{1}_{2}".format(field, band, array_config)), 'w') as fh:
                    fh.write("{0}".format(antnames))
                logprint("Acquired metadata for {0} in {1}_{2}_{3} successfully [Elapsed: {4}]"
                         .format(fn, field, band, array_config, time.time() - t0))
                t2 = time.time()


                msmd.close()


with open('metadata.json', 'w') as fh:
    json.dump(metadata, fh)

with open('contdatfiles.json', 'w') as fh:
    json.dump(contdat_files, fh)

logprint("Completed metadata assembly")
logprint("Metadata acquisition took {0} seconds".format(time.time() - t1))
