import os
import numpy as np
from radio_beam import Beam
import regions
import pylab as pl
pl.ion()
from spectral_cube import SpectralCube
from astropy import units as u


def make_robust_comparison_figures(fieldname, bandname,
                                   uidname,
                                   arrays=['12M', 'bsens_12M', '7M12M'],
                                   selfcalnumber=4,
                                   suffix='_finaliter',
                                   robusts=[-2,-1,-0.5,0,0.5,1,2],
                                   imageresultspath='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/',
                                   noiseregionpath='/orange/adamginsburg/ALMA_IMF/reduction/reduction/noise_estimation_regions/',
                                  ):

    noisebeamdata = {}


    noiseregfn = '{noiseregionpath}/{fieldname}_{bandname}_noise_sampling.reg'.format(**locals())
    noisereg = regions.read_ds9(noiseregfn)

    baseimagename = '{imageresultspath}/{fieldname}_{bandname}_{uidname}_continuum_merged'.format(**locals())
    
    fig = pl.figure(1, figsize=(20,10))
    fig.clf()

    nrobusts = len(robusts)

    beams = {}
    rms = {}


    for ii,array in enumerate(arrays):
        for jj,robust in enumerate(robusts):
            imagename = "{baseimagename}_{array}_robust{robust}_selfcal{selfcalnumber}{suffix}".format(**locals())
            ax = pl.subplot(3, nrobusts, ii*nrobusts + (jj % nrobusts) + 1)
            print(ii,jj,array,robust)

            if os.path.exists(imagename+".image.tt0"):
                cube = SpectralCube.read(imagename+".image.tt0", format='casa_image')
                beam = cube.beam


                xl,xh = cube.shape[1]//2-50, cube.shape[1]//2+50
                yl,yh = cube.shape[0]//2-50, cube.shape[0]//2+50

                cutout = cube[0][yl:yh,xl:xh]
                ax.imshow(cutout.value, origin='lower', vmin=-0.0002,
                          vmax=0.005, cmap='gray')
                ax.set_xticks([])
                ax.set_yticks([])

                pixscale = cube.wcs.celestial.pixel_scale_matrix[1,1]
                beampatch = beam.ellipse_to_plot(10, 10, pixscale*u.deg)
                ax.add_patch(beampatch)
                ax.set_title("{array} r={robust}".format(**locals()))
                beams[(array, robust)] = beam
                noise = cube.subcube_from_regions(noisereg).std()
                rms[(array, robust)] = noise
            else:
                rms[(array, robust)] = np.nan*u.Jy
                beams[(array, robust)] = Beam(np.nan)
                print("MISSING {0}".format(imagename))
    pl.savefig("{baseimagename}_robust_comparison.png".format(**locals()), bbox_inches='tight')
    print(noise)
    print(beams)

    pl.figure(2).clf()
    ax1 = pl.subplot(2,1,1)
    ax2 = pl.subplot(2,1,2)
    for array, marker in zip(arrays, 'sox'):
        ax1.plot(robusts, [rms[(array, robust)].value for robust in robusts], label=array, marker=marker)
        ax2.plot(robusts, [beams[(array, robust)].major.to(u.arcsec).value for robust in robusts], label=array, marker=marker)

    ax2.set_xlabel("Robust Value")
    ax1.set_ylabel("Noise Estimate (Jy)")
    ax2.set_ylabel("Beam Major")

    pl.figure(2)
    pl.legend(loc='best')
    pl.savefig(baseimagename+'_noise_and_beams_vs_robust.png', bbox_inches='tight')
