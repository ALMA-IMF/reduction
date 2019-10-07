from spectral_cube import SpectralCube
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


    cube = SpectralCube.read(f'{imname}.image.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.00)
    im1 = ax1.imshow(cube[0].value, norm=norm)
    cube = SpectralCube.read(f'{imname}.residual.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.95)
    im2 = ax2.imshow(cube[0].value, norm=norm)
    cube = SpectralCube.read(f'{imname}.model.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch='asinh', min_percent=1, max_percent=99.00)
    im3 = ax3.imshow(cube[0].value, norm=norm)
    title = pl.suptitle("Before selfcal")

    def update(ii):

        if ii == 0:
            return im, (ax1,ax2,ax3)
        else:
            cube = SpectralCube.read(f'{imname}_selfcal{ii}.image.tt0', format='casa_image')
            im1.set_data(cube[0].value)
            cube = SpectralCube.read(f'{imname}_selfcal{ii}.residual.tt0', format='casa_image')
            im2.set_data(cube[0].value)
            cube = SpectralCube.read(f'{imname}_selfcal{ii}.model.tt0', format='casa_image')
            im3.set_data(cube[0].value)

            title.set_text(f"Selfcal iteration {ii}")

            return im, (ax1,ax2,ax3)

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

    cube = SpectralCube.read(f'{imname}.{suffix}.tt0', format='casa_image')
    norm = visualization.simple_norm(data=cube[0].value, stretch=stretch,
                                     min_percent=min_percent,
                                     max_percent=max_percent)
    im1 = ax.imshow(cube[0].value, norm=norm)
    title = pl.suptitle("Before selfcal")

    def update(ii):

        if ii == 0:
            return im, ax
        else:
            cube = SpectralCube.read(f'{imname}_selfcal{ii}.{suffix}.tt0', format='casa_image')
            im1.set_data(cube[0].value)

            title.set_text(f"Selfcal iteration {ii}")

            return im, ax

    anim = FuncAnimation(fig, update, frames=range(0,nselfcaliter), interval=400)
    anim.save(f'{imname}_{suffix}_selfcal_anim.gif', dpi=dpi, writer='imagemagick')

    return anim
