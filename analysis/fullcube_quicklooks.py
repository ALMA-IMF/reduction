
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

spws = {3: range(4),
        6: range(7),}

suffix = '.image'

global then
then = time.time()
def dt():
    global then
    now = time.time()
    print(f"Elapsed: {now-then}")
    then = now

for field in "W43-MM2 G333.60 G327.29 G338.93 W51-E G353.41 G008.67 G337.92 W43-MM3 G328.25 G351.77 W43-MM1 G010.62 W51-IRS2 G012.80".split():
    for band in (3,6):
        for config in ('7M12M', '12M'):
            for spw in spws[band]:
                for suffix in (".image", ".contsub.image"):
                    globblob = f"{field}_B{band}_spw{spw}_{config}_spw{spw}{suffix}"
                    fn = glob.glob(globblob)
                    if any(fn):
                        print(f"Found some matches for fn {fn}, using {fn[0]}.")
                        fn = fn[0]
                    else:
                        print(f"Found no matches for glob {globblob}")
                        continue

                    if os.path.exists('collapse/min/{0}'.format(fn.replace(suffix,"_min_K.fits"))):
                        print(f"Found completed quicklooks for {fn}, skipping.")
                        continue

                    modfile = fn.replace(suffix, ".model")
                    if os.path.exists(modfile):
                        modcube = SpectralCube.read(modfile, format='casa_image', use_dask=True)
                        modcube.beam_threshold=100000

                    cube = SpectralCube.read(fn, format='casa_image', use_dask=True)
                    cube.use_dask_scheduler('threads', num_workers=8)
                    cube.beam_threshold = 1
                    #cube.allow_huge_operations = True
                    mcube = cube.mask_out_bad_beams(0.1)
                    mcube.use_dask_scheduler('threads', num_workers=8)
                    mcube.beam_threshold = 1

                    print(mcube)

                    dt(); print("Spatial mad_std")
                    pl.close('all')
                    pl.clf()
                    stdspec = mcube.mad_std(axis=(1,2))#, how='slice')
                    stdspec.write("collapse/stdspec/{0}".format(fn.replace(suffix, "_std_spec.fits")), overwrite=True)
                    stdspec.quicklook("collapse/stdspec/pngs/{0}".format(fn.replace(suffix, "_std_spec.png")))

                    if np.nanmin(stdspec) > 0.1*cube.unit:
                        threshold = np.nanpercentile(stdspec, 90)
                    else:
                        threshold = 0.1

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
