#############################
#
# Template script to extract, concatenate, regrid, and clean the N2H+ visibility data of G328
#
#############################
#
# INITIAL DATASETS:
#
# 7m array: 2 MOUS
#     uid___A002_Xc6c0d5_X3f2e.ms
#     uid___A002_Xc6d2f9_X4380.ms
#
# 12m array, compact (C43-2): 1 MOUS
#     uid___A002_Xcf3a9c_X17b3.ms
#
# 12m array, extended (C43-5): 1 MOUS
#     uid___A002_Xc8ed16_Xd8b0_pipeline_original.ms
#
#############################
#
# TASKS USED:
#
# 1. listobs: MS header
# 2. uvcontsub: continuum subtraction
# 3. concat: merges the two 7m-array datasets into one
# 4. mstransform: regrids and splits out visibility data
# 5. tclean: generate an image cube from the visibilities
#
#############################

thesteps=[]
step_title = {0: 'Plot mosaic pointings and split out source and N2H+ spw',
              1: 'Continuum subtraction',
              2: 'Concatenate 7m + 12m array datasets',
              3: 'Check the relative weights of 12m array and 7m array visibilities',
              4: 'Regrid the N2H+(1-0) visibility data',
              5: 'CLEAN 12m+7m cube'
}
 
# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('g328-cube.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps
#
#
#
#
###############
# step 0: Plot mosaic pointings and split out source and N2H+ spw
###############

mystep = 0 
if(mystep in thesteps):

  os.system('rm -rf g328_n2h_7m-1.ms')
  os.system('rm -rf g328_n2h_7m-2.ms')
  os.system('rm -rf g328_n2h_12m-com.ms')
  os.system('rm -rf g328_n2h_12m-ext.ms')
  os.system('rm -rf g328_7m_mosaic.png')
  os.system('rm -rf g328_12m_com_mosaic.png')
  os.system('rm -rf g328_12m_mosaic_ext.png')

# Examine mosaic pointing maps (needs installing analysis utilities)
  au.plotmosaic('uid___A002_Xc6c0d5_X3f2e.ms',sourceid='2',figfile='g328_7m_mosaic.png')
  au.plotmosaic('uid___A002_Xcf3a9c_X17b3.ms',sourceid='2',figfile='g328_12m_com_mosaic.png')
  au.plotmosaic('uid___A002_Xc8ed16_Xd8b0_pipeline_original.ms',sourceid='2',figfile='g328_12m_ext_mosaic.png')

# Split out the source and N2H+ spw for each dataset
  split(vis = 'uid___A002_Xc6c0d5_X3f2e.ms',
      outputvis = 'g328_n2h_7m-1.ms',
      field = '3~5',
      spw = '16',
      datacolumn = 'corrected',
      keepflags = False)

  split(vis = 'uid___A002_Xc6d2f9_X4380.ms',
      outputvis = 'g328_n2h_7m-2.ms',
      field = '3~5',
      spw = '16',
      datacolumn = 'corrected',
      keepflags = False)

  split(vis = 'uid___A002_Xcf3a9c_X17b3.ms',
      outputvis = 'g328_n2h_12m-com.ms',
      field = '3~12',
      spw = '25',
      datacolumn = 'corrected',
      keepflags = False)

  split(vis = 'uid___A002_Xc8ed16_Xd8b0_pipeline_original.ms',
      outputvis = 'g328_n2h_12m-ext.ms',
      field = '3~12',
      spw = '25',
      datacolumn = 'corrected',
      keepflags = False)

###############
# step 1: Continuum subtraction
###############

mystep = 1
if(mystep in thesteps):

  os.system('rm -rf g328_n2h_7m-1.ms.contsub')
  os.system('rm -rf g328_n2h_7m-2.ms.contsub')
  os.system('rm -rf g328_n2h_12m-com.ms.contsub')
  os.system('rm -rf g328_n2h_12m-ext.ms.contsub')

  uvcontsub(vis = 'g328_n2h_7m-1.ms',
      field = '',
      fitspw = '0:20~889;1151~2028',
      excludechans = False,
      fitorder = 0)

  uvcontsub(vis = 'g328_n2h_7m-2.ms',
      field = '',
      fitspw = '0:20~889;1151~2028',
      excludechans = False,
      fitorder = 0)

  uvcontsub(vis = 'g328_n2h_12m-com.ms',
      field = '',
      fitspw = '0:20~819;1089~1900',
      excludechans = False,
      fitorder = 0)

  uvcontsub(vis = 'g328_n2h_12m-ext.ms',
      field = '',
      fitspw = '0:20~819;1089~1900',
      excludechans = False,
      fitorder = 0)



###############
# step 2: Concatenate 7m + 12m array datasets
###############

mystep = 2
if(mystep in thesteps):

  os.system('rm -rf g328_n2h_all_ori.ms')
  os.system('rm -rf g328_n2h_all_ori.ms.contsub')

# Concatenate
  concat(vis = ['g328_n2h_7m-1.ms','g328_n2h_7m-2.ms','g328_n2h_12m-com.ms','g328_n2h_12m-ext.ms'],
      concatvis = 'g328_n2h_all_ori.ms')

# Examine some header information, e.g. #spws, #fields in the mosaic, etc.
# CHECK: Average Interval(s) for 7m and 12m array data --> write it down for later (step 2)
#
  listobs(vis='g328_n2h_all_ori.ms',
      listfile='g328_n2h_all_ori.listobs',
      overwrite = True)

# Concatenate the continuum-subtracted MSs.
  concat(vis = ['g328_n2h_7m-1.ms.contsub','g328_n2h_7m-2.ms.contsub','g328_n2h_12m-com.ms.contsub','g328_n2h_12m-ext.ms.contsub'],
      concatvis = 'g328_n2h_all_ori.ms.contsub')



###############
# step 3: Check the relative weights of 12m array and 7m array visibilities
###############

mystep = 3
if(mystep in thesteps):

  os.system('rm -rf g328_weight.png')

  plotms(vis='g328_n2h_all_ori.ms.contsub',
      yaxis='wt',
      xaxis='uvdist',
      spw='0:200,1:200,2:200,3:200',# plotting visibilities for a single channel
      coloraxis='spw',
      plotfile='g328_weight.png')
#
# CHECK: the relative weights, 7m/12m should be ~0.19: A(7m)*A(7m)/A(12m)*A(12m) * t(7m)/t(12m) = 7^4/12^4 * 6.05/10.1
#

###############
# step 4: Regrid the N2H+(1-0) visibility data
###############


mystep = 4
if(mystep in thesteps):

  os.system('rm -rf g328_n2h_all.ms')
  os.system('rm -rf g328_n2h_all.ms.contsub')

# Regridding visibility cube for N2H+(1-0)
  mstransform(vis = 'g328_n2h_all_ori.ms',
      outputvis = 'g328_n2h_all.ms',
      field = '',
      spw = '',
      combinespws = False,
      datacolumn = 'data',
      regridms = True,
      mode = 'frequency',
      nchan = 80,
      start = '93.180757GHz',#freq_lsr [Vlsr=-43km/s]
      width = '0.2MHz',
      restfreq = '93.1763402',
      outframe = 'LSRK',
      keepflags = False)

# Examine some header information, e.g. #spws, #fields in the mosaic, etc.
  listobs(vis='g328_n2h_all.ms.contsub',
      listfile='g328_n2h_all_contsub.listobs',
      overwrite = True)


###############
# step 5: Generate a dirty/shallow clean image to select line-free channels
###############

mystep = 5
if(mystep in thesteps):

  os.system('rm -rf g328_n2h_all_clean.*')
  os.system('rm -rf g328_n2h_all_clean2.*')

# beam = 0.97" x 0.87"
# This is just one example of shallow clean for an 80-channel cube containing N2H+(J=1-0) (~20min)
# Please build different versions to test threshold, niter, masks, multiscale, etc.

  tclean(vis = 'g328_n2h_all.ms',
      imagename = 'g328_n2h_all_clean2',
      field = '',
      spw = '',
      imsize = [2048,2048],
      cell = ['0.2arcsec'],
      outframe = 'LSRK',
      gridder = 'mosaic',
      datacolumn = 'data',
      deconvolver = 'multiscale',
      scales = [0,4,16],
      weighting = 'briggs',
      specmode = 'cube',
      pbcor = False,
      interactive = False,
      niter = 1000000,
      threshold = '0.010Jy',
      phasecenter = 'ICRS 15:57:59.6807 -053.58.00.200',# taken from field '2' in the original MS data
      robust = 0.5,
      usemask = 'pb',
      pbmask = 0.2,
      pblimit = 0.2)


  tclean(vis = 'g328_n2h_all.ms',
      imagename = 'g328_n2h_all_clean',
      field = '',
      spw = '',
      imsize = [2048,2048],
      cell = ['0.1arcsec'],
      outframe = 'LSRK',
      gridder = 'mosaic',
      datacolumn = 'data',
      deconvolver = 'multiscale',
      scales = [0,4,16],
      weighting = 'briggs',
      specmode = 'cube',
      pbcor = False,
      interactive = False,
      niter = 1000000,
      threshold = '0.010Jy',
      phasecenter = 'ICRS 15:57:59.6807 -053.58.00.200',# taken from field '2' in the original MS data
      robust = 0.5,
      usemask = 'pb',
      pbmask = 0.2,
      pblimit = 0.2)


# Visualise the image cube and spectrum, and determine the line-free channels
#  viewer(infile = 'g328_n2h_all_clean.image')

            
