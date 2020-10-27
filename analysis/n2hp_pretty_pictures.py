import numpy as np
from astropy import units as u
from spectral_cube import SpectralCube
from astropy import visualization
import pylab as pl

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults'

colorslices = {'W51-IRS2': {'b': (46, 52), 'g': (52, 58), 'r': (59, 65)},
               'W51-E': {'b': (46, 52), 'g': (52, 58), 'r': (59, 65)},
               'G010.62': {'b': (-6, -2.5), 'g': (-2.5, 0), 'r': (0, 4)},
               'G012.80': {'b': (32,36), 'g': (36,40), 'r': (40,44)},
               'G327.29': {'b': (-55,-51), 'g': (-51,-49), 'r': (-49,-46)},
               'G328.25': {'b': (-50,-46), 'g': (-46,-44), 'r': (-44,-41)},
               'G333.60': {'b': (-52,-49), 'g': (-49,-46), 'r': (-46,-43)},
               'G337.92': {'b': (-41.5,-39), 'g': (-39,-36.5), 'r': (-36.5,-35)},
               'G338.93': {'b': (-68.5,-66), 'g': (-66,-63.5), 'r': (-63.5,-61)},
              }

band = 'B3'

for field in colorslices:
    pl.figure(figsize=(20,20))

    filepath = f'{basepath}/{field}/{band}/linecubes_12m/{field}_{band}_spw0_12M_n2hp.image'

    n2hc = SpectralCube.read(filepath).with_spectral_unit(u.km/u.s, velocity_convention='radio')
    n2hc = n2hc.rechunk((10,)+n2hc.shape[1:])

    moment_slabs = {color: n2hc.spectral_slab(vmin*u.km/u.s,
                                              vmax*u.km/u.s).moment0(axis=0)
                    for color,(vmin,vmax) in colorslices[field].items()}

    rgb_image = np.array([moment_slabs['r'],
                          moment_slabs['g'],
                          moment_slabs['b'],
                         ]).T.swapaxes(0,1)

    norm = visualization.simple_norm(rgb_image, min_percent=0.1, max_percent=99.5)

    zrx = n2hc.shape[2] // 20
    zry = n2hc.shape[1] // 20

    pl.imshow(norm(rgb_image)[zry:-zry, zrx:-zrx], origin='lower')

    pl.xticks([])
    pl.yticks([])

    pl.savefig(filepath+".rgb.png", bbox_inches='tight', dpi=300)
