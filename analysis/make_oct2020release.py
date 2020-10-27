import glob
import os
import shutil

from pathlib import Path

cwd = os.getcwd()
basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')
releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/October2020Release/')
os.chdir(basepath)

for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    for band in ('B3','B6'):
        for imtype,itgl in zip(('cleanest', 'bsens', '7m12m', ), ('continuum_merged_12M', 'bsens_12M', '7M12M')):
            itpath = releasepath / field / band / imtype
            itpath.mkdir(parents=True, exist_ok=True)

            for suffix in ('image.tt0.fits', 'image.tt0.pbcor.fits', "image.tt0", "model.tt0", "image.tt1", "model.tt1", "psf.tt0", "psf.tt1", "residual.tt0", "residual.tt1"):

                for globstr in (f"{field}*_{band}_*{itgl}*robust0_*selfcal[0-9]*finaliter.{suffix}",
                                f"{field}*_{band}_*{itgl}*robust0_*preselfcal.{suffix}"):

                    files = glob.glob(str(basepath / globstr))
                    for fn in files:
                        try:
                            if not os.path.exists(itpath):
                                shutil.copy(fn, itpath)
                                print(f"{fn} -> {itpath}")
                            else:
                                continue
                        except IsADirectoryError:
                            target = itpath / os.path.basename(fn)

                            # EITHER: Rewrite or Continue
                            if os.path.isdir(target):
                                # If it already exists, skip
                                # comment this line and uncomment the next if you want to overwrite
                                continue
                                #shutil.rmtree(target)
                            print(f"{fn} -> {target}")
                            shutil.copytree(fn, target)
