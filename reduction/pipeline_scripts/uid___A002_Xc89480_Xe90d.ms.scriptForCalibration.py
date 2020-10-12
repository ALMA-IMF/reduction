# ALMA Data Reduction Script

# Calibration

thesteps = []
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column',
              19: 'Save flags after applycal'}

applyonly=True
if 'applyonly' not in globals(): applyonly = False
try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps
applyonly=True

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]
# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

import casadef

if applyonly != True: es = aU.stuffForScienceDataReduction() 


if re.search('^5.1.1', '.'.join([str(i) for i in cu.version().tolist()[:-1]])) == None:
    print("WARNING: Script is being run with a different version of CASA than it was first run.  "
          "This is expected to be OK as Timea has tested with a few versions.")



# SETUP FOR ALMA-IMF PIPELINE
# make calibrated directory: if this already exists, we expect a crash
os.mkdir('../calibrated')
os.chdir('../calibrated')
os.symlink('../uid___A002_Xc89480_Xe90d.asdm.sdm', 'uid___A002_Xc89480_Xe90d.asdm.sdm')



# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: G337.92,J1617-5848
# CALIBRATE_BANDPASS: J1617-5848
# CALIBRATE_DIFFGAIN: 
# CALIBRATE_FLUX: J1617-5848
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J1650-5044
# CALIBRATE_POINTING: J1617-5848
# OBSERVE_CHECK: 
# OBSERVE_TARGET: G337.92

# Using reference antenna = DA59

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_Xc89480_Xe90d.ms') == False:
    importasdm('uid___A002_Xc89480_Xe90d', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=False, process_caldevice=False)
    if not os.path.exists('uid___A002_Xc89480_Xe90d.ms.flagversions'):
      print 'ERROR in importasdm. Output MS is probably not useful. Will stop here.'
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xc89480_Xe90d.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xc89480_Xe90d.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.listobs')
  listobs(vis = 'uid___A002_Xc89480_Xe90d.ms',
    listfile = 'uid___A002_Xc89480_Xe90d.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_Xc89480_Xe90d.ms',
    mode = 'manual',
    spw = '5~12,17~32',
    autocorr = True,
    flagbackup = False)

# Added by TCS due to outlying phase solutions
  flagdata(vis = 'uid___A002_Xc89480_Xe90d.ms',
    mode = 'manual',
    spw = '25,27,29,31',
    antenna = 'DA44', 
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xc89480_Xe90d.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xc89480_Xe90d.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xc89480_Xe90d.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xc89480_Xe90d.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xc89480_Xe90d.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.wvr',
    spw = [25, 27, 29, 31],
    smooth = '6.048s',
    toffset = 0,
    tie = ['G337.92,J1650-5044'],
    statsource = 'G337.92')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xc89480_Xe90d.ms.wvr', spw='25', antenna='DA59',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xc89480_Xe90d.ms.wvr.plots/uid___A002_Xc89480_Xe90d.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.tsys') 
  gencal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xc89480_Xe90d.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xc89480_Xe90d.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=False, 
    field='', figfile='uid___A002_Xc89480_Xe90d.ms.tsys.plots.overlayTime/uid___A002_Xc89480_Xe90d.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.tsys', msName='uid___A002_Xc89480_Xe90d.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Warning: no baseline run found for following antenna(s): ['PM01'].
  
  # Position for antenna DV20 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA65 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA64 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA49 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA60 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA46 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV15 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV14 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV23 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV25 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA63 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA62 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV09 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV10 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV22 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV04 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA53 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA50 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA56 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DA59 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV03 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV01 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV16 is derived from baseline run made on 2018-01-20 05:53:41.
  
  # Position for antenna DV24 is derived from baseline run made on 2018-01-20 05:53:41.
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.antpos') 
  gencal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA46,DA49,DA50,DA53,DA56,DA59,DA60,DA62,DA63,DA64,DA65,DV01,DV03,DV04,DV09,DV10,DV14,DV15,DV16,DV20,DV22,DV23,DV24,DV25',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [-2.24034e-04,5.60846e-04,5.30174e-05,-1.95680e-05,4.99547e-04,1.62531e-04,7.49390e-05,2.52565e-04,5.08937e-05,-4.21727e-04,1.09451e-03,4.38716e-04,9.11857e-05,1.60062e-04,-1.71573e-05,3.98466e-04,-6.83681e-04,-3.67813e-04,3.79109e-04,-1.13295e-04,-2.11257e-04,-2.21331e-04,5.54393e-04,1.67316e-04,-2.90802e-04,1.03316e-03,3.38398e-04,4.98023e-04,-8.92690e-04,-5.19646e-04,2.59070e-04,-3.77194e-04,-2.85423e-04,1.84043e-04,5.19186e-05,-1.56412e-05,1.57472e-04,-4.63086e-06,-1.64848e-04,3.42332e-04,-7.15470e-04,-3.20177e-04,-1.31220e-04,6.03422e-04,1.40662e-04,2.89878e-04,3.90147e-04,2.29889e-04,7.29142e-04,-1.09842e-03,-5.14426e-04,5.45672e-04,-7.10713e-04,-2.43412e-04,1.70738e-04,-1.85744e-05,-1.01851e-04,-9.46586e-05,7.43842e-04,2.94957e-04,2.21853e-04,1.97205e-04,-1.48408e-05,1.95242e-04,-3.09346e-05,-4.76387e-05,-1.04122e-04,8.22402e-04,3.94492e-04,1.68857e-07,6.33483e-04,9.23297e-05])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DV14     7.29142e-04   -1.09842e-03   -5.14426e-04    1.41520e-03      2018-01-20 05:53:41
  # DA53    -4.21727e-04    1.09451e-03    4.38716e-04    1.25231e-03      2018-01-20 05:53:41
  # DA64     4.98023e-04   -8.92690e-04   -5.19646e-04    1.14671e-03      2018-01-20 05:53:41
  # DA63    -2.90802e-04    1.03316e-03    3.38398e-04    1.12538e-03      2018-01-20 05:53:41
  # DV15     5.45672e-04   -7.10713e-04   -2.43412e-04    9.28505e-04      2018-01-20 05:53:41
  # DV24    -1.04122e-04    8.22402e-04    3.94492e-04    9.18047e-04      2018-01-20 05:53:41
  # DA59     3.98466e-04   -6.83681e-04   -3.67813e-04    8.72629e-04      2018-01-20 05:53:41
  # DV04     3.42332e-04   -7.15470e-04   -3.20177e-04    8.55337e-04      2018-01-20 05:53:41
  # DV20    -9.46586e-05    7.43842e-04    2.94957e-04    8.05767e-04      2018-01-20 05:53:41
  # DV25     1.68857e-07    6.33483e-04    9.23297e-05    6.40176e-04      2018-01-20 05:53:41
  # DV09    -1.31220e-04    6.03422e-04    1.40662e-04    6.33343e-04      2018-01-20 05:53:41
  # DA62    -2.21331e-04    5.54393e-04    1.67316e-04    6.19947e-04      2018-01-20 05:53:41
  # DA46    -2.24034e-04    5.60846e-04    5.30174e-05    6.06259e-04      2018-01-20 05:53:41
  # DA65     2.59070e-04   -3.77194e-04   -2.85423e-04    5.39313e-04      2018-01-20 05:53:41
  # DV10     2.89878e-04    3.90147e-04    2.29889e-04    5.37674e-04      2018-01-20 05:53:41
  # DA49    -1.95680e-05    4.99547e-04    1.62531e-04    5.25686e-04      2018-01-20 05:53:41
  # DA60     3.79109e-04   -1.13295e-04   -2.11257e-04    4.48541e-04      2018-01-20 05:53:41
  # DV22     2.21853e-04    1.97205e-04   -1.48408e-05    2.97202e-04      2018-01-20 05:53:41
  # DA50     7.49390e-05    2.52565e-04    5.08937e-05    2.68319e-04      2018-01-20 05:53:41
  # DV03     1.57472e-04   -4.63086e-06   -1.64848e-04    2.28022e-04      2018-01-20 05:53:41
  # DV23     1.95242e-04   -3.09346e-05   -4.76387e-05    2.03337e-04      2018-01-20 05:53:41
  # DV16     1.70738e-04   -1.85744e-05   -1.01851e-04    1.99675e-04      2018-01-20 05:53:41
  # DV01     1.84043e-04    5.19186e-05   -1.56412e-05    1.91865e-04      2018-01-20 05:53:41
  # DA56     9.11857e-05    1.60062e-04   -1.71573e-05    1.85011e-04      2018-01-20 05:53:41
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xc89480_Xe90d.ms', tsystable = 'uid___A002_Xc89480_Xe90d.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    field = '0',
    spw = '25,27,29,31',
    gaintable = ['uid___A002_Xc89480_Xe90d.ms.tsys', 'uid___A002_Xc89480_Xe90d.ms.wvr', 'uid___A002_Xc89480_Xe90d.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J1650-5044 didn't have any Tsys measurement, so I used the one made on G337.92. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    field = '1',
    spw = '25,27,29,31',
    gaintable = ['uid___A002_Xc89480_Xe90d.ms.tsys', 'uid___A002_Xc89480_Xe90d.ms.wvr', 'uid___A002_Xc89480_Xe90d.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xc89480_Xe90d.ms',
    field = '2~8',
    spw = '25,27,29,31',
    gaintable = ['uid___A002_Xc89480_Xe90d.ms.tsys', 'uid___A002_Xc89480_Xe90d.ms.wvr', 'uid___A002_Xc89480_Xe90d.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xc89480_Xe90d.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split') 
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.flagversions') 
  
  split(vis = 'uid___A002_Xc89480_Xe90d.ms',
    outputvis = 'uid___A002_Xc89480_Xe90d.ms.split',
    datacolumn = 'corrected',
    spw = '25,27,29,31',
    keepflags = True)
  
  

print "# Calibration"

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.listobs')
  listobs(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    listfile = 'uid___A002_Xc89480_Xe90d.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xc89480_Xe90d.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

#  setjy(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
#    standard = 'manual',
#    field = 'J1617-5848',
#    fluxdensity = [1.01673380666, 0, 0, 0],
#    spix = -0.907650117476,
#    reffreq = '98.2615523779GHz')
  
  
  setjy(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    standard = 'manual',
    field = 'J1617-5848',
    fluxdensity = [1.01673380666, 0, 0, 0],
    spix = -0.907650117476,
    reffreq = '98.2615523779GHz')

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.ap_pre_bandpass',
    field = '1', # J1617-5848
    spw = '0:0~1919,1:0~1919,2:0~1919,3:0~1919',
    scan = '4,8', #'1,3',
    solint = 'int',
    refant = 'DA59',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.ap_pre_bandpass', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.bandpass',
    field = '1', #'0', # J1617-5848
    scan = '4,8', #'1,3',
    solint = 'inf',
    combine = 'scan',
    refant = 'DA59',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xc89480_Xe90d.ms.split.ap_pre_bandpass')
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch') 
  
  bandpass(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch',
    field = '1', #'0', # J1617-5848
    scan = '4,8', #'1,3',
    solint = 'inf,20ch',
    combine = 'scan',
    refant = 'DA59',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xc89480_Xe90d.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.bandpass', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.phase_int',
    field = '0~1', # J1617-5848,J1650-5044
    solint = 'int',
    refant = 'DA59',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.phase_int', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.ampli_inf',
    field = '0~1', # J1617-5848,J1650-5044
    solint = 'inf',
    refant = 'DA59',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch', 'uid___A002_Xc89480_Xe90d.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.ampli_inf', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xc89480_Xe90d.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xc89480_Xe90d.ms.split.flux_inf',
    reference = '0') # J1617-5848
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xc89480_Xe90d.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xc89480_Xe90d.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    caltable = 'uid___A002_Xc89480_Xe90d.ms.split.phase_inf',
    field = '0~1', # J1617-5848,J1650-5044
    solint = 'inf',
    refant = 'DA59',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xc89480_Xe90d.ms.split.phase_inf', msName='uid___A002_Xc89480_Xe90d.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0']: # J1617-5848
    applycal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch', 'uid___A002_Xc89480_Xe90d.ms.split.phase_int', 'uid___A002_Xc89480_Xe90d.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    field = '1,2~8', # G337.92
    gaintable = ['uid___A002_Xc89480_Xe90d.ms.split.bandpass_smooth20ch', 'uid___A002_Xc89480_Xe90d.ms.split.phase_inf', 'uid___A002_Xc89480_Xe90d.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J1650-5044
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.cal') 
  os.system('rm -rf uid___A002_Xc89480_Xe90d.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  split(vis = 'uid___A002_Xc89480_Xe90d.ms.split',
    outputvis = 'uid___A002_Xc89480_Xe90d.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xc89480_Xe90d.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

