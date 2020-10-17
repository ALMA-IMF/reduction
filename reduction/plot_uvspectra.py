import numpy as np
import pylab as pl
import os
from astropy import log
from astropy import units as u
from astropy.io import fits
from astropy.table import Table, Column
from casatools import table, msmetadata

tb = table()
spwtb = table()
msmd = msmetadata()

def plot_uvspectra(msname, **kwargs):

    msmd.open(msname)
    tb.open(msname)
    spwtb.open(msname+"/SPECTRAL_WINDOW")

    fields = msmd.fieldnames()

    for fieldnum,fieldname in enumerate(fields):


        pl.clf()
        fig = pl.figure(1)

        #spws = msmd.spwsforfield(fieldnum)
        spws = np.unique(tb.getcol('DATA_DESC_ID'))

        spws = [spw for spw in spws
                if len(msmd.chanfreqs(spw)) > 400]

        if len(spws) == 4:
            subplots = fig.subplots(2,2).ravel()
        elif len(spws) == 5:
            subplots = fig.subplots(2,3).ravel()
        elif len(spws) < 4:
            log.error(f"TOO FEW SPWS IN {msname}")
        elif len(spws) == 8:
            subplots = fig.subplots(2,4).ravel()
        else:
            log.error(f"TOO ??? SPWS IN {msname}")

        hdul = fits.HDUList()

        ind = 0
        for spw in spws:
            # does not work: frq = msmd.chanfreqs(spw)
            frq = (spwtb.getcol('CHAN_FREQ', startrow=spw, nrow=1)).squeeze()
            if len(frq) < 100:
                continue

            stb = tb.query(f'ANTENNA1 != ANTENNA2 && FIELD_ID == {fieldnum} && DATA_DESC_ID == {spw}')
            dat = stb.getcol('DATA')
            if dat.ndim < 3:
                continue
            # axis = 0 is poln
            # axis = 1 is spec
            # axis = 2 is baseline (?)
            avgspec = dat.mean(axis=(0,2)) # axis=0 is polarization

            ax = subplots[ind]
            ax.set_xlabel("Frequency (GHz)")
            ax.set_ylabel("UV Spectrum")

            if frq.size != avgspec.size:
                #raise ValueError(f"spectrum shape = {dat.shape}, frq.shape = {frq.shape}")
                #continue
                frq = np.arange(dat.shape[1])
                ax.set_xlabel("Index")
                ax.set_ylabel("Who knows?!")
                unit = u.dimensionless_unscaled
            else:
                unit = u.Hz

            ax.plot(frq/1e9, avgspec)
            ax.set_title(f"SPW {spw}")

            spectable = Table([Column(data=frq, unit=unit, name='Frequency'),
                               Column(data=avgspec, name='Spectrum')],
                              meta={'basename': os.path.basename(msname),
                                    'fieldname': fieldname,
                                    'fieldnum': fieldnum,
                                    'spw': spw,
                                    'msname': msname,
                                   }
                             )
            hdul.append(fits.BinTableHDU(spectable))

            ind += 1

        fig.suptitle(f"field={fieldname} {fieldnum}")

        basename = os.path.basename(msname)
        fig.savefig(f"{basename}_{fieldname}_{fieldnum}_uvspectra.png")
        hdul.writeto(f"{basename}_{fieldname}_{fieldnum}_uvspectra.fits", overwrite=True)

    tb.close()
    msmd.close()
    stb.close()
    spwtb.close()


if __name__ == "__main__":

    import glob
    from pathlib import Path
    scigoals = glob.glob('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/science_goal*/')

    os.chdir('/orange/adamginsburg/ALMA_IMF/diagnostic_plots/uvspectra')

    for sg in scigoals:
        for dirpath, dirnames, filenames in os.walk(sg):
            root = Path(dirpath)
            for name in dirnames:
                if name.endswith('.ms.split.cal'):
                    fullpath = (Path(root)/Path(name))
                    print(fullpath)
                    plot_uvspectra(str(fullpath))
