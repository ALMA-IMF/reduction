import numpy as np
from __casac__ import quanta

def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)

def contchannels_to_linechannels(contsel, freqslist):

    new_sel = []

    for spw,freq in freqslist.items():
        fmin, fmax = np.min(freq), np.max(freq)
        selected = np.zeros_like(freq, dtype='bool')
        for selstr in contsel.split(";"):
            lo, hi = selstr.split("~")
            flo = quanta.convert(lo, 'Hz')['value']
            fhi = quanta.convert(hi, 'Hz')['value']

            if fhi < fmax and flo > fmin:
                selected |= (freq > flo) & (freq < fmax)

        # invert from continuum to line
        invselected = ~selected

        chans = [0] + np.where(invselected[1:] != invselected[:-1])[0].tolist() + [len(freq)-1]

        selchan = ("{0}:".format(spw) +
                   ";".join(["{0}~{1}".format(lo,hi)
                             for lo, hi in zip(chans[::2], chans[1::2])]))

        new_sel.append(selchan)

    return ",".join(new_sel)
