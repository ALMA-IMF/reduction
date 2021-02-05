import glob
import os
import shutil

from pathlib import Path

cwd = os.getcwd()
basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')
releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/February2021Release/')
os.chdir(basepath)

# configurable, kinda
overwrite = True

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in ('B3','B6'):
        for imtype,itgl in zip(('cleanest', 'bsens', ), ('continuum_merged_12M', 'bsens_12M', )):
            itpath = releasepath / field / band / imtype
            itpath.mkdir(parents=True, exist_ok=True)

            for suffix in ('image.tt0.fits', 'image.tt0.pbcor.fits', "image.tt0", "model.tt0", "image.tt1", "model.tt1", "psf.tt0", "psf.tt1", "residual.tt0", "residual.tt1", "mask"):

                for globstr in (f"{field}*_{band}_*{itgl}*robust0_*selfcal[0-9]*finaliter.{suffix}",
                                f"{field}*_{band}_*{itgl}*robust0_*preselfcal.{suffix}",
                                f"{field}*_{band}_*{itgl}*robust0_*preselfcal_finalmodel.{suffix}",
                                f"{field}_{band}_*_robust0_12M_mask.{suffix}", # use suffix here to avoid re-copying
                               ):

                    files = glob.glob(str(basepath / globstr))
                    for fn in files:
                        basefn = os.path.basename(fn)
                        try:
                            if os.path.exists(itpath / basefn) and not overwrite:
                                pass
                            else:
                                shutil.copy(fn, itpath)
                                print(f"{fn} -> {itpath}")
                        except IsADirectoryError:
                            target = itpath / basefn

                            # EITHER: Rewrite or Continue
                            if os.path.isdir(target):
                                if overwrite:
                                    shutil.rmtree(target)
                                else:
                                    continue
                            print(f"{fn} -> {target}")
                            shutil.copytree(fn, target)
