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

if __name__ == "__main__":
    from pathlib import Path
    from os import symlink, chdir, mkdir
    import glob
    releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults/')
    basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')

    dirnames = {#'fullcubes_12m': 'spw[0-9]_12M_spw[0-9]',
                #'linecubes_12m': 'spw[0-9]_12M_[a-z][!p]',
                #'fullcubes_7m12m': 'spw[0-9]_7M12M_spw[0-9]',
                #'linecubes_7m12m': 'spw[0-9]_7M12M_[a-z][!p]',
                'bsens': 'bsens_12M',
                'cleanest': 'merged_12M',
                '7m12m': 'merged_7M12M',
                #'7m12m_bsens': 'bsens_7M12M*.tt0',
                #'7m': 'merged_7M_*.tt0',
                #'7m_bsens': 'bsens_7M_*.tt0',
               }

    for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
        for band in (3,6):
            bandpath = Path(f"B{band}")
            for dirname, globstr in dirnames.items():
                cwd = os.getcwd()
                chdir(releasepath / field / bandpath / dirname)
                globbo = str(basepath / f"{field}_B{band}*{globstr}*image.tt0")
                filelist = glob.glob(globbo)

                filename = filelist[0]

                uid = filename.split(f"B{band}_")[1].split("_continuum_merged")[0]

                make_robust_comparison_figures(fieldname=field,
                                               band=f'B{band}',
                                               uidname=uid,)

                chdir(cwd)
