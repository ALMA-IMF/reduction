import numpy as np
from astropy import units as u
from spectral_cube import SpectralCube
from astropy import visualization
import pylab as pl

basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults'

colorslices = {'W51-IRS2': {'b': (46, 52), 'g': (52, 58), 'r': (59, 65)},
               'W51-E': {'b': (46, 52), 'g': (52, 58), 'r': (59, 65)},
               'G010.62': {'b': (-10, -5), 'g': (-5, 0), 'r': (0, 5)},
               'G012.80': {'b': (32,36), 'g': (36,40), 'r': (40,44)},
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

    pl.imshow(norm(rgb_image)[250:-250,250:-250], origin='lower')

    pl.xticks([])
    pl.yticks([])

    pl.savefig(filepath+".rgb.png", bbox_inches='tight', dpi=300)
