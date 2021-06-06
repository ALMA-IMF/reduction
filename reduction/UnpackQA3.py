from casatools import msmetadata, table
tb = table()
msmd = msmetadata()
import glob
import shutil, os

asdm_eb_tbls = glob.glob("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/2021_QA3_Deliveries/*/*/ASDM_EXECBLOCK")

mousmap = {}
for tbn in asdm_eb_tbls:
    tb.open(tbn)
    sessref = tb.getcol('sessionReference')
    mous = sessref[0].split()[1].split("/")[-1].strip('"')
    if mous in mousmap:
        mousmap[mous].append(tbn)
    else:
        mousmap[mous] = [tbn]
    tb.close()

mous_pathmap = {x.split("/")[-1].split("_")[-1]:x for x in glob.glob("/orange/adamginsburg/ALMA_IMF/201*/science_goal.uid*/group*/member*")}


not_yet_updated = []

for ii,mouskey in enumerate(mousmap):
    calibrated_path = mous_pathmap[mouskey]+"/calibrated"
    for msname in mousmap[mouskey]:
        splitname = msname.split('/')[-2]
        splitpath = "/".join(msname.split('/')[:-1])
        
        new_splitpath = calibrated_path + "/" + splitname
        old_splitpath = calibrated_path + "/" + splitname + "_old"

        if not os.path.exists(old_splitpath):
            if 'W43-MM1' not in splitpath:
                print()
                print(splitpath.split('/')[-2])
                print(new_splitpath, old_splitpath, splitpath)
                if not os.path.exists(new_splitpath):
                    print(f"Missing {new_splitpath}")
                else:
                    not_yet_updated.append(new_splitpath)

            if os.path.exists(new_splitpath):
                print(f"mv {new_splitpath} {old_splitpath}")
                print(f"link {splitpath} {new_splitpath}")
                #shutil.move(new_splitpath, old_splitpath)
                #os.symlink(splitpath, new_splitpath)
            else:
                if 'W43-MM1' not in splitpath:
                    print(f"****** {new_splitpath} did not exist! *******")
                    print(f"link {splitpath} {new_splitpath}")
                    #os.symlink(splitpath, new_splitpath)


if False:
    # this can only be run once; if it's run twice, it will error with "YIPE" telling you that the 'old' path already exists
    for ii,mouskey in enumerate(mousmap):
        calibrated_path = mous_pathmap[mouskey]+"/calibrated"
        splitname = mousmap[mouskey].split('/')[-2]
        splitpath = "/".join(mousmap[mouskey].split('/')[:-1])
        
        new_splitpath = calibrated_path + "/" + splitname
        old_splitpath = calibrated_path + "/" + splitname + "_old"
        
        if os.path.exists(old_splitpath):
            raise "YIPE"
        
        print(ii)
        if os.path.exists(new_splitpath):
            print(f"mv {new_splitpath} {old_splitpath}")
            print(f"link {splitpath} {new_splitpath}")
            #shutil.move(new_splitpath, old_splitpath)
            #os.symlink(splitpath, new_splitpath)
        else:
            print(f"****** {new_splitpath} did not exist! *******")
            print(f"link {splitpath} {new_splitpath}")
            #os.symlink(splitpath, new_splitpath)



if False: # only do this once, on April 30, 2021
    flagtabs = glob.glob("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.flagversions")
    for fn in flagtabs:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")

    contsplits = glob.glob("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.cont")

    for fn in contsplits:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")

    splits = glob.glob("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.split")
    concat_ms = glob.glob("/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.ms")

    for fn in splits+concat_ms:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")
