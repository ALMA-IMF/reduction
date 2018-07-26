#You should run this with CASA 5.1.1


thesteps = [] 
step_title = {0: 'Image continuum of the target source only spw 29, 103 and 156',
              1: 'Continuum subtraction',
              2: 'Image representative spectral line  N2H+ v=0 J=1-0 ',
              3: 'Image spectral line CH3CN  ',
              4: 'Image spectral line CH3CCH',
              5: 'Image cube spectral window continuum 2',
              6: 'Export FITS files'}

try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

v0='93.17340200000001GHz' # line N2H+ v=0 J=1-0  rep.spw. 
v1='92.2GHz' # line CH3CN
v2='102.6GHz' # line CH3CCH
v3='105.0GHz' # spectral window continuum 2

thems= 'calibrated.ms'

# Image continuum of the target source only spw 29, 103 and 156 (line free spectral window)

mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf W43-MM2_sci.spw29_103_156.*')
  tclean(vis=thems,
        imagename='W43-MM2_sci.spw29_103_156.cont.I.manual',
        field="W43-MM2",
        spw=['29,103,156'],
        threshold="25 uJy",
        robust=0.5, 
        niter=100, 
        weighting='briggs',
        pbcor=True, # will create both pbcorrected and uncorrected images 
        imsize=[8960, 8960],
        cell="0.03arcsec",
        specmode='mfs', 
        deconvolver='hogbom',
        nterms=1,
        chanchunks=-1, 
        gridder='mosaic', 
        interactive=True,     
        uvtaper = ['0.3arcsec','0.3arcsec', '0.0deg'])

#RESULTS: beam= 0.44"x 0.36" at -79.3492 deg   RMS ~0.038 mJy 


# Continuum subtraction
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  uvcontsub(vis= 'calibrated.ms',
            field="W43-MM2",
            spw='25,27,29,31,99,101,103,105,152,154,156,158',
            fitorder=1,
            fitspw='25:0~850;1000~1919,27:0~340;360~1380;1460~1919,29,31:0~174;186~1080;1110~1919,99:0~850;1000~1919,101:0~340;360~1380;1460~1919,103,105:0~174;186~1080;1110~1919,152:0~850;1000~1919,154:0~340;360~1380;1460~1919,156,158:0~174;186~1080;1110~1919')

  listobs('calibrated.ms.contsub',listfile='calibrated.ms.contsub.listobs')


thems_contsub= 'calibrated.ms.contsub'

#With the continuum subtraction the SPWs are renumbered: 25,27,29,31,99,101,103,105,152,154,156,158 --> 0,1,2,3,4,5,6,7,8,9,10,11

# Image representative spectral line  N2H+ v=0 J=1-0
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf W43-MM2_sci.spw0_4_8.*')
  tclean(vis=thems_contsub,
        imagename='W43-MM2_sci.spw0_4_8.cube.I.manual_N2H',
        field="W43-MM2",
        spw=['0,4,8'],
        threshold='1.2mJy',
        interactive= True,
        niter=100,
        imsize=[8960,8960],
        cell="0.03arcsec",
        outframe='LSRK',
        restfreq=v0,
        weighting="briggs",
        robust = 0.5,
        deconvolver='hogbom', 
        pbcor=True, 
        specmode='cube', 
        restoringbeam='common',
        chanchunks=-1, 
        gridder='mosaic',
        width=6,
        uvtaper = ['0.2arcsec','0.2arcsec', '0.0deg'])

#RESULTS: beam = 0.41x0.33  arcsec, RMS = 1.2 mJy 

# Image spectral line  CH3CN
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf W43-MM2_sci.spw1_5_9.*')
  tclean(vis=thems_contsub,
        imagename='W43-MM2_sci.spw1_5_9.cube.I.manual_CH3CN',
        field="W43-MM2",
        spw=['1,5,9'],
        threshold='1.2mJy',
        interactive= True,
        niter=100,
        imsize=[8960,8960],
        cell="0.03arcsec",
        outframe='LSRK',
        restfreq=v1,
        weighting="briggs",
        robust = 0.5, 
        deconvolver='hogbom', 
        pbcor=True, 
        specmode='cube', 
        restoringbeam='common',
        chanchunks=-1, 
        gridder='mosaic',
        width=6,
        uvtaper = ['0.25arcsec','0.25arcsec', '0.0deg'])

#RESULTS: beam = 0.44x0.36  arcsec, RMS = 0.54 mJy

# Image spectral line CH3CCH
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf W43-MM2_sci.spw2_6_10.*')
  tclean(vis=thems_contsub,
        imagename='W43-MM2_sci.spw2_6_10.cube.I.manual_CH3CCH',
        field="W43-MM2",
        spw=['2,6,10'],
        threshold='1.2mJy',
        interactive= True,
        niter=100,
        imsize=[8960,8960],
        cell="0.03arcsec",
        outframe='LSRK',
        restfreq=v2,
        weighting="briggs",
        robust = 0.5, 
        deconvolver='hogbom', 
        pbcor=True, 
        specmode='cube', 
        restoringbeam='common',
        chanchunks=-1, 
        gridder='mosaic',
        width=6,
        uvtaper = ['0.25arcsec','0.25arcsec', '0.0deg'])
 

# Image spectral window continuum 2
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf W43-MM2_sci.spw3_7_11.*')
  tclean(vis=thems_contsub,
        imagename='W43-MM2_sci.spw3_7_11.cube.I.manual_cont2',
        field="W43-MM2",
        spw=['3,7,11'],
        threshold='1.2mJy',
        interactive= True,
        niter=100,
        imsize=[8960,8960],
        cell="0.03arcsec",
        outframe='LSRK',
        restfreq=v3,
        weighting="briggs",
        robust = 0.5, 
        deconvolver='hogbom', 
        pbcor=True, 
        specmode='cube', 
        restoringbeam='common',
        chanchunks=-1, 
        gridder='mosaic',
        width=6,
        uvtaper = ['0.25arcsec','0.25arcsec', '0.0deg'])


#Export FITS files
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  myimages = set([])
  myimages.add('W43-MM2_sci.spw29_103_156.cont.I.manual')
#  myimages.add('W43-MM2_sci.spw0_4_8.cube.I.manual_N2H')
#  myimages.add('W43-MM2_sci.spw1_5_9.cube.I.manual_CH3CN')
#  myimages.add('W43-MM2_sci.spw2_6_10.cube.I.manual_CH3CCH')
#  myimages.add('W43-MM2_sci.spw3_7_11.cube.I.manual_cont2')
  
  for myimagebase in myimages:
    exportfits(imagename=myimagebase+'.image.pbcor', fitsimage=myimagebase+'.image.pbcor.fits', overwrite=True) # export the corrected image
    exportfits(imagename=myimagebase+'.pb', fitsimage=myimagebase+'.flux.fits', overwrite=True) # export the PB image

