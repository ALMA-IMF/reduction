from spectral_cube import SpectralCube
import os
import pylab as pl
from astropy import visualization
from matplotlib.animation import FuncAnimation
import warnings
warnings.filterwarnings('ignore')

pl.rcParams['image.origin'] = 'lower'
pl.rcParams['image.interpolation'] = 'none'
pl.rcParams['ytick.direction'] = 'in'
pl.rcParams['xtick.direction'] = 'in'
pl.rcParams['ytick.color'] = 'w'
pl.rcParams['xtick.color'] = 'w'


def make_anim(imname, nselfcaliter=7):
    # base imname: W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0

    fig, (ax1, ax2, ax3) = pl.subplots(ncols=3, figsize=(18,6))
    fig.set_tight_layout(True)

    dpi = fig.get_dpi()
    size_inches = fig.get_size_inches()

    print(f"Figure size={size_inches} dpi={dpi}")


    for ax in (ax1,ax2,ax3):
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    fig.subplots_adjust(hspace=0)


    cube = SpectralCube.read(f'{imname}_preselfcal.image.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.00)
    im1 = ax1.imshow(cube[0].value, norm=norm)
    cube = SpectralCube.read(f'{imname}_preselfcal.residual.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.95)
    im2 = ax2.imshow(cube[0].value, norm=norm)
    cube = SpectralCube.read(f'{imname}_preselfcal.model.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.00)
    if cube.max() > cube.min():
        # ensure that vmax > vmin
        mpct = 99
        while norm.vmax > norm.vmin:
            mpct += (100-mpct)*0.05
            norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=mpct)
        im3 = ax3.imshow(cube[0].value, norm=norm)
    else:
        im3 = ax3.imshow(cube[0].value)
    title = pl.suptitle("Before selfcal")

    def update(ii):

        try:
            if ii == 0:
                return (im1,im2,im3), (ax1,ax2,ax3)
            else:
                cube = SpectralCube.read(f'{imname}_selfcal{ii}.image.tt0', format='casa_image')
                im1.set_data(cube[0].value)
                cube = SpectralCube.read(f'{imname}_selfcal{ii}.residual.tt0', format='casa_image')
                im2.set_data(cube[0].value)
                cube = SpectralCube.read(f'{imname}_selfcal{ii}.model.tt0', format='casa_image')
                im3.set_data(cube[0].value)

                title.set_text(f"Selfcal iteration {ii}")

                return (im1,im2,im3), (ax1,ax2,ax3)
        except Exception as ex:
            print(ex)

    anim = FuncAnimation(fig, update, frames=range(0,nselfcaliter), interval=400)
    anim.save(f'{imname}_selfcal_anim.gif', dpi=dpi, writer='imagemagick')

    return anim


def make_anim_single(imname, suffix, nselfcaliter=7, stretch='asinh', min_percent=1, max_percent=99.00):
    # base imname: W51-E_B6_uid___A001_X1296_X213_continuum_merged_12M_robust0

    fig, ax = pl.subplots(ncols=1, figsize=(8,8))
    fig.set_tight_layout(True)

    dpi = fig.get_dpi()
    size_inches = fig.get_size_inches()

    print(f"Figure size={size_inches} dpi={dpi}")

    ax.set_xticklabels([])
    ax.set_yticklabels([])

    cube_before = SpectralCube.read(f'{imname}_preselfcal.{suffix}.tt0', format='casa_image')
    data = cube_before[0].value
    norm = visualization.simple_norm(data=data, stretch=stretch,
                                     min_percent=min_percent,
                                     max_percent=max_percent)
    im1 = ax.imshow(data, norm=norm)
    title = pl.title("Before selfcal")

    def update(ii):

        try:
            if os.path.exists(f'{imname}_selfcal{ii}_finaliter.{suffix}.tt0'):
                cube = SpectralCube.read(f'{imname}_selfcal{ii}_finaliter.{suffix}.tt0', format='casa_image')
                im1.set_data(cube[0].value)

                title.set_text(f"Selfcal iteration {ii} (final clean)")

                return im1, ax
            if ii == 0:
                im1.set_data(data)
                title.set_text(f"Before selfcal")
                return im1, ax
            else:
                cube = SpectralCube.read(f'{imname}_selfcal{ii}.{suffix}.tt0', format='casa_image')
                im1.set_data(cube[0].value)

                title.set_text(f"Selfcal iteration {ii}")

                return im1, ax
        except Exception as ex:
            print(ex)

    anim = FuncAnimation(fig, update, frames=range(0, nselfcaliter), interval=400)
    anim.save(f'{imname}_{suffix}_selfcal_anim.gif', dpi=dpi, writer='imagemagick')

    return anim
