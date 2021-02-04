
vis = '../W51-E_B3_uid___A001_X1296_X10b_continuum_merged_bsens_12M_selfcal_bsens.ms/'
startmodel = ['../imaging_results/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_bsens_12M_robust0_selfcal6_finaliter.model.tt0',
              '../imaging_results/W51-E_B3_uid___A001_X1296_X10b_continuum_merged_bsens_12M_robust0_selfcal6_finaliter.model.tt1']
msmd.open(vis)
for obsid in range(msmd.nobservations()):
    scanset = msmd.scannumbers(obsid=obsid)
    if len(scanset) > 0:

        tclean(vis=vis,
               cell='0.05arcsec',
               imsize=512,
               startmodel=startmodel,
               #field="0",
               scan=",".join(map(str, scanset.tolist())),
               nterms=2,
               specmode='mfs',
               deconvolver='mtmfs',
               uvrange='100~2000m',
               weighting='briggs',
               robust=0,
               imagename='W51-E_ObsID_startmod_bsens_uvcut_robust0_{0:02d}'.format(obsid),
               phasecenter='ICRS 19:23:43.9 +14.30.34.8')
msmd.close()


obs7 = SpectralCube.read('W51-E_ObsID_07.image')
bm7 = SpectralCube.read('W51-E_ObsID_07.psf', format='casa_image')
obs3_conv7 = convolution.convolve_fft(obs3[0], bm7[0], normalize_kernel=False)
obs7_conv3 = convolution.convolve_fft(obs7[0], bm3[0], normalize_kernel=False)
obs3minusobs7 = obs3_conv7 - obs7_conv3
fits.PrimaryHDU(data=obs3minusobs7, header=cube.wcs.celestial.to_header()).writeto('obs3_minus_obs7.fits')
obs9 = SpectralCube.read('W51-E_ObsID_09.image')
obs11 = SpectralCube.read('W51-E_ObsID_11.image')
bm9 = SpectralCube.read('W51-E_ObsID_09.psf', format='casa_image')
bm11 = SpectralCube.read('W51-E_ObsID_11.psf', format='casa_image')
obs9_conv11 = convolution.convolve_fft(obs9[0], bm11[0], normalize_kernel=False)
obs11_conv9 = convolution.convolve_fft(obs11[0], bm9[0], normalize_kernel=False)
obs9minusobs11 = obs9_conv11 - obs11_conv9
fits.PrimaryHDU(data=obs9minusobs11, header=cube.wcs.celestial.to_header()).writeto('obs9_minus_obs11.fits')

for spw in msmd.spwsforfield('W51-E'):
    tclean(vis=vis,
           cell='0.05arcsec',
           imsize=512,
           startmodel=startmodel,
           spw=spw,
           specmode='mfs',
           deconvolver='mtmfs',
           nterms=2,
           weighting='briggs',
           robust=0,
           imagename='W51-E_ObsID_startmod_bsens_robust0_continuum_spw{0}'.format(spw),
           phasecenter='ICRS 19:23:43.9 +14.30.34.8')
