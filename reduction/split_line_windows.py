import os
import json

import sys

from taskinit import casalog
from taskinit import msmdtool
from taskinit import mstool, tbtool
from tasks import split, flagdata


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

msmd = msmdtool()
ms = mstool()
tb = tbtool()

# band name : frequency range (GHz)
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


def logprint(string):
    casalog.post(string, origin='split_line_windows')
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

logprint("Splitting fields {0}".format(fields))

if os.path.exists('to_image.json'):
    with open('to_image.json', 'r') as fh:
        to_image = json.load(fh)
else:
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
                base_uid = str(vis.split(".")[0])
                invis = str(os.path.join(path, vis))
                outvis = str(os.path.join(path,
                                      "{base_uid}_{field}_{band}_spw{spw}.split"
                                      .format(band=band, field=field,
                                              spw=newid, base_uid=base_uid)))

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
                        datacolumn = 'corrected'
                    else:
                        datacolumn = 'data'
                    tb.close()

                    # verify that no channels are flagged in the input data
                    # (no channel-based flagging is performed by the ALMA pipeline or by
                    # the ALMA-IMF pipeline; there is no technical reason channels should
                    # ever be flagged)
                    check_channel_flags(invis, field=field, spw=spws[newid])

                    assert split(vis=invis,
                                 spw=spws[newid],
                                 field=field,
                                 outputvis=outvis,
                                 # there is no corrected_data column because we're
                                 # splitting from split MSes
                                 datacolumn=datacolumn,
                                ), "Split failed 3"

                    flagdata(vis=outvis, mode='manual', autocorr=True)

                if outvis in to_image[band][field][newid]:
                    raise ValueError()

                to_image[band][field][newid].append(outvis)


with open('to_image.json', 'w') as fh:
    json.dump(to_image, fh)

logprint("Completed line ms splitting.")
