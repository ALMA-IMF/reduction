import numpy as np
import string
from __casac__.quanta import quanta
from taskinit import msmdtool
qq = quanta()

def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)

def contchannels_to_linechannels(contsel, freqslist):
    """
    Parameters
    ----------
    contsel : str
        A CASA selection string with assumed units of frequency and no assumed
        spectral windows.
    freqslist : dict
        A dictionary of frequency arrays, where the key is the spectral window
        number and the value is a numpy array of frequencies
    """

    new_sel = []

    for spw,freq in freqslist.items():
        fmin, fmax = np.min(freq), np.max(freq)
        if fmin > fmax:
            fmin,fmax = fmax,fmin
        selected = np.zeros_like(freq, dtype='bool')
        for selstr in contsel.split(";"):
            lo, hi = selstr.strip(string.ascii_letters).split("~")
            unit = selstr.lstrip(string.punctuation + string.digits)
            flo = qq.convert({'value':float(lo), 'unit':unit}, 'Hz')['value']
            fhi = qq.convert({'value':float(hi), 'unit':unit}, 'Hz')['value']

            if fhi < fmax and flo > fmin:
                selected |= (freq > flo) & (freq < fhi)


        # invert from continuum to line
        invselected = ~selected

        chans = ([0] +
                 np.where(invselected[1:] !=
                                invselected[:-1])[0].tolist() +
                 [len(freq)-1])

        selchan = ("{0}:".format(spw) +
                   ";".join(["{0}~{1}".format(lo,hi)
                             for lo, hi in zip(chans[::2], chans[1::2])]))

        new_sel.append(selchan)

    return ",".join(new_sel)

def freq_selection_overlap(ms, freqsel, spw=0):
    """
    For a given frequency selection string (e.g., '215~216GHz;900~950GHz'),
    find the subset of the `;`-separated entries that overlap with the
    measurement set and return those.

    Parameters
    ----------
    ms : str
        The name of a measurement set to compare against
    freqsel : str
        A frequency-based selection string
    spw : int
        The spectral window number, default to 0
    """

    msmd = msmdtool()
    msmd.open(ms)
    frequencies_in_ms = msmd.chanfreqs(spw)
    msmd.close()

    fmin, fmax = frequencies_in_ms.min(), frequencies_in_ms.max()

    new_sel = []

    for selstr in freqsel.split(";"):
        lo, hi = map(float, selstr.strip(string.ascii_letters).split("~"))
        unit = selstr.lstrip(string.punctuation + string.digits)
        if lo > hi:
            lo, hi = hi, lo

        flo = qq.convert({'value':float(lo), 'unit':unit}, 'Hz')['value']
        fhi = qq.convert({'value':float(hi), 'unit':unit}, 'Hz')['value']

        if (fhi < fmax) or (flo > fmin):
            new_sel.append(selstr)

    return ";".join(new_sel)
