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
                                   arrays=['12M', 'bsens_12M',],# '7M12M'],
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
    dynamicrange = {}


    for ii,array in enumerate(arrays):
        for jj,robust in enumerate(robusts):
            imagename = "{baseimagename}_{array}_robust{robust}_selfcal{selfcalnumber}{suffix}".format(**locals())
            ax = pl.subplot(len(arrays), nrobusts, ii*nrobusts + (jj % nrobusts) + 1)

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
                peak = cube.max()
                rms[(array, robust)] = noise
                dynamicrange[(array, robust)] = (peak / noise).decompose().value
                print("found {0}".format(imagename),ii,jj,array,robust)
            else:
                rms[(array, robust)] = np.nan*u.Jy/u.beam
                dynamicrange[(array, robust)] = np.nan
                beams[(array, robust)] = Beam(np.nan)
                print("MISSING {0}".format(imagename),ii,jj,array,robust)
    pl.savefig("{baseimagename}_robust_comparison.png".format(**locals()), bbox_inches='tight')

    pl.figure(2).clf()
    ax3 = pl.subplot(3,1,1)
    ax1 = pl.subplot(3,1,2)
    ax2 = pl.subplot(3,1,3)

    array_label_map = {'12M': 'cleanest',
                       'bsens_12M': 'bsens'}

    for array, marker in zip(arrays, 'sox'):
        try:
            rmses = [rms[(array, robust)].to(u.mJy/u.beam).value for robust in
                     robusts]
        except u.UnitConversionError:
            rmses = [rms[(array, robust)].to(u.mJy).value for robust in
                     robusts]
        ax1.plot(robusts, rmses, label=array_label_map[array],
                 marker=marker)
        ax2.plot(robusts, [beams[(array, robust)].major.to(u.arcsec).value for
                           robust in robusts], label=array_label_map[array],
                 marker=marker)
        ax3.plot(robusts, [dynamicrange[(array, robust)] for robust in
                           robusts], label=array_label_map[array],
                 marker=marker)


    ax3.set_xticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xlabel("Robust Value")
    ax1.set_ylabel("Noise Estimate (mJy)")
    ax2.set_ylabel("Beam Major")
    ax3.set_ylabel("Dynamic Range")

    pl.figure(2)
    leg = pl.legend(loc='best')
    pl.setp(leg.texts, family='courier')
    pl.suptitle(f"{fieldname} {bandname}")
    pl.tight_layout()
    pl.savefig(baseimagename+'_noise_and_beams_vs_robust.png', bbox_inches='tight')
    pl.savefig(baseimagename+'_noise_and_beams_vs_robust.pdf', bbox_inches='tight')

if __name__ == "__main__":
    from pathlib import Path
    from os import symlink, chdir, mkdir
    import glob
    releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults/')
    releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/June2021Release/')
    basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')

    dirnames = {#'fullcubes_12m': 'spw[0-9]_12M_spw[0-9]',
                #'linecubes_12m': 'spw[0-9]_12M_[a-z][!p]',
                #'fullcubes_7m12m': 'spw[0-9]_7M12M_spw[0-9]',
                #'linecubes_7m12m': 'spw[0-9]_7M12M_[a-z][!p]',
                'bsens': 'bsens_12M',
                'cleanest': 'merged_12M',
                #'7m12m': 'merged_7M12M',
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
                globbo = str(basepath / f"{field}_B{band}*{globstr}*finaliter.image.tt0")
                filelist = glob.glob(globbo)

                if len(filelist) >= 1:
                    filename = filelist[0]

                    selfcalnumber = int(filename.split("selfcal")[1][0])

                    uid = filename.split(f"B{band}_")[1].split("_continuum_merged")[0]

                    make_robust_comparison_figures(fieldname=field,
                                                   bandname=f'B{band}',
                                                   selfcalnumber=selfcalnumber,
                                                   uidname=uid,)

                chdir(cwd)

    from zoom_figures import make_zoom, make_multifig, make_robust_comparison

    for band in ('B3','B6'):
        for fieldid in prefixes:
            for robust0fn in glob.glob(f'/orange/adamginsburg/ALMA_IMF/RestructuredImagingResults/{fieldid}*/{band}/cleanest/{fieldid}*_{band}_uid___A001_X1296_*_continuum_merged_12M_robust0_selfcal*_finaliter.image.tt0'):
                pfx = robust0fn.replace(".image.tt0","")
                print(fieldid, band, pfx)
                try:
                    make_robust_comparison(fieldid, band=band, nsigma_linear_max=15, inner_stretch='asinh',
                                           finaliter_prefix=pfx, suffix='model.tt0', fileformat='casa_image')
                except FileNotFoundError:
                    print(f"File not found: {fieldid} {band} {pfx} model.tt0")

                try:
                    make_robust_comparison(fieldid, band=band, nsigma_linear_max=15, inner_stretch='asinh',
                                           finaliter_prefix=pfx, suffix='residual.tt0', fileformat='casa_image')
                except FileNotFoundError:
                    print(f"File not found: {fieldid} {band} {pfx} residual.tt0")

                try:
                    make_robust_comparison(fieldid, band=band, nsigma_linear_max=15, inner_stretch='asinh',
                                           suffix='image.tt0', fileformat='casa_image',
                                           finaliter_prefix=pfx)
                except FileNotFoundError:
                    print(f"File not found: {fieldid} {band} {pfx} image.tt0")
