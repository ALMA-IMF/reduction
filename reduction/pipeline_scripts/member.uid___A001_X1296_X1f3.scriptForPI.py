# ALMA Data Reduction Script
# $Id: scriptForPI.py,v 1.23 2017/10/17 15:15:15 dpetry Exp $

# Calibration application

import os
import sys
import glob
from xml.etree import cElementTree as ET

applyonly = True

os.environ["LANG"] = "C"

print '*** ALMA scriptForPI ***'
casalog.origin('casa')
casalog.post('*** ALMA scriptForPI ***', 'INFO', 'scriptForPI')
casalog.post('$Id: scriptForPI.py,v 1.23 2017/10/17 15:15:15 dpetry Exp $', 'INFO', 'scriptForPI')

savingslevel=0
if globals().has_key("SPACESAVING"):
    print 'SPACESAVING =', SPACESAVING
    if (type(SPACESAVING)!=int or SPACESAVING<-1):
        sys.exit('ERROR: SPACESAVING value \"'+str(SPACESAVING)+'\" not permitted, must be int>=-1.\n'
                 + 'Valid values: 0 = no saving,\n'
                 + '              1 = delete *.ms.split,\n'
                 + '              2 = delete *.ms and *.ms.split,\n'
                 + '            >=3 = delete *.ms, *.ms.split, and if possible *.ms.split.cal'
                 + '             -1 = do not check disk space')
        
    savingslevel = SPACESAVING

dosplit = False # In case only pipeline imaging was done, the science SPWs will not be split out. Override using DOSPLIT.
if globals().has_key("DOSPLIT"):
    print 'DOSPLIT =', DOSPLIT
    if (type(DOSPLIT)!=bool):
        sys.exit('ERROR: DOSPLIT value \"'+str(DOSPLIT)+'\" not permitted, must be bool (True or False)')
    dosplit = DOSPLIT

scriptdir = os.getcwd()

if (os.path.basename(scriptdir) != 'script'):
    sys.exit('ERROR: Please start this script in directory \"script\".')

scriptnames = sorted(glob.glob('*uid*.ms.scriptForCalibration.py'))

pscriptnames = glob.glob('*casa_piperestorescript.py')
if len(pscriptnames)>1:
    print 'Found more than one piperestorescript:'
    print pscriptnames
    sys.exit('ERROR: non-unique piperestorescript')

p2scriptnames = glob.glob('*casa_pipescript.py')
if len(p2scriptnames)>1:
    print 'Found more than one pipescript:'
    print p2scriptnames
    sys.exit('ERROR: non-unique pipescript')

polcalscriptnames = glob.glob('*scriptForPolCalibration.py')
if len(polcalscriptnames)>1:
    print 'Found more than one scriptForPolCalibration:'
    print polcalscriptnames
    sys.exit('ERROR: non-unique scriptForPolCalibration')

fluxcalscriptnames = glob.glob('*scriptForFluxCalibration.py')
if len(fluxcalscriptnames)>1:
    print 'Found more than one scriptForFluxCalibration:'
    print fluxcalscriptnames
    sys.exit('ERROR: non-unique scriptForFluxCalibration')

imprepscriptnames = glob.glob('*scriptForImagingPrep.py')
if len(imprepscriptnames)>1:
    print 'Found more than one scriptForImagingPrep:'
    print imprepscriptnames
    sys.exit('ERROR: non-unique scriptForImagingPrep')

pipererun = False
istppipe = False

pprnames = glob.glob('*PPR*.xml') # old naming scheme
if len(pprnames)>1:
    print 'Found more than one PPR:'
    print pprnames
    sys.exit('ERROR: non-unique PPR')

if len(pprnames)==0:
    pprnames = glob.glob('*pprequest.xml')
    if len(pprnames)>1:
        print 'Found more than one PPR:'
        print pprnames
        sys.exit('ERROR: non-unique PPR')

if not os.path.exists('../calibration'):
    sys.exit('ERROR: Cannot find directory \"calibration\"')

manifestnames = glob.glob('*pipeline_manifest.xml')
if len(manifestnames)>0:
    print 'Found pipeline manifest(s):'
    print manifestnames
    for mname in manifestnames:
        themanifest = ET.parse(mname).find('ous/aux_products_file')
        os.system('cp '+mname+' ../calibration')
        if not themanifest==None:
            if themanifest.items()[0][0]=='name':
                os.chdir('../calibration')
                supportingfilenames = [themanifest.items()[0][1]]
                if os.path.exists(supportingfilenames[0]):
                    print "Unpacking "+supportingfilenames[0]+" ..."
                    os.system('tar xzf '+supportingfilenames[0])
                else:
                    print "WARNING: could not find the file "+supportingfilenames[0]+" in directory \"calibration\" although the pipeline manifest mentions it."
                os.chdir('../script')

else:
    if len(pprnames)>0:
        print "No pipeline manifest found."
    os.chdir('../calibration')
    supportingfilenames = glob.glob('*supporting.tgz')
    if len(supportingfilenames)>0:
        print 'Found tarball(s) containing supporting files:'
        print supportingfilenames
        for sname in supportingfilenames:
            os.system('tar xzf '+sname)
    else:
        supportingfilenames = glob.glob('*auxproducts.tgz')
        if len(supportingfilenames)>0:
            print 'Found tarball(s) containing auxiliary files:'
            print supportingfilenames
            for sname in supportingfilenames:
                os.system('tar xzf '+sname)

os.chdir(scriptdir)

if ((len(scriptnames) + len(pscriptnames))  == 0):
    if len(p2scriptnames)>0:
        print 'Pipeline calibration by pipeline rerun'
        pipererun = True
        jyperknames =  glob.glob('../calibration/*jyperk.csv')
        if len(jyperknames)==1:
            istppipe = True
        elif len(jyperknames)>1:
            print 'Found more than jyperk.csv file:'
            print jyperknames
            sys.exit('ERROR: non-unique jyperk.csv file')
    else:
        sys.exit('ERROR: No calibration script found.')

pprasdms = []
usedimpipe = False
if (len(pprnames)>0):
    for line in open(pprnames[0]):
        if "<AsdmDiskName>" in line:
            pprasdms.append(line[line.index('uid'):line.index('</')])

    tmppipe = os.popen("grep hif_makeimages "+pprnames[0]+" | wc -l")
    nummkim = int((tmppipe.readline()).rstrip('\n'))
    tmppipe.close()
    if ( nummkim > 1 ):
        print "Science pipeline imaging use was foreseen in PPR."
        tmppipe = os.popen("ls ../product/*_sci.spw*.fits 2>/dev/null | wc -l ")
        numscienceim = int((tmppipe.readline()).rstrip('\n'))
        tmppipe.close()
        tmppipe = os.popen("cat *scriptForImaging.py | grep -v \"#\" | wc -l ")
        numuncomlines = int((tmppipe.readline()).rstrip('\n'))
        tmppipe.close()
        if (numscienceim>0 and numuncomlines==0):
            print "Science images and only a dummy scriptForImaging were found. Will assume only pipeline imaging took place."
            usedimpipe = True

try:
    if os.path.islink('../raw'):
        print "Note: your raw directory is a link."
    os.chdir('../raw/')
except:
    sys.exit('ERROR: directory \"raw\" not present.\n'
             '       Please download your raw data and unpack it to create and fill directory \"raw\".') 

# check available disk space
tmppipe = os.popen("df -P -m $PWD | awk '/[0-9]%/{print $(NF-2)}'")
avspace = int((tmppipe.readline()).rstrip('\n'))
tmppipe.close()
tmppipe = os.popen("du -smc $PWD | grep total | tail -n 1 | cut -f1")
packspace = int((tmppipe.readline()).rstrip('\n'))
tmppipe.close()

spacefactor = 0.

fcalpresent = False
if len(fluxcalscriptnames)>0:
    fcalpresent = True
    spacefactor = 1.

impreppresent = False
if len(imprepscriptnames)>0:
    impreppresent = True
    spacefactor = 1.

polcalpresent = False
if  len(polcalscriptnames)>0:
    polcalpresent = True
    spacefactor = 1.

spaceneed = packspace*(11.+spacefactor*3.)

if (savingslevel==1):
    print 'Will delete intermediate MSs named *.ms.split to save disk space.'
    spaceneed = packspace*(7.+spacefactor*3.)   
elif (savingslevel==2):
    print 'Will delete intermediate MSs named *.ms and *.ms.split to save disk space.'
    spaceneed = packspace*(3.+spacefactor*3.)   
elif (savingslevel>=3):
    print 'Will delete all intermediate MSs to save disk space.'
    spaceneed = packspace*(3.+spacefactor*3.)   
elif (savingslevel==-1):
    print 'Will not check available disk space.'
    spaceneed = 0
    

print 'Found ',avspace,' MB of available free disk space.'
print 'Expect to need up to ',spaceneed,' MB of free disk space.'
if(spaceneed>avspace):
    print 'ERROR: not enough free disk space. Need at least '+str(spaceneed)+' MB.'
    print 'If you think this is not correct and want to try anyway, please set SPACESAVING to -1.'
    sys.exit('ERROR: probably not enough free disk space.')

asdmnames = glob.glob('uid*.asdm.sdm')


if len(asdmnames) == 0:
    sys.exit('ERROR: No ASDM found in directory \"raw\".')

print 'Found the following ASDMs:', asdmnames

for i in range(len(asdmnames)):
    asdmnames[i] = asdmnames[i].replace('.asdm.sdm', '')


scriptasdms = []
for i in range(len(scriptnames)):
    scriptasdms.append(scriptnames[i].replace('.ms.scriptForCalibration.py', ''))

allasdms = []
allasdms.extend(scriptasdms)
allasdms.extend(pprasdms)

missing = []

if sorted(asdmnames) != sorted(allasdms):
    print "WARNING: Inconsistency between ASDMs and calibration scripts"
    print "         Calibration info available for: ", sorted(allasdms)
    print "         ASDMs available in directory raw: ", sorted(asdmnames)
    for myname in allasdms:
        if not (myname in asdmnames):
            missing.append(myname)
    if len(missing)==0:
        print "       The ASDMs without calibration info are probably \"QA semipass\" data which were"
        print "       not used to create the science products and are not needed to achieve the science goal."
        print "       Only the ASDMs for which there is calibration information will be calibrated."
    else:
        print "ERROR: the following ASDMs have calibration information but are absent from directory \"raw\":"
        print missing
        print "Will try to proceed with the rest ..."
        for myname in missing:
            if myname in scriptasdms:
                scriptasdms.remove(myname)
            if myname in pprasdms:
                pprasdms.remove(myname)
            if myname in allasdms:
                allasdms.remove(myname)
        if(len(allasdms)==0):
            sys.exit('ERROR: Nothing to process.')

os.chdir(scriptdir)

ephnames = glob.glob('../calibration/*.eph')

if len(ephnames)>0:
    print "Note: this dataset uses external ephemerides."
    print "      You can find them in directory \"calibration\"."

if os.path.exists('../calibrated') and not globals().has_key("USEMS"):
    os.chdir('../calibrated')
    sys.exit('WARNING: will stop here since directory '+os.path.abspath(os.path.curdir)
             +' already exists.\nPlease delete it first and then try again.')
    
if not globals().has_key("USEMS"):
    print 'Creating destination directory for calibrated data.'
    os.mkdir('../calibrated')
else:
    print 'You have set USEMS. Will use your pre-imported MSs rather than importing them from the ASDMs.'
    for asdmname in scriptasdms:
        if not os.path.exists('../calibrated/'+asdmname+'.calibration/'+asdmname+'.ms'):
            print 'When USEMS is set, you must have created the directory \"calibrated\" and'
            print 'put the imported raw MSs \"uid*.ms\" in individual working directories'
            print 'named \"uid*.calibration\" inside \"calibrated\".'
            sys.exit('ERROR: cannot find calibrated/'+asdmname+'.calibration/'+asdmname+'.ms')
    
os.chdir('../calibrated')


for asdmname in scriptasdms:

    print 'Processing ASDM '+asdmname
    
    if not globals().has_key("USEMS"):
        os.mkdir(asdmname+'.calibration')

    os.chdir(asdmname+'.calibration')

    if not os.path.exists('../../raw/'+asdmname+'.asdm.sdm'):
        sys.exit('ERROR: cannot find raw/'+asdmname+'.asdm.sdm')

    os.system('ln -sf ../../raw/'+asdmname+'.asdm.sdm '+asdmname)

    for ephname in ephnames: 
        os.system('ln -sf ../'+ephname)

    execfile('../../script/'+asdmname+'.ms.scriptForCalibration.py')

    if not os.path.exists(asdmname+'.ms.split.cal'):
        print 'ERROR: '+asdmname+'.ms.split.cal was not created.'
    else:
        print asdmname+'.ms.split.cal was produced successfully, moving it to \"calibrated\" directory.'
        os.system('mv '+asdmname+'.ms.split.cal ..')
        if (savingslevel>=2):
            print 'Deleting intermediate MS ', asdmname+'.ms'
            os.system('rm -rf '+asdmname+'.ms')
        if (savingslevel>=1):
            print 'Deleting intermediate MS ', asdmname+'.ms.split'
            os.system('rm -rf '+asdmname+'.ms.split')

    os.chdir('..')

if (len(pprasdms)>0):

    if dir().count('h_init')==0:
        sys.exit("ERROR: Pipeline not available. Make sure you start CASA with option --pipeline to activate the pipeline.") 

    if pipererun:
        print 'Processing the ASDMs ', pprasdms, ' in pipeline rerun.'
    else:
        print 'Processing the ASDMs ', pprasdms, ' using pipeline restore.'

        os.mkdir('rawdata')
        os.chdir('rawdata')
        for asdmname in pprasdms:
            if not os.path.exists('../../raw/'+asdmname+'.asdm.sdm'):
                sys.exit('ERROR: cannot find raw/'+asdmname+'.asdm.sdm')

            os.system('ln -sf ../../raw/'+asdmname+'.asdm.sdm '+asdmname)

        os.chdir('..')
        
        os.system('ln -sf ../calibration products')

    os.mkdir('working')
    os.chdir('working')

    if pipererun:
        for asdmname in pprasdms:
            if not os.path.exists('../../raw/'+asdmname+'.asdm.sdm'):
                sys.exit('ERROR: cannot find raw/'+asdmname+'.asdm.sdm')

            os.system('ln -sf ../../raw/'+asdmname+'.asdm.sdm '+asdmname)

        if istppipe:
            os.system('cp ../../calibration/*jyperk.csv ./jyperk.csv')

        os.system('cp ../../calibration/*flagtemplate.txt .')

        os.system('cp ../../calibration/*pipeline_manifest.xml .')

        fluxfiles = glob.glob("../../calibration/*flux.csv")
        if len(fluxfiles)>0:
            if len(fluxfiles)==1:
                os.system('cp ../../calibration/*flux.csv ./flux.csv')
            else:
                print fluxfiles
                sys.exit('ERROR: found more than one *flux.csv file in directory "calibration"')

        antennaposfiles = glob.glob("../../calibration/*antennapos.csv")
        if len(antennaposfiles)>0:
            if len(antennaposfiles)==1:
                os.system('cp ../../calibration/*antennapos.csv ./antennapos.csv')
            else:
                print antennaposfiles
                sys.exit('ERROR: found more than one *antennapos.csv file in directory "calibration"')

        contfiles = glob.glob("../../calibration/*cont.dat")
        if len(contfiles)>0:
            if len(contfiles)==1:
                os.system('cp ../../calibration/*cont.dat ./cont.dat')
            else:
                print contfiles
                sys.exit('ERROR: found more than one *cont.dat file in directory "calibration"')

        print "Directory \"working\" set up for pipeline re-run:"
        os.system('ls -l')
        
        execfile('../../script/'+p2scriptnames[0])

    else:
        print "now running ", pscriptnames[0]
        execfile('../../script/'+pscriptnames[0])

    for asdmname in pprasdms:
        if not os.path.exists(asdmname+'.ms'):
            print 'ERROR: '+asdmname+'.ms was not created.'
        elif pipererun and istppipe:
            tpmsnames = glob.glob(asdmname+'*.ms_bl')
            if len(tpmsnames)==0:
                print 'ERROR: '+asdmname+'*.ms_bl was not created.'
            else:
                os.system('mv '+asdmname+'*.ms_bl ..')
                
            if (savingslevel>=2):
                print 'Deleting intermediate MS ', asdmname+'.ms'
                os.system('rm -rf '+asdmname+'.ms')
        else:
            msmd.open(asdmname+'.ms')
            targetspws = msmd.spwsforintent('OBSERVE_TARGET*')
            sciencespws = ''
            outputspws = ''
            i = 0
            for myspw in targetspws:
                if msmd.nchan(myspw)>4:
                            sciencespws += str(myspw)+','
                            outputspws += str(i)+','
                            i += 1
            sciencespws = sciencespws.rstrip(',')
            outputspws = outputspws.rstrip(',')
            msmd.close()
            if usedimpipe and not dosplit:
                print 'Imaging pipeline was used. Will not create '+asdmname+'.ms.split.cal'
                print 'Linking MS '+asdmname+'.ms into directory "calibrated"'
                os.system('cd ..; ln -sf working/'+asdmname+'.ms')
            else:
                print 'Splitting out science SPWs for '+asdmname+': '+sciencespws
                print 'Note: SPW IDs will not be reindexed to start at 0!'
                mstransform(vis=asdmname+'.ms', outputvis=asdmname+'.ms.split.cal', spw = sciencespws, reindex=False)
                if not os.path.exists(asdmname+'.ms.split.cal'):
                    print 'ERROR: '+asdmname+'.ms.split.cal was not created.'
                else:
                    os.system('mv '+asdmname+'.ms.split.cal ..')
                    if (savingslevel>=2):
                        print 'Deleting intermediate MS ', asdmname+'.ms'
                        os.system('rm -rf '+asdmname+'.ms')

    os.chdir('..')

if polcalpresent:
    print 'Executing scriptForPolCalibration.py ...'
    execfile('../script/'+polcalscriptnames[0])

if fcalpresent:
    print 'Executing scriptForFluxCalibration.py ...'
    execfile('../script/'+fluxcalscriptnames[0])

if impreppresent:
    print 'Executing scriptForImagingPrep.py ...'
    execfile('../script/'+imprepscriptnames[0])

if (savingslevel>=3) and os.path.exists('calibrated.ms'):
    for asdmname in allasdms:
        print 'Deleting intermediate MS ', asdmname+'.ms.split.cal'
        os.system('rm -rf '+asdmname+'.ms.split.cal')

print 'Done. Please find results in directory \"calibrated\".'
casalog.origin('casa')
casalog.post('ALMA scriptForPI completed.', 'INFO', 'scriptForPI')
