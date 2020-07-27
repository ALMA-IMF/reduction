import glob
from os import symlink, chdir, mkdir
from pathlib import Path
import os

spws = {3: list(range(4)),
        6: list(range(7)),}

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


dirnames = {'fullcubes': 'spw[0-9]_{config}_spw[0-9]',
            'linecubes': 'spw[0-9]_{config}_[!s]',
            'continuum': '.tt0'}


basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')

with open(basepath / '../scigoals/file_list.txt', 'w') as fh1:
    with open(basepath / '../scigoals/file_tree.txt', 'w') as fh2:

        for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
            if not os.path.exists(basepath / field):
                mkdir(basepath / field)
            for band in (3,6):
                bandpath = Path(f"B{band}")
                if not os.path.exists(basepath / field / bandpath):
                    mkdir(basepath / field / bandpath)
                for dirname, globstr in dirnames.items():
                    for config in ("12m", "7m12m"):
                        if not os.path.exists(basepath / field / bandpath / f"{dirname}_{config}"):
                            mkdir(basepath / field / bandpath / f"{dirname}_{config}")
                        cwd = os.getcwd()
                        chdir(basepath / field / bandpath / f"{dirname}_{config}")
                        dotdot = Path('../../../')
                        globbo = str(dotdot / f"{field}_B{band}*{globstr}*".format(config=config))
                        filelist = glob.glob(globbo)
                        #print(field, band, dirname, config, filelist)
                        for fn in filelist:
                            #print(f"Linking {dotdot / fn} to {os.getcwd()}")
                            basename = os.path.basename(fn)
                            if not os.path.exists(basename):
                                symlink(fn, basename)
                            elif not os.path.exists(os.readlink(basename)):
                                os.unlink(basename)
                                symlink(fn, basename)
                            fh1.write(os.path.realpath(basename) + "\n")
                            fh2.write(os.path.join(os.getcwd(), basename) + "\n")
                        chdir(cwd)
