import numpy as np
import pylab as pl
import os
from astropy import log
from casatools import table, msmetadata

tb = table()
msmd = msmetadata()

def plot_autocorrelations(msname, **kwargs):

    msmd.open(msname)
    tb.open(msname)

    fields = msmd.fieldnames()

    for fieldnum,fieldname in enumerate(fields):


        pl.clf()
        fig = pl.figure(1)

        spws = msmd.spwsforfield(fieldnum)

        spws = [spw for spw in spws
                if len(msmd.chanfreqs(spw)) > 400]

        if len(spws) == 4:
            subplots = fig.subplots(2,2).ravel()
        elif len(spws) < 4:
            log.error(f"TOO FEW SPWS IN {msname}")
        elif len(spws) < 10:
            subplots = fig.subplots(3,3).ravel()
        else:
            print(f"Found spws {spws}")
            subplots = fig.subplots(3,3).ravel()

        ind = 0
        for spw in spws:
            frq = msmd.chanfreqs(spw)
            if len(frq) < 100:
                continue

            stb = tb.query(f'ANTENNA1 == ANTENNA2 && FIELD_ID == {fieldnum} && DATA_DESC_ID == {spw}')
            dat = stb.getcol('DATA')
            if dat.ndim < 3:
                continue
            avgspec = dat.mean(axis=2) # axis=2 is polarization

            if frq.size != avgspec.shape[1]:
                raise ValueError(f"spectrum shape = {dat.shape}, frq.shape = {frq.shape}")
                continue

            ax = subplots[ind]
            ax.plot(frq/1e9, avgspec.T)
            ax.set_xlabel("Frequency (GHz)")
            ax.set_ylabel("Autocorr")
            ax.set_title(f"SPW {spw}")

            ind += 1

        fig.suptitle(fieldname)

        basename = os.path.basename(msname)
        fig.savefig(f"{basename}_{fieldname}.png")

    tb.close()
    msmd.close()
    stb.close()


if __name__ == "__main__":

    import glob
    from pathlib import Path
    scigoals = glob.glob('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/science_goal*/')

    os.chdir('/orange/adamginsburg/ALMA_IMF/diagnostic_plots')

    for sg in scigoals:
        for dirpath, dirnames, filenames in os.walk(sg):
            root = Path(dirpath)
            for name in dirnames:
                if name.endswith('.ms.split.cal'):
                    fullpath = (Path(root)/Path(name))
                    print(fullpath)
                    plot_autocorrelations(str(fullpath))
