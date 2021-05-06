"""
Script to determine the central frequency of our observations
"""
import glob
import pyspeckit
import numpy as np
import string

import os
import json
import time
import numpy as np

import sys

try:
    from casatools import msmetadata, table, ms
    msmd = msmetadata()
    ms = ms()
    tb = table()
    from casatasks import casalog
except:
    from taskinit import casalog
    from taskinit import msmdtool, tbtool, mstool
    msmd = msmdtool()
    ms = mstool()
    tb = tbtool()


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

from parse_contdotdat import parse_contdotdat, contchannels_to_linechannels, qq # noqa: E402


# band name : frequency range (GHz)
bands = {'B3': (80, 110),
         'B6': (210, 250),
        }


def logprint(string):
    casalog.post(string, origin='central_frequency')
    print(string)

logprint("ALMAIMF_ROOTDIR directory set to {0}".format(os.getenv('ALMAIMF_ROOTDIR')))

with open('metadata.json', 'r') as fh:
    metadata = json.load(fh)

with open('contdatfiles.json', 'r') as fh:
    contdat_files = json.load(fh)

# extract the fields from the metadata
all_fields = set(str(x) for x in metadata['B3']) | set(str(x) for x in metadata['B6'])

logprint("all_fields include: {0}".format(all_fields))

avgfreqs = {'B3': {}, 'B6': {}}

alphas = (0, 2, 2.5, 3, 3.5, 4)

for band in bands:
    for field in all_fields:

        if field not in metadata[band]:
            logprint("Skipping {0}:{1} because it has no metadata"
                     .format(band, field))
            continue
        else:
            logprint("Processing continuum for {0}:{1} because it has metadata"
                     .format(band, field))

        mymd = metadata[band][field]

        #logprint("Metadata for {0}:{1} is {2}".format(band, field, mymd))

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

            visfile = str(os.path.join(path, vis))

            msmd.open(visfile)
            ms.open(visfile)
            freqs = {}
            for spw in spws:
                try:
                    freqs[spw] = ms.cvelfreqs(spwid=[spw], outframe='LSRK')
                except TypeError:
                    freqs[spw] = ms.cvelfreqs(spwids=[spw], outframe='LSRK')

            msmd.close()
            ms.close()

            cont_selected = {}

            contsel = cont_channel_selection
            for spw,freq in freqs.items():
                fmin, fmax = np.min(freq), np.max(freq)
                if fmin > fmax:
                    raise ValueError("this is literally impossible")

                selected = np.zeros_like(freq, dtype='bool')
                for selstr in contsel.split(";"):
                    lo, hi = selstr.strip(string.ascii_letters).split("~")
                    unit = selstr.lstrip(string.punctuation + string.digits)
                    flo = qq.convert({'value':float(lo), 'unit':unit}, 'Hz')['value']
                    fhi = qq.convert({'value':float(hi), 'unit':unit}, 'Hz')['value']
                    if flo > fhi:
                        flo,fhi = fhi,flo

                    # only include selections that are at least partly in range
                    if fmin < fhi < fmax or fmax > flo > fmin:
                        selected |= (freq > flo) & (freq < fhi)
                    # but also allow for the case where EVERYTHING is included
                    elif fhi > fmax and flo < fmin:
                        selected[:] = True

                    cont_selected[spw] = selected

            avgfreqs[band][field] = {'bsens': {}, 'cleanest': {}}

            for alpha in alphas:
                bsensfreqs = np.hstack([freqs[spw] for spw in freqs])
                cleanestfreqs = np.hstack([freqs[spw][cont_selected[spw]] for spw in freqs])
                chwids_bsens = np.hstack([np.ones_like(freqs[spw]) *
                                          np.abs(np.mean(np.diff(freqs[spw])))
                                          for spw in freqs])
                chwids_cleanest = chwids_bsens[np.hstack([cont_selected[spw] for spw in freqs])]

                avgfreqs[band][field]['bsens'][alpha] = np.average(bsensfreqs, weights=chwids_bsens*bsensfreqs**alpha)
                avgfreqs[band][field]['cleanest'][alpha] = np.average(cleanestfreqs, weights=chwids_cleanest*cleanestfreqs**alpha)
            print(band, field, avgfreqs[band][field])


tabledir = os.environ['ALMAIMF_ROOTDIR']+"../../datapaper"

alphas = (0, 2, 3, 3.5, 4)
with open(f'{tabledir}/band_freqs.tex', 'w') as fh:

    fh.write(r"""
\begin{table*}
\caption{Central Frequencies}
""")
    nalpha = len(alphas)
    fh.write(f"\\begin{{tabular}}{{{'l'+'r'*(nalpha*2)}}}\n")
    fh.write(r"\label{tab:centralfreqs}\n")
    fh.write(f"& \\multicolumn{{{nalpha*2}}}{{c}}{{\\bsens}} \\\\\n")
    fh.write(f"& \\multicolumn{{{nalpha}}}{{c}}{{B3}} & \\multicolumn{{{nalpha}}}{{c}}{{B6}} \\\\\n")
    fh.write("Field & " + " & ".join(map(str,alphas * 2)) + "\\\\\n")
    fh.write(r"\hline\\" + "\n")
    for field in all_fields:
        fh.write(" & ".join([f"{field:12s}"] +
                            ([f"{avgfreqs['B3'][field]['bsens'][alpha]/1e9:10.3f}" for alpha in alphas] if field in avgfreqs['B3'] else [" "*10]*5) +
                            ([f"{avgfreqs['B6'][field]['bsens'][alpha]/1e9:10.3f}" for alpha in alphas] if field in avgfreqs['B6'] else [" "*10]*5)
                           )
                 + "\\\\\n")

    fh.write(r"\hline\\" + "\n")
    fh.write(r"\hline\\" + "\n")
    fh.write(f"& \\multicolumn{{{nalpha*2}}}{{c}}{{\\cleanest}} \\\\\n")
    fh.write(f"& \\multicolumn{{{nalpha}}}{{c}}{{B3}} & \\multicolumn{{{nalpha}}}{{c}}{{B6}} \\\\\n")
    fh.write("Field & " + " & ".join(map(str,alphas)) * 2 + "\\\\\n")
    fh.write(r"\hline\\" + "\n")
    for field in all_fields:
        fh.write(" & ".join([f"{field:12s}"] +
                            ([f"{avgfreqs['B3'][field]['cleanest'][alpha]/1e9:10.3f}" for alpha in alphas] if field in avgfreqs['B3'] else [" "*10]*5) +
                            ([f"{avgfreqs['B6'][field]['cleanest'][alpha]/1e9:10.3f}" for alpha in alphas] if field in avgfreqs['B6'] else [" "*10]*5)
                           )
                 + "\\\\\n")

    fh.write("\end{tabular}\n")
    fh.write("\par All frequencies given in GHz.  Headings give the spectral index $\\alpha$.\n")
    fh.write("\end{table*}\n")

