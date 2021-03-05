import numpy as np
from astropy.table import Table
from casatools import msmetadata, ms
import glob
import pylab as pl
from astropy import units as u

def make_figure(data, wavelength, beam_to_bl, bins=50):
    pl.figure(figsize=(8,4))
    ax1 = pl.subplot(1,2,1)
    _=pl.hist(np.concatenate([data[spw]['uvdist'][~data[spw]['flag'].any(axis=(0,1))] for spw in data]).ravel(), bins=bins)
    _=pl.xlabel('Baseline Length (m)')
    _=pl.ylabel("Number of Visibilities")
    yl = pl.ylim()
    pl.fill_betweenx(yl, beam_to_bl[0].value, beam_to_bl[1].value, zorder=-5, color='orange', alpha=0.5)
    pl.ylim(yl)
    ax1t = ax1.secondary_xaxis('top', functions=(lambda x: x/1e3/wavelength.to(u.m).value, lambda x:x/1e3/wavelength.to(u.m).value))
    ax1t.set_xlabel("Baseline Length (k$\lambda$)")
    #ax1t.set_ticks(np.linspace(1000,100000,10))
    ax2 = pl.subplot(1,2,2)
    _=pl.hist(np.concatenate([data[spw]['uvdist'][~data[spw]['flag'].any(axis=(0,1))] for spw in data]).ravel(),
            weights=np.concatenate([data[spw]['weight'].mean(axis=0)[~data[spw]['flag'].any(axis=(0,1))] for spw in data]).ravel(),
            bins=bins, density=True)
    _=pl.xlabel('Baseline Length (m)')
    _=pl.ylabel("Fractional Weight")
    def forward(x):
        return (wavelength.to(u.m)/(x*u.arcsec)).to(u.m, u.dimensionless_angles()).value
    def inverse(x):
        return (wavelength.to(u.m)/(x*u.m)).to(u.arcsec, u.dimensionless_angles()).value
    ax2t = ax2.secondary_xaxis('top', functions=(forward, inverse))
    ax2t.set_xlabel("Angular size $\lambda/D$ (arcsec)")
    if ax2.get_xlim()[1] > 1000:
        ax2t.set_ticks([10,1,0.5,0.4,0.3,0.2,0.1])
    elif ax2.get_xlim()[1] > 600:
        ax2t.set_ticks([10,2,1,0.6,0.5,0.4,0.3])
    else:
        ax2t.set_ticks([10,2,1,0.8,0.7,0.6,0.2])
    yl = pl.ylim()
    pl.fill_betweenx(yl, beam_to_bl[0].value, beam_to_bl[1].value, zorder=-5, color='orange', alpha=0.5)
    pl.ylim(yl)
    #pl.subplots_adjust(wspace=0.3)
    pl.tight_layout()

if  __name__ == "__main__":
    tbl = Table.read('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/February2021Release/tables/metadata_image.tt0.ecsv')


    mslist = {(row['region'],row['band']): {'msname': glob.glob(f'/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/{row["region"]}_{row["band"]}*_12M_selfcal.ms'),
                                            'beam': (row['bmaj'], row['bmin'])}
            for row in tbl if row['robust'] == 'r0.0' and row['suffix'] == 'finaliter' and not row['bsens']}

    msmd = msmetadata()
    ms = ms()

    for (region, band) in mslist:

        if len(mslist[(region,band)]['msname']) == 1:
            msname = mslist[(region,band)]['msname'][0]
        else:
            raise ValueError('msname borked')

        msmd.open(msname)
        spws = msmd.spwsforfield(region)
        freqs = np.concatenate([msmd.chanfreqs(spw) for spw in spws])
        freqweights = np.concatenate([msmd.chanfreqs(spw) for spw in spws])
        msmd.close()

        avfreq = np.average(freqs, weights=freqweights)
        wavelength = (avfreq*u.Hz).to(u.m, u.spectral())          

        data = {}
        for spw in spws:
            ms.open(msname)
            ms.selectinit(spw)
            data[spw] = ms.getdata(items=['weight', 'uvdist', 'flag'])
            ms.close()

        beam = mslist[(region,band)]['beam']*u.arcsec
        beam_to_bl = (wavelength / beam).to(u.m, u.dimensionless_angles())

        make_figure(data, wavelength, beam_to_bl)
        pl.savefig(f'/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/paper_figures/uvhistograms/{region}_{band}_uvhistogram.pdf', bbox_inches='tight')