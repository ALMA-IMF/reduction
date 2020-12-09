#############################
#
# Template script to extract, concatenate, regrid, and clean the N2H+ visibility data of G353.41
#
#############################
import sys
sys.path.append("/nina/hongli/.hlwk/myModule")
sys.path.append("/nina/hongli/.hlwk/myModule/analysis_scripts") # This is for Analysis utilities
import analysisUtils as au
from collections import OrderedDict
import glob
from astropy import units as u
import numpy as np
from taskinit import msmdtool, iatool
msmd = msmdtool()
ia = iatool()



step_title = {
              1: 'Continuum subtraction',
              2: 'Concatenate 7m + 12m array datasets',
              3: 'Check the relative weights of 12m array and 7m array visibilities',
              4: 'Prepare for some final parameter for clean',
              5: 'CLEAN 12m+7m cube',
}
 
# The Python variable 'mysteps' will control which steps
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.



field = 'G353.41'
phasecenter = '17:30:26.280 -034.41.49.700' # which can be obtained from the weblog
band = 'B3'
targetspw = 'spw0'

userpars={'0_7M':
          {'vispath':'../../../../member.uid___A001_X1296_X1d5/preimage/',
           'visname':'*spw0.split',
           'fitspw':'0:20~889;1200~2028', # for the continuum subtraction, which can be roughly estimated from the find_cont on the weblog page
           'set':'7M',
          },

          '1_TM1':
          {'vispath':'../../../../member.uid___A001_X1296_X1d1/preimage/',
           'visname':'*spw0.split',
           'fitspw':'0:20~880;1151~1900', # for the continuum subtraction; which can be estimated from the find_cont on the weblog page
           'set':'TM1',
          },

          '2_TM2':
          {'vispath':'../../../../member.uid___A001_X1296_X1d3/preimage/',
           'visname':'*spw0.split',
           'fitspw':'0:20~880;1151~1900', # for the continuum subtraction; which can be estimated from the find_cont on the weblog page
           'set':'TM2',
          },
 
}

userpars = OrderedDict(sorted(userpars.items()))

# parameters for melecule tracers
molepars = {'0_n2h_123_012':
            {'mole':'n2h',
             'restfreq':'93.173700GHz',
             'vlsr':'-18km/s', #test for -28 , actual for -18
             'cubewidth':'32km/s', # test for 5, actual for 40
            },
           }
molepars = OrderedDict(sorted(molepars.items()))



#mysteps = [1,2,3,4]
mysteps = [5]

def thesteps(mysteps):
  thesteps=[]
  try:
    print('List of steps to be executed ...', mysteps)
    thesteps = mysteps
  except:
    print('global variable mysteps not set.')
  if (thesteps==[]):
    thesteps = range(0,len(step_title))
    print('Executing all steps: ', thesteps)
  return(thesteps)














###############
# step 1: Continuum subtraction on the split data
###############


mystep = 1
if(mystep in thesteps(mysteps)):

  
  os.system('rm -rf *.contsub')

  all_split = [] # for non continuum subtraction ms files in mystep=2
  all_contsub = [] # for continuum subtraction ms files in mystep=2

  for pars in userpars:
    vispath = userpars[pars]['vispath']    
    visname = userpars[pars]['visname']
    fitspw = userpars[pars]['fitspw']
    for name in glob.glob(vispath+visname):
      invis = name
      uvcontsub(vis = invis, 
        field = '',
        fitspw = fitspw,
        excludechans = False,
        fitorder = 0)
      all_split = all_split+[invis]
      all_contsub = all_contsub+[invis+'.contsub']

  #after the for loop, you can obtain files with the extension '.contsub'

###############
# step 2: Concatenate 7m + 12m array datasets
###############

mystep = 2
if(mystep in thesteps(mysteps)):

  os.system('rm -rf '+field+'_all_split.ms')
  os.system('rm -rf '+field+'_all_split.ms.contsub')

# Concatenate
  concat(vis = all_split,
      concatvis = field+'_all_split.ms')

# Examine some header information, e.g. #spws, #fields in the mosaic, etc.
# CHECK: Average Interval(s) for 7m and 12m array data 
#
  listobs(vis=field+'_all_split.ms',
      listfile=field+'_all_split.ms.listobs',
      overwrite = True)

# Concatenate the continuum-subtracted MSs.
  concat(vis = all_contsub,
      concatvis = field+'_all_split.ms.contsub')

# Examine some header information, e.g. #spws, #fields in the mosaic, etc.
  listobs(vis=field+'_all_split.ms.contsub',
      listfile=field+'_all_split.ms.contsub.listobs',
      overwrite = True)

###############
# step 3: Check the relative weights of 12m array and 7m array visibilities
###############

mystep = 3
if(mystep in thesteps(mysteps)):

  os.system('rm -rf *.weight.png')

  plotms(vis=field+'_all_split.ms.contsub',
      yaxis='wt',
      xaxis='uvdist',
      spw='0:2~2048,1:2~2048,2:2~2048',# plotting visibilities for a single channel, here assumes the value(2048) can be larger than the actual number of channels
      coloraxis='spw',
      plotfile=field+'_all_split.ms.contsub'+'.weight.png',
      showgui=True, overwrite=True)
#
# CHECK: the relative weights, the 7m should actually have weights &approx; 0.193 times lower than the 12m data: A(7m)*A(7m)/A(12m)*A(12m) * t(7m)/t(12m) = 7^4/12^4 * 6.05/10.1
# If it is not ~0.19, there is a way to correct the weights, pls search "relative weights casa" on google to find the solution
# As of Casa 4xxx, the relative weights should not be an issue because the pipleline has already solved it.


###############
# step 4: Check the velocity range to be used in the tclean and Prepare for some final parameter for clean
###############

mystep = 4
if(mystep in thesteps(mysteps)):
  plotms(vis=field+'_all_split.ms.contsub',xaxis='velocity',yaxis='amp',
      avgtime='1e8',avgscan=True,plotfile=field+'_all_split.ms.contsub.plotms.png', 
      showgui = True,overwrite=True)
  # After plotms, you need to determine the following parameters:
  # e.g., nchan=112;vstart='-40km/s';vwidth='0.4km/s'



###############
# step 5: Auto-mask tclean
###############

mystep = 5
if(mystep in thesteps(mysteps)):
  imaging_root = "imaging_results_test8"
  if not os.path.exists(imaging_root):
    os.mkdir(imaging_root)
  
  # buid up the intial parameters for the line imaging 
  impars = { 'niter':5000000,
             'threshold':'0.0mJy/beam',
             'usemask':'auto-multithresh',
             'growiterations':80,
             'sidelobethreshold':2.0,
             'noisethreshold':4.25,
             'lownoisethreshold':1.0,
             'minbeamfrac':3.0,
             'negativethreshold':10000.0,
             'parallel':False,
             'dogrowprune':True,
             'robust':0.5,
             'weighting': 'briggs',
             'scales': [0,5,10,15],
             'gridder': 'mosaic',
             'specmode': 'cube',
             'stokes':'I',
             'deconvolver': 'multiscale',
             'outframe':'LSRK',
             'veltype':'radio',
             'interactive':False,
             'pbcor':True,
             'restoration':True,
             'restoringbeam':'common',  # using common to fit the TP data reduced by the ALMA staff.
             'pblimit':0.2,
             'chanchunks':-1,
             'nterms':1,  
             }
             
  for molepar in molepars:
    mole=molepars[molepar]['mole']
        
    # calculate the channel width
    count_spws = len(au.spwsforfield(field+'_all_split.ms.contsub',field=field))
    width = np.max([np.abs(au.effectiveResolution(field+'_all_split.ms.contsub',spw='{0}'.format(i),kms=True)) for i in range(count_spws)])
    width = 0.2 #using the manual measurement instead of the above calculation because the latter is still somehow large.
    impars['width'] = '{0:.6f}km/s'.format(width)
    impars['restfreq'] = molepars[molepar]['restfreq']
    # calculate vstart
    vstart = u.Quantity( molepars[molepar]['vlsr'])-u.Quantity(molepars[molepar]['cubewidth'])/2
    impars['start'] = '{0:.1f}km/s'.format(vstart.value)
    # calculate the dimension
    dim = au.pickCellSize(field+'_all_split.ms.contsub',imsize=True)
    impars['imsize'] = dim[1]
    impars['cell'] = ['{0:.2f}arcsec'.format(dim[0])] 
    
    
    
    # creating the dirty image
    if not os.path.exists(os.path.join(imaging_root, field+'_'+band)+'_dirty_'+mole+'.residual'):
      print('making the dirty images')
      
      imagename = os.path.join(imaging_root, field+'_'+band)+'_dirty_'+mole
      os.system('rm -rf '+imagename+'*')
      
      impars_dirty = impars.copy()
      impars_dirty['niter'] = 0 
      impars_dirty['nchan'] = 6 # only use very small part of channels to quickly create the dirty images
     

      
      tclean(vis=field+'_all_split.ms.contsub', 
            field=field, 
            #spw=['21', '21', '21'], 
            datacolumn='data', 
            imagename=imagename, 
            phasecenter=phasecenter,          
            **impars_dirty   
            )
            
    # do the imaging cleaning 
    print('line imaging cleaning')
    imagename = os.path.join(imaging_root, field+'_'+band)+'_'+mole
    os.system('rm -rf '+imagename+'*')
    # calculate the number of channels
    impars['nchan'] = int((u.Quantity(molepars[molepar]['cubewidth'])/u.Quantity(impars['width'])).value)                 
    # calculate the threshold using the image residual
    im_stats = imstat(os.path.join(imaging_root,field+'_'+band)+'_dirty_'+mole+'.residual', chans="0~5")
    impars['threshold'] = '{0:.6f}Jy/beam'.format(2*im_stats['rms'][0]) 
    imhd = imhead(os.path.join(imaging_root,field+'_'+band)+'_dirty_'+mole+'.image')
    bmaj =  imhd['restoringbeam']['major']['value']
    bmin =  imhd['restoringbeam']['minor']['value']
    cell = np.sqrt(bmaj**2+bmin**2)/5.0
    imsize = max(int(dim[1][0]*dim[0]/cell),int(dim[1][1]*dim[0]/cell))
    imsize = 400 # using the manual measurement instead of the above calculation because the latter is still somehow large.
    impars['imsize'] = [imsize,imsize]
    impars['cell'] = ['{0:.2f}arcsec'.format(cell)]
         
         
          
    tclean(vis=field+'_all_split.ms.contsub', 
            field=field, 
            #spw=['21', '21', '21'], 
            datacolumn='data', 
            imagename=imagename, 
            phasecenter=phasecenter,          
            **impars   
            )


    ia.open(imagename+'.image')
    ia.sethistory(origin='almaimf_cont_selfcal',
                  history=["{0}: {1}".format(key, val) for key, val in
                  impars.items()])
    ia.close()    
    
    imhead(imagename+'.image.pbcor',mode='add',hdkey='history',hdvalue='reduced by Hong-Li Liu')
    imhead(imagename+'.image',mode='add',hdkey='history',hdvalue='reduced by Hong-Li Liu')
    exportfits(imagename=imagename+'.image.pbcor',
           fitsimage=imagename+'.image.pbcor.fits',
           overwrite=True)
    exportfits(imagename=imagename+'.image',
           fitsimage=imagename+'.image.fits',
           overwrite=True)
    exportfits(imagename=imagename+'.pb',
           fitsimage=imagename+'.pb.fits',
           overwrite=True)
           
          



