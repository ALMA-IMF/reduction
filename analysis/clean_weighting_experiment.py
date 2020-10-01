"""
Experiment to check how weighting affects the beam shape and noise level.

Goal: 
    (1) Determine whether the weights in the measurement set are responsible
        for the erratic beam sizes we're observing.  
    (2) Come up with an appropriate imaging recommendation to achieve
        the target (proposed) beam size and sensitivity.


Plan:
    (1) Create a copy of the self-calibrated data set for a field
    (2) Statweight that ms
    (3) Image both the original and statweighted versions of the MS
    using the same input model and no cleaning with each of 5 robust
    parameters (-2, -1, 0, 1, 2)
    (4) Measure the noise in the noise measurement regions
    (5) Plot noise level vs beam size
"""

def clean_weight_and_image(vis, baseimagename, robusts=[-2,-1,0,1,2],
                           swdatacolumns=('data', 'residual_data', 'orig'),
                           **kwargs):

    origvis = vis

    for swdatacolumn in swdatacolumns:
        if swdatacolumn == 'orig':
            vis = origvis
        else:
            swvis = origvis+".statwt."+swdatacolumn
            if not os.path.exists(swvis):
                shutil.copytree(origvis, swvis)
            vis = swvis

            tclean(vis=vis,
                   datacolumn='corrected', # assumes we're using the self-cal'd data
                   imagename='temp',
                   specmode="mfs",
                   gridder="mosaic",
                   deconvolver="mtmfs",
                   scales=[0, 3, 9, 27],
                   nterms=2,
                   weighting="briggs",
                   robust=0,
                   niter=0,
                   savemodel='modelcolumn',
                   **kwargs)
            os.system('rm -r temp.*')

            statwt(vis, datacolumn=swdatacolumn, slidetimebin=True,
                   timebin='20s')

        print(vis)
        ms.open(vis)
        ss = ms.getscansummary()
        spws = set([blah for entry in ss for key in ss[entry] for blah in ss[entry][key]['SpwIds']])
        ms.close()
        fig = pl.figure(4)
        fig.clf()

        for spw in spws:
            ms.open(vis)
            ms.selectinit(datadescid=spw)
            data = ms.getdata(['weight','uvdist'])
            try:
                pl.plot(data['uvdist'], data['weight'].T, ',', alpha=0.5)
            except Exception as ex:
                print("data weight min max: ",data['weight'].min(), data['weight'].max())
                print("uvdist min max: ",data['uvdist'].min(), data['uvdist'].max())
                print(ex)
            ms.close()

        pl.loglog()
        pl.xlabel("UV Distance")
        pl.ylabel("Weight")
        pl.savefig(baseimagename+"."+swdatacolumn+".weight_vs_uvdist.png", bbox_inches='tight')

        for robust in robusts:

            imagename = baseimagename+".{1}.robust{0}".format(robust, swdatacolumn)

            if not os.path.exists(imagename+".image.tt0"):
                tclean(vis=vis,
                       datacolumn='corrected', # assumes we're using the self-cal'd data
                       imagename=imagename,
                       specmode="mfs",
                       gridder="mosaic",
                       deconvolver="mtmfs",
                       scales=[0, 3, 9, 27],
                       nterms=2,
                       weighting="briggs",
                       robust=robust,
                       niter=0,
                       **kwargs)


if __name__ == "__main__":
    import os

    pwd = os.getcwd()

    if not os.path.exists('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/clean_weighting_experiment_Sep2020'):
        os.mkdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/clean_weighting_experiment_Sep2020')

    os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/clean_weighting_experiment_Sep2020')

    import shutil
    from astropy import units as u
    import numpy as np
    from radio_beam import Beam
    import regions
    import pylab as pl
    pl.ion()
    from spectral_cube import SpectralCube
    from astropy import units as u


    vis = 'G337.92_B3_uid___A001_X1296_X147_continuum_merged.cal.ms'
    if not os.path.exists(vis):
        shutil.copytree('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/scigoals/G337.92/group.uid___A001_X1296_X142/member.uid___A001_X1296_X147/calibrated/G337.92_B3_uid___A001_X1296_X147_continuum_merged.cal.ms',
                        vis)

    vis = 'G337.92_B3__continuum_merged_12M_selfcal.ms'
    if not os.path.exists(vis):
        shutil.copytree('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/timea_data/'+vis, vis)


    imresultspath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/'

    imaging_parameters = dict(
        field="G337.92",
        antenna="DA42,DA43,DA44,DA45,DA46,DA48,DA49,DA50,DA51,DA52,DA53,DA54,DA55,DA56,DA57,DA58,DA59,DA60,DA61,DA62,DA63,DA64,DA65,DV01,DV03,DV04,DV07,DV08,DV09,DV10,DV11,DV13,DV14,DV15,DV16,DV17,DV19,DV20,DV22,DV23,DV24,DV25,PM01,DA41,DA42,DA43,DA44,DA45,DA46,DA47,DA48,DA50,DA51,DA54,DA55,DA56,DA57,DA58,DA61,DA62,DA63,DV02,DV03,DV05,DV06,DV07,DV11,DV12,DV14,DV18,DV19,DV21,DV22",
        imsize=[3136, 2560],
        cell=['0.07arcsec', '0.07arcsec'],
        phasecenter="ICRS 250.29425deg -47.134138572deg",
        pblimit=0.1,
        usemask="user",
        mask="",
        startmodel=[imresultspath + 'G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter.model.tt0',
                    imresultspath + 'G337.92_B3_uid___A001_X1296_X147_continuum_merged_12M_robust0_selfcal4_finaliter.model.tt1'],
    )


    fig3 = pl.figure(3)
    fig3.clf()
    ax3 = pl.subplot(2,1,1)
    ax4 = pl.subplot(2,1,2)

    noisebeamdata = {}

    for vis, baseimagename, swdatacolumns in zip(('G337.92_B3_uid___A001_X1296_X147_continuum_merged.cal.ms',
                                                  'G337.92_B3__continuum_merged_12M_selfcal.ms'),
                                                 ('G337.92_B3_uid___A001_X1296_X147_continuum_merged.statwt',
                                                  'G337.92_B3_TimeaData_continuum_merged.statwt'),
                                                 (('data', 'residual_data', 'orig'),
                                                  ('corrected', 'residual', 'orig'))):

        vis_shortname = 'pipe' if 'uid' in vis else 'timea'

        robusts = [-1.5, -1, -0.5, -0.25, 0, 0.25, 0.5,]# 1, 1.5]
        try:
            clean_weight_and_image(vis=vis,
                                   baseimagename=baseimagename,
                                   robusts=robusts,
                                   swdatacolumns=swdatacolumns,
                                   **imaging_parameters)
        except Exception as ex:
            print(ex)

        noiseregfn = '/orange/adamginsburg/ALMA_IMF/reduction/reduction/noise_estimation_regions/G337.92_B3_noise_sampling.reg'
        noisereg = regions.read_ds9(noiseregfn)

        
        fig = pl.figure(1, figsize=(20,10))
        fig.clf()

        xl,xh = 1500,1650
        yl,yh = 1200,1350

        nrobusts = len(robusts)

        beams = {}
        rms = {}

        for ii,swdatacolumn in enumerate(swdatacolumns):
            for jj,robust in enumerate(robusts):
                imagename = baseimagename+".{1}.robust{0}".format(robust, swdatacolumn)
                ax = pl.subplot(3, nrobusts, ii*nrobusts + (jj % nrobusts) + 1)
                print(ii,jj,swdatacolumn,robust)

                if os.path.exists(imagename+".image.tt0"):
                    cube = SpectralCube.read(imagename+".image.tt0", format='casa_image')
                    beam = cube.beam

                    cutout = cube[0][yl:yh,xl:xh]
                    ax.imshow(cutout.value, origin='lower', vmin=-0.0002,
                              vmax=0.005, cmap='gray')
                    ax.set_xticks([])
                    ax.set_yticks([])

                    pixscale = cube.wcs.celestial.pixel_scale_matrix[1,1]
                    beampatch = beam.ellipse_to_plot(10, 10, pixscale*u.deg)
                    ax.add_patch(beampatch)
                    ax.set_title("{swdatacolumn} r={robust}".format(**locals()))
                    beams[(swdatacolumn, robust)] = beam
                    noise = cube.subcube_from_regions(noisereg).std()
                    rms[(swdatacolumn, robust)] = noise
                else:
                    rms[(swdatacolumn, robust)] = np.nan*u.Jy
                    beams[(swdatacolumn, robust)] = Beam(np.nan)
                    print("MISSING {0}".format(imagename))
        pl.savefig("{baseimagename}_robust_comparison.png".format(**locals()), bbox_inches='tight')
        print(noise)
        print(beams)

        pl.figure(2).clf()
        ax1 = pl.subplot(2,1,1)
        ax2 = pl.subplot(2,1,2)
        for swdatacolumn, marker in zip(swdatacolumns, 'sox'):
            ax1.plot(robusts, [rms[(swdatacolumn, robust)].value for robust in robusts], label=swdatacolumn, marker=marker)
            ax2.plot(robusts, [beams[(swdatacolumn, robust)].major.to(u.arcsec).value for robust in robusts], label=swdatacolumn, marker=marker)

            ax3.plot(robusts, [rms[(swdatacolumn, robust)].value for robust in robusts], label=vis_shortname+"_"+swdatacolumn, marker=marker)
            ax4.plot(robusts, [beams[(swdatacolumn, robust)].major.to(u.arcsec).value for robust in robusts], label=vis_shortname+"_"+swdatacolumn, marker=marker)

        ax2.set_xlabel("Robust Value")
        ax1.set_ylabel("Noise Estimate (Jy)")
        ax2.set_ylabel("Beam Major")

        pl.figure(2)
        pl.legend(loc='best')
        pl.savefig(baseimagename+'_noise_and_beams_vs_robust.png', bbox_inches='tight')

        noisebeamdata[vis] = {'noise': noise, 'beams': beams}


    pl.figure(3)
    ax3.set_ylabel("Noise Estimate (Jy)")
    ax4.set_ylabel("Beam Major")
    ax4.set_xlabel("Robust Value")
    pl.legend(loc='best')
    fig3.savefig('compare_timea_vs_pipeline_noise_and_beams_vs_robust.png', bbox_inches='tight')
