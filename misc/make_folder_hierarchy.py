import glob
import os
import shutil

'''
Script that recreates the original folder hierarchy of the entire ALMA-IMF program and moves the renormalization delivery .ms.split.cal files into it. 
'''


original_path = "/lustre/roberto/ALMA_IMF/lines/science*/group*/member*"
new_basepath = "/lustre/roberto/ALMA_IMF/lines/normalized"

original_mouspathmap = {x.split("/")[-1].split("_")[-1]:x for x in glob.glob(original_path)}
new_mouspathmap = {x.split("/")[-1].split("_")[-1]:"/".join([new_basepath,x.split("/")[-3],x.split("/")[-2],x.split("/")[-1]]) for x in glob.glob(original_path)}
mous_list = original_mouspathmap.keys()


asdm_eb_tbls = glob.glob("/".join([new_basepath,"*","*","ASDM_EXECBLOCK"]))


mousmap = {mous_list[i]:[] for i in range(len(mous_list))}


for tbn in asdm_eb_tbls:
    tb.open(tbn)
    sessref = tb.getcol('sessionReference')
    #print(sessref)
    mous = sessref[0].split()[1].split("/")[-1].strip('"')
    #print(mous)
    mousmap[mous].append(tbn)
    tb.close    


for mouskey in mous_list: 
    #print(mousmap[mouskey])
    for EB in range(len(mousmap[mouskey])):
        #print(mousmap[mouskey][EB])
        calibrated_path = new_mouspathmap[mouskey]+"/calibrated"
        full_visib_path = mousmap[mouskey][EB].replace("/ASDM_EXECBLOCK","")
        visib_file = full_visib_path.split("/")[-1]
        if os.path.exists(calibrated_path): 
            print(calibrated_path+" exists, moving .ms.split.cal there.")
            shutil.move(full_visib_path,calibrated_path)
        else: 
            print(calibrated_path+" doesn't exist, creating it and moving .ms.split.cal there.") 
            os.makedirs(calibrated_path)
            shutil.move(full_visib_path,calibrated_path)
