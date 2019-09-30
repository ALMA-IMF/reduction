import pylab as pl
import numpy as np
import glob
import os
from astropy.io import fits
from astropy.stats import mad_std
from astropy import visualization
from spectral_cube import SpectralCube


def make_comparison_image(bsens, cleaned):
    #fh_pre = fits.open(bsens)
    #fh_post = fits.open(cleaned)
    cube_pre = SpectralCube.read(bsens, format='casa_image')
    cube_post = SpectralCube.read(cleaned, format='casa_image')
    cube_pre = cube_pre.with_mask(cube_pre != 0*cube_pre.unit)
    cube_post = cube_post.with_mask(cube_post != 0*cube_post.unit)
    #cube_pre = cube_pre.minimal_subcube()
    #cube_post = cube_post.minimal_subcube()
    data_pre = cube_pre[0].value
    data_post = cube_post[0].value

    data_pre[np.abs(data_pre) < 1e-7] = np.nan
    data_post[np.abs(data_post) < 1e-7] = np.nan

    try:
        diff = (data_post - data_pre)
    except Exception as ex:
        print(bsens, cleaned, cube_pre.shape, cube_post.shape)
        raise ex

    fig = pl.figure(1, figsize=(14,6))
    fig.clf()


    norm = visualization.simple_norm(data=diff.squeeze(), stretch='asinh',
                                     min_cut=-0.001)
    if norm.vmax < 0.001:
        norm.vmax = 0.001

    cm = pl.matplotlib.cm.viridis
    cm.set_bad('white', 0)

    ax1 = pl.subplot(1,3,1)
    ax2 = pl.subplot(1,3,2)
    ax3 = pl.subplot(1,3,3)
    for ax in (ax1,ax2,ax3):
        ax.cla()
    ax1.imshow(data_pre, norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax1.set_title("bsens")
    ax2.imshow(data_post, norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax2.set_title("line-free")
    ax3.imshow(diff.squeeze(), norm=norm, origin='lower', interpolation='none', cmap=cm)
    ax3.set_title("bsens - line-free")

    for ax in (ax1,ax2,ax3):
        ax.set_xticks([])
        ax.set_yticks([])

    pl.subplots_adjust(wspace=0.0)

    return ax1,ax2,ax3,fig


print("{4:14s}{0:>15s} {1:>15s} {2:>15s} {3:>15s} {5:>15s} {6:>15s}".format("bsens_sum", "bsens_mad",  "clean_sum",  "clean_mad", "field & band", "diff_sum", "diff_mad"))

for fn in glob.glob("*bsens_12M_bsens_reclean_robust0.image.tt0.fits"):
    bsens = fn
    clean = fn.replace("_bsens","")
    #print(os.path.exists(bsens), os.path.exists(clean))
    field = fn.split("_uid")[0]

    bsens_fh = fits.open(bsens)
    try:
        clean_fh = fits.open(clean)
    except Exception as ex:
        print(ex)
        continue

    if (bsens_fh[0].data.shape == clean_fh[0].data.shape):
        bsd = bsens_fh[0].data
        cld = clean_fh[0].data
        diff = bsd-cld
        bsens_fh[0].data = diff
        try:
            bsens_fh.writeto(fn.replace("_bsens_reclean", "_bsens_minus_clean_reclean"), overwrite=False)
        except Exception as ex:
            print(ex)
        print(f"{field:14s}"
              f"{bsd[np.isfinite(bsd)].sum():15.3f} {mad_std(bsd, ignore_nan=True):15.5f} "
              f"{cld[np.isfinite(cld)].sum():15.3f} {mad_std(cld, ignore_nan=True):15.5f} "
              f"{diff[np.isfinite(diff)].sum():15.3f} {mad_std(diff, ignore_nan=True):15.5f} "
             )
        try:
            make_comparison_image(bsens, clean)
        except Exception as ex:
            if "operands could not be broadcast together with shapes" in str(ex):
                print("Shapes: ",bsens_fh[0].data.shape, clean_fh[0].data.shape)
            print(ex)
        pl.savefig(f"comparisons/{field}_12M_bsens_vs_cleanest_comparison.png", bbox_inches='tight')
    else:
        print(f"Skipping {bsens} because there was a shape mismatch.")
