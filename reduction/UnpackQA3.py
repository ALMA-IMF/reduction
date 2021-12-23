if 'msmd' not in locals():
    from casatools import msmetadata, table
    tb = table()
    msmd = msmetadata()
import glob
import shutil, os

basedir = '{basedir}'

asdm_eb_tbls = glob.glob("{basedir}/2017.1.01355.L/2021_QA3_Deliveries/*/*/ASDM_EXECBLOCK")

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

# mous_pathmap = {x.split("/")[-1].split("_")[-1]:x for x in glob.glob(f"{basedir}/201*/science_goal.uid*/group*/member*")}

mous_pathmap = {'X1b9': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1b5/group.uid___A001_X1296_X1b6/member.uid___A001_X1296_X1b9',
 'X1b7': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1b5/group.uid___A001_X1296_X1b6/member.uid___A001_X1296_X1b7',
 'X1bb': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1b5/group.uid___A001_X1296_X1b6/member.uid___A001_X1296_X1bb',
 'X1eb': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1eb',
 'X1e7': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e7',
 'X1e9': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e9',
 'X1e5': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e5',
 'X19b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X197/group.uid___A001_X1296_X198/member.uid___A001_X1296_X19b',
 'X19f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X197/group.uid___A001_X1296_X198/member.uid___A001_X1296_X19f',
 'X199': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X197/group.uid___A001_X1296_X198/member.uid___A001_X1296_X199',
 'X19d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X197/group.uid___A001_X1296_X198/member.uid___A001_X1296_X19d',
 'X1c1': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1bd/group.uid___A001_X1296_X1be/member.uid___A001_X1296_X1c1',
 'X1c3': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1bd/group.uid___A001_X1296_X1be/member.uid___A001_X1296_X1c3',
 'X1bf': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1bd/group.uid___A001_X1296_X1be/member.uid___A001_X1296_X1bf',
 'X1c5': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1bd/group.uid___A001_X1296_X1be/member.uid___A001_X1296_X1c5',
 'X16f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X167/group.uid___A001_X1296_X168/member.uid___A001_X1296_X16f',
 'X16d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X167/group.uid___A001_X1296_X168/member.uid___A001_X1296_X16d',
 'X16b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X167/group.uid___A001_X1296_X168/member.uid___A001_X1296_X16b',
 'X169': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X167/group.uid___A001_X1296_X168/member.uid___A001_X1296_X169',
 'X1d3': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1cf/group.uid___A001_X1296_X1d0/member.uid___A001_X1296_X1d3',
 'X1d7': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1cf/group.uid___A001_X1296_X1d0/member.uid___A001_X1296_X1d7',
 'X1d5': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1cf/group.uid___A001_X1296_X1d0/member.uid___A001_X1296_X1d5',
 'X1d1': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1cf/group.uid___A001_X1296_X1d0/member.uid___A001_X1296_X1d1',
 'X1e1': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1d9/group.uid___A001_X1296_X1da/member.uid___A001_X1296_X1e1',
 'X1dd': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1d9/group.uid___A001_X1296_X1da/member.uid___A001_X1296_X1dd',
 'X1df': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1d9/group.uid___A001_X1296_X1da/member.uid___A001_X1296_X1df',
 'X1db': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1d9/group.uid___A001_X1296_X1da/member.uid___A001_X1296_X1db',
 'X20d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X207/group.uid___A001_X1296_X208/member.uid___A001_X1296_X20d',
 'X20f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X207/group.uid___A001_X1296_X208/member.uid___A001_X1296_X20f',
 'X209': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X207/group.uid___A001_X1296_X208/member.uid___A001_X1296_X209',
 'X20b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X207/group.uid___A001_X1296_X208/member.uid___A001_X1296_X20b',
 'X11b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X119/group.uid___A001_X1296_X11a/member.uid___A001_X1296_X11b',
 'X11d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X119/group.uid___A001_X1296_X11a/member.uid___A001_X1296_X11d',
 'X11f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X119/group.uid___A001_X1296_X11a/member.uid___A001_X1296_X11f',
 'X143': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X141/group.uid___A001_X1296_X142/member.uid___A001_X1296_X143',
 'X149': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X141/group.uid___A001_X1296_X142/member.uid___A001_X1296_X149',
 'X147': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X141/group.uid___A001_X1296_X142/member.uid___A001_X1296_X147',
 'X145': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X141/group.uid___A001_X1296_X142/member.uid___A001_X1296_X145',
 'X1f9': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1f5/group.uid___A001_X1296_X1f6/member.uid___A001_X1296_X1f9',
 'X1fb': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1f5/group.uid___A001_X1296_X1f6/member.uid___A001_X1296_X1fb',
 'X1f7': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1f5/group.uid___A001_X1296_X1f6/member.uid___A001_X1296_X1f7',
 'X1fd': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1f5/group.uid___A001_X1296_X1f6/member.uid___A001_X1296_X1fd',
 'X203': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ff/group.uid___A001_X1296_X200/member.uid___A001_X1296_X203',
 'X205': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ff/group.uid___A001_X1296_X200/member.uid___A001_X1296_X205',
 'X201': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ff/group.uid___A001_X1296_X200/member.uid___A001_X1296_X201',
 'X161': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X15f/group.uid___A001_X1296_X160/member.uid___A001_X1296_X161',
 'X163': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X15f/group.uid___A001_X1296_X160/member.uid___A001_X1296_X163',
 'X165': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X15f/group.uid___A001_X1296_X160/member.uid___A001_X1296_X165',
 'X107': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X107',
 'X10b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X10b',
 'X10d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X10d',
 'X109': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X105/group.uid___A001_X1296_X106/member.uid___A001_X1296_X109',
 'X1c9': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1c7/group.uid___A001_X1296_X1c8/member.uid___A001_X1296_X1c9',
 'X1cd': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1c7/group.uid___A001_X1296_X1c8/member.uid___A001_X1296_X1cd',
 'X1cb': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1c7/group.uid___A001_X1296_X1c8/member.uid___A001_X1296_X1cb',
 'X1a3': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1a1/group.uid___A001_X1296_X1a2/member.uid___A001_X1296_X1a3',
 'X1a5': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1a1/group.uid___A001_X1296_X1a2/member.uid___A001_X1296_X1a5',
 'X1a7': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1a1/group.uid___A001_X1296_X1a2/member.uid___A001_X1296_X1a7',
 'X1a9': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1a1/group.uid___A001_X1296_X1a2/member.uid___A001_X1296_X1a9',
 'X1af': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ab/group.uid___A001_X1296_X1ac/member.uid___A001_X1296_X1af',
 'X1b3': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ab/group.uid___A001_X1296_X1ac/member.uid___A001_X1296_X1b3',
 'X1ad': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ab/group.uid___A001_X1296_X1ac/member.uid___A001_X1296_X1ad',
 'X1b1': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ab/group.uid___A001_X1296_X1ac/member.uid___A001_X1296_X1b1',
 'X1f1': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ed/group.uid___A001_X1296_X1ee/member.uid___A001_X1296_X1f1',
 'X1f3': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ed/group.uid___A001_X1296_X1ee/member.uid___A001_X1296_X1f3',
 'X1ef': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X1ed/group.uid___A001_X1296_X1ee/member.uid___A001_X1296_X1ef',
 'X117': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X10f/group.uid___A001_X1296_X110/member.uid___A001_X1296_X117',
 'X113': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X10f/group.uid___A001_X1296_X110/member.uid___A001_X1296_X113',
 'X111': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X10f/group.uid___A001_X1296_X110/member.uid___A001_X1296_X111',
 'X115': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X10f/group.uid___A001_X1296_X110/member.uid___A001_X1296_X115',
 'X13f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X137/group.uid___A001_X1296_X138/member.uid___A001_X1296_X13f',
 'X13d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X137/group.uid___A001_X1296_X138/member.uid___A001_X1296_X13d',
 'X139': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X137/group.uid___A001_X1296_X138/member.uid___A001_X1296_X139',
 'X13b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X137/group.uid___A001_X1296_X138/member.uid___A001_X1296_X13b',
 'X9f': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A001_X12f_X9f',
 'Xa0': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A002_X996c88_Xa0',
 'Xa3': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A002_X996c88_Xa3',
 'X87': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A002_X996c88_X87',
 'Xa4': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A002_X996c88_Xa4',
 'Xa1': f'{basedir}/2013.1.01365.S/science_goal.uid___A001_X12f_X9d/group.uid___A001_X12f_X9e/member.uid___A002_X996c88_Xa1',
 'X157': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X155/group.uid___A001_X1296_X156/member.uid___A001_X1296_X157',
 'X15d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X155/group.uid___A001_X1296_X156/member.uid___A001_X1296_X15d',
 'X159': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X155/group.uid___A001_X1296_X156/member.uid___A001_X1296_X159',
 'X15b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X155/group.uid___A001_X1296_X156/member.uid___A001_X1296_X15b',
 'X129': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X123/group.uid___A001_X1296_X124/member.uid___A001_X1296_X129',
 'X127': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X123/group.uid___A001_X1296_X124/member.uid___A001_X1296_X127',
 'X12b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X123/group.uid___A001_X1296_X124/member.uid___A001_X1296_X12b',
 'X125': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X123/group.uid___A001_X1296_X124/member.uid___A001_X1296_X125',
 'X217': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X217',
 'X215': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X215',
 'X213': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X211/group.uid___A001_X1296_X212/member.uid___A001_X1296_X213',
 'X14f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X14b/group.uid___A001_X1296_X14c/member.uid___A001_X1296_X14f',
 'X14d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X14b/group.uid___A001_X1296_X14c/member.uid___A001_X1296_X14d',
 'X153': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X14b/group.uid___A001_X1296_X14c/member.uid___A001_X1296_X153',
 'X151': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X14b/group.uid___A001_X1296_X14c/member.uid___A001_X1296_X151',
 'X131': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X12d/group.uid___A001_X1296_X12e/member.uid___A001_X1296_X131',
 'X135': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X12d/group.uid___A001_X1296_X12e/member.uid___A001_X1296_X135',
 'X133': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X12d/group.uid___A001_X1296_X12e/member.uid___A001_X1296_X133',
 'X12f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X12d/group.uid___A001_X1296_X12e/member.uid___A001_X1296_X12f',
 'X18b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X183/group.uid___A001_X1296_X184/member.uid___A001_X1296_X18b',
 'X189': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X183/group.uid___A001_X1296_X184/member.uid___A001_X1296_X189',
 'X185': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X183/group.uid___A001_X1296_X184/member.uid___A001_X1296_X185',
 'X187': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X183/group.uid___A001_X1296_X184/member.uid___A001_X1296_X187',
 'X177': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X171/group.uid___A001_X1296_X172/member.uid___A001_X1296_X177',
 'X173': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X171/group.uid___A001_X1296_X172/member.uid___A001_X1296_X173',
 'X175': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X171/group.uid___A001_X1296_X172/member.uid___A001_X1296_X175',
 'X195': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X18d/group.uid___A001_X1296_X18e/member.uid___A001_X1296_X195',
 'X193': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X18d/group.uid___A001_X1296_X18e/member.uid___A001_X1296_X193',
 'X18f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X18d/group.uid___A001_X1296_X18e/member.uid___A001_X1296_X18f',
 'X191': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X18d/group.uid___A001_X1296_X18e/member.uid___A001_X1296_X191',
 'X17f': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X179/group.uid___A001_X1296_X17a/member.uid___A001_X1296_X17f',
 'X181': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X179/group.uid___A001_X1296_X17a/member.uid___A001_X1296_X181',
 'X17b': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X179/group.uid___A001_X1296_X17a/member.uid___A001_X1296_X17b',
 'X17d': f'{basedir}/2017.1.01355.L/science_goal.uid___A001_X1296_X179/group.uid___A001_X1296_X17a/member.uid___A001_X1296_X17d',
 'X502': f'{basedir}/2015.1.01273.S/science_goal.uid___A001_X2f7_X500/group.uid___A001_X2f7_X501/member.uid___A002_X2f7_X502',
 'X50a': f'{basedir}/2015.1.01273.S/science_goal.uid___A001_X2f7_X500/group.uid___A001_X2f7_X501/member.uid___A002_X2f7_X50a',
 'X506': f'{basedir}/2015.1.01273.S/science_goal.uid___A001_X2f7_X500/group.uid___A001_X2f7_X501/member.uid___A002_X2f7_X506',
 'X504': f'{basedir}/2015.1.01273.S/science_goal.uid___A001_X2f7_X500/group.uid___A001_X2f7_X501/member.uid___A002_X2f7_X504'}



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
    flagtabs = glob.glob(f"{basedir}/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.flagversions")
    for fn in flagtabs:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")

    contsplits = glob.glob(f"{basedir}/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.cont")

    for fn in contsplits:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")

    splits = glob.glob(f"{basedir}/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.split")
    concat_ms = glob.glob(f"{basedir}/2017.1.01355.L/scigoals/science*/*/member*/calibrated/*.ms")

    for fn in splits+concat_ms:
        print(f'mv {fn} {fn+"_old_20210430"}')
        shutil.move(fn, fn+"_old_20210430")
