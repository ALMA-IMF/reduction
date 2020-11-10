import glob
from os import symlink, chdir, mkdir
from pathlib import Path
import os
import time

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


dirnames = {'fullcubes_12m': 'spw[0-9]_12M_spw[0-9]',
            'linecubes_12m': 'spw[0-9]_12M_[a-z][!p]',
            'fullcubes_7m12m': 'spw[0-9]_7M12M_spw[0-9]',
            'linecubes_7m12m': 'spw[0-9]_7M12M_[a-z][!p]',
            'bsens': 'bsens_12M_*.tt0',
            'cleanest': 'merged_12M*.tt0',
            '7m12m': 'merged_7M12M*.tt0',
            '7m12m_bsens': 'bsens_7M12M*.tt0',
            '7m': 'merged_7M_*.tt0',
            '7m_bsens': 'bsens_7M_*.tt0',
           }


basepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')

releasepath = Path('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/RestructuredImagingResults/')

with open(basepath / '../scigoals/file_list.txt', 'w') as fh1:
    with open(basepath / '../scigoals/file_tree.txt', 'w') as fh2:
        with open(basepath / '../scigoals/modtimes.txt', 'w') as fh3:

            for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
                if not os.path.exists(releasepath / field):
                    mkdir(releasepath / field)
                for band in (3,6):
                    bandpath = Path(f"B{band}")
                    if not os.path.exists(releasepath / field / bandpath):
                        mkdir(releasepath / field / bandpath)
                    for dirname, globstr in dirnames.items():
                        if not os.path.exists(releasepath / field / bandpath / dirname):
                            mkdir(releasepath / field / bandpath / dirname)
                        cwd = os.getcwd()
                        chdir(releasepath / field / bandpath / dirname)
                        globbo = str(basepath / f"{field}_B{band}*{globstr}*")
                        filelist = glob.glob(globbo)
                        fitsglobbo = str(basepath / f"{field}_B{band}*{globstr}*fits")
                        filelist += glob.glob(fitsglobbo)
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
                            newpath = os.path.join(os.getcwd(), basename)
                            fh2.write(newpath + "\n")
                            fh3.write(time.ctime(os.path.getmtime(basename)) + "  " +  newpath + "\n")
                        chdir(cwd)
