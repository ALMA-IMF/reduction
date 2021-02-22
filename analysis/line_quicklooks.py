
import glob
from astropy.io import fits
from astropy import visualization
import pylab as pl


import os
import time
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.stats import mad_std
import pylab as pl
import radio_beam
import glob
from spectral_cube import SpectralCube,DaskSpectralCube
from spectral_cube.lower_dimensional_structures import Projection

if os.getenv('NO_PROGRESSBAR') is None:
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

nthreads = 1
scheduler = 'synchronous'

if os.getenv('DASK_THREADS') is not None:
    try:
        nthreads = int(os.getenv('DASK_THREADS'))
        if nthreads > 1:
            scheduler = 'threads'
        else:
            scheduler = 'synchronous'
    except (TypeError,ValueError):
        nthreads = 1
        scheduler = 'synchronous'

default_lines = {'n2hp': '93.173700GHz',
                 'sio': '217.104984GHz',
                 'h2co303': '218.222195GHz',
                 '12co': '230.538GHz',
                 'h30a': '231.900928GHz',
                 'h41a': '92.034434GHz',
                 "c18o": "219.560358GHz",
                 "ch3cn": "92.26144GHz",
                 "ch3cch": "102.547983GHz",
                }

suffix = '.image'

os.environ['TEMPDIR'] = '/blue/adamginsburg/adamginsburg/tmp/'

cwd = os.getcwd()
basepath = '/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'
os.chdir(basepath)
print(f"Changed from {cwd} to {basepath}, now running line_quicklooks")

# allow %run -i w/overwrite=True to force overwriting
if 'overwrite' not in locals():
    overwrite = bool(os.getenv('OVERWRITE'))

global then
then = time.time()
def dt():
    global then
    now = time.time()
    print(f"Elapsed: {now-then}")
    then = now

for field in "G328.25 G351.77 W51-IRS2 W43-MM2 G327.29 G338.93 W51-E G353.41 G008.67 G337.92 W43-MM3 W43-MM1 G010.62 G012.80 G333.60".split():
    for band in (3,6):
        for config in ('12M',): #'7M12M',
            for line in default_lines:
                for suffix in (".image", ".contsub.image"):
                    globblob = f"{field}_B{band}*_{config}_*{line}{suffix}"
                    fn = glob.glob(globblob)
                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    if os.path.exists('collapse/min/{0}'.format(fn.replace(suffix,"_min_K.fits"))) and not overwrite:
                        print(f"Found completed quicklooks for {fn}, skipping.")
                        continue

                    modfile = fn.replace(suffix, ".model")
                    if os.path.exists(modfile+".fits"):
                        modcube = SpectralCube.read(modfile+".fits", use_dask=True)
                        modcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        modcube.beam_threshold=100000
                    elif os.path.exists(modfile):
                        modcube = SpectralCube.read(modfile, format='casa_image', use_dask=True)
                        modcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                        modcube.beam_threshold=100000

                    rest_value = u.Quantity(default_lines[line])

                    if os.path.exists(fn+".fits"):
                        cube = SpectralCube.read(fn+".fits", format='fits', use_dask=True)
                    else:
                        cube = SpectralCube.read(fn, format='casa_image', use_dask=True)
                    cube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    cube.beam_threshold = 1
                    #cube.allow_huge_operations = True
                    mcube = cube.mask_out_bad_beams(0.1)
                    mcube.use_dask_scheduler(scheduler, num_workers=nthreads)
                    mcube.beam_threshold = 1

                    print(mcube)

                    dt(); print("Spatial mad_std")
                    pl.close('all')
                    pl.clf()
                    stdspec = mcube.mad_std(axis=(1,2))#, how='slice')
                    stdspec.write("collapse/stdspec/{0}".format(fn.replace(suffix, "_std_spec.fits")), overwrite=True)
                    stdspec.quicklook("collapse/stdspec/pngs/{0}".format(fn.replace(suffix, "_std_spec.png")))

                    if np.nanmin(stdspec) > 0.1*cube.unit:
                        threshold = np.nanpercentile(stdspec, 90).value
                    else:
                        threshold = 0.1

                    dt(); print("Thresholding")
                    mcube = mcube.with_mask((stdspec < threshold*cube.unit)[:,None,None])

                    beam = mcube.beam if hasattr(mcube, 'beam') else mcube.average_beams(1)
                    cfrq = mcube.with_spectral_unit(u.GHz).spectral_axis.mean()

                    pl.clf()
                    dt(); print("Moment 0")
                    mvcube = mcube.with_spectral_unit(u.km/u.s, velocity_convention='radio')
                    mom0 = mvcube.moment0(axis=0)
                    mom0_Kkms = (mom0*u.beam*u.s/u.km).to(u.K,
                                                          u.brightness_temperature(beam_area=beam,
                                                                                   frequency=cfrq))*u.km/u.s
                    mom0_Kkms.write('collapse/moment0/{0}'.format(fn.replace(suffix,"_mom0_Kkms.fits")),
                                    overwrite=True)
                    mom0_Kkms.quicklook('collapse/moment0/pngs/{0}'.format(fn.replace(suffix,"_mom0_Kkms.png")))

                    pl.clf()
                    dt(); print("Moment 1")
                    mom1 = mvcube.moment1(axis=0)
                    mom1.write('collapse/moment1/{0}'.format(fn.replace(suffix,"_mom1_kms.fits")),
                               overwrite=True)
                    mom1.quicklook('collapse/moment1/pngs/{0}'.format(fn.replace(suffix,"_mom1_kms.png")))

                    pl.clf()
                    dt(); print("Moment 2")
                    mom2 = mvcube.linewidth_fwhm()
                    mom2.write('collapse/moment2/{0}'.format(fn.replace(suffix,"_mom2fwhm_kms.fits")),
                               overwrite=True)
                    mom2.quicklook('collapse/moment2/pngs/{0}'.format(fn.replace(suffix,"_mom2fwhm_kms.png")))

                    pl.clf()
                    dt(); print("Spatial max (peak spectrum)")
                    mxspec = mcube.max(axis=(1,2))#, how='slice')
                    mxspec.write("collapse/maxspec/{0}".format(fn.replace(suffix, "_max_spec.fits")), overwrite=True)
                    mxspec.quicklook("collapse/maxspec/pngs/{0}".format(fn.replace(suffix, "_max_spec.png")))
                    if os.path.exists(modfile):
                        mxmodspec = modcube.max(axis=(1,2))#, how='slice')
                        mxmodspec.write("collapse/maxspec/{0}".format(fn.replace(suffix, "_max_model_spec.fits")), overwrite=True)
                        mxmodspec.quicklook("collapse/maxspec/pngs/{0}".format(fn.replace(suffix, "_max_model_spec.png")))

                    dt(); print("Peak intensity")
                    mx = mcube.max(axis=0)#, how='slice')
                    mx_K = (mx*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mx_K.write('collapse/max/{0}'.format(fn.replace(suffix,"_max_K.fits")),
                               overwrite=True)
                    mx_K.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max_K.png")))
                    mx.write('collapse/max/{0}'.format(fn.replace(suffix,"_max.fits")),
                             overwrite=True)
                    mx.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max.png")))

                    sn_mask = mxspec / stdspec > 5
                    if any(sn_mask):
                        dt(); print("Masked peak intensity")
                        mcube_sn = mcube.with_mask(sn_mask[:,None,None])
                        mx_masked = mcube_sn.max(axis=0)#, how='slice')
                        mx_masked_K = (mx_masked*u.beam).to(u.K,
                                                            u.brightness_temperature(beam_area=beam,
                                                                                     frequency=cfrq))
                        mx_masked_K.write('collapse/max/{0}'.format(fn.replace(suffix,"_max_masked_K.fits")),
                                          overwrite=True)
                        mx_masked_K.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max_masked_K.png")))
                        mx_masked.write('collapse/max/{0}'.format(fn.replace(suffix,"_max_masked.fits")),
                                        overwrite=True)
                        mx_masked.quicklook('collapse/max/pngs/{0}'.format(fn.replace(suffix,"_max_masked.png")))

                        pl.clf()
                        dt(); print("Masked moment 0")
                        mom0 = mcube_sn.with_spectral_unit(u.km/u.s, velocity_convention='radio').moment0(axis=0)
                        mom0_Kkms = (mom0*u.beam*u.s/u.km).to(u.K,
                                                              u.brightness_temperature(beam_area=beam,
                                                                                       frequency=cfrq))*u.km/u.s
                        mom0_Kkms.write('collapse/moment0/{0}'.format(fn.replace(suffix,"_mom0_Kkms_masked.fits")),
                                        overwrite=True)
                        mom0_Kkms.quicklook('collapse/moment0/pngs/{0}'.format(fn.replace(suffix,"_mom0_Kkms_masked.png")))

                        pl.clf()
                        dt(); print("Masked moment 1")
                        mom1 = mcube_sn.with_spectral_unit(u.km/u.s, velocity_convention='radio').moment1(axis=0)
                        mom1.write('collapse/moment1/{0}'.format(fn.replace(suffix,"_mom1_kms_masked.fits")),
                                   overwrite=True)
                        mom1.quicklook('collapse/moment1/pngs/{0}'.format(fn.replace(suffix,"_mom1_kms_masked.png")))

                        pl.clf()
                        dt(); print("Masked moment 2")
                        mom2 = mcube_sn.with_spectral_unit(u.km/u.s, velocity_convention='radio').linewidth_fwhm()
                        mom2.write('collapse/moment2/{0}'.format(fn.replace(suffix,"_mom2fwhm_kms_masked.fits")),
                                   overwrite=True)
                        mom2.quicklook('collapse/moment2/pngs/{0}'.format(fn.replace(suffix,"_mom2fwhm_kms_masked.png")))

                    mcube = mcube.with_mask(np.isfinite(mx))
                    argmax = mcube.argmax(axis=0)#, how='ray')
                    hdu = mx.hdu
                    hdu.data = argmax
                    hdu.writeto('collapse/argmax/{0}'.format(fn.replace(suffix,"_argmax.fits")),
                                overwrite=True)
                    bad = np.isnan(argmax)
                    argmax = np.nan_to_num(argmax).astype('int')
                    assert 'int' in argmax.dtype.name
                    vmax = mcube.with_spectral_unit(u.km/u.s, rest_value=rest_value, velocity_convention='radio').spectral_axis[argmax]
                    vmax[bad] = np.nan
                    hdu.data = vmax.to(u.km/u.s).value
                    hdu.writeto('collapse/argmax/{0}'.format(fn.replace(suffix,"_vmax.fits")),
                                overwrite=True)


                    mn = mcube.min(axis=0)#, how='slice')
                    mn_K = (mn*u.beam).to(u.K, u.brightness_temperature(beam_area=beam,
                                                                        frequency=cfrq))
                    mn_K.write('collapse/min/{0}'.format(fn.replace(suffix,"_min_K.fits")),
                               overwrite=True)
                    mn_K.quicklook('collapse/min/pngs/{0}'.format(fn.replace(suffix,"_min_K.png")))



                    for pct in (25,50,75):
                        dt(); print(f"{pct}th Percentile")
                        #pctmap = mcube.percentile(pct, axis=0, iterate_rays=True)
                        pctmap = mcube.percentile(pct, axis=0)
                        pctmap_K = (pctmap*u.beam).to(u.K,
                                                      u.brightness_temperature(beam_area=beam,
                                                                               frequency=cfrq))
                        pctmap_K.write('collapse/percentile/{0}'.format(fn.replace(suffix,"_{0}pct_K.fits".format(pct))),
                                       overwrite=True)
                        pctmap_K.quicklook('collapse/percentile/pngs/{0}'.format(fn.replace(suffix,"_{0}pct_K.png".format(pct))))

                    pl.close('all')


"""
Files that have resulted in m/s parsing failures:
    ['G012.80_B3_spw0_7M12M_n2hp.contsub.image']
"""

# for fn in /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/collapse/*/pngs; do out=${fn//*collapse\// }; out=${out/\//_}; outdir="/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/cube_quicklooks/${out/ /}"; cp -v ${fn}/* ${outdir}; done
# for fn in /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/collapse/*/pngs; do out=${fn//*collapse\// }; out=${out/\//_}; echo $out; mkdir /orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/cube_quicklooks/${out}; cp -v ${fn}/* /orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/cube_quicklooks/${out}/; done
