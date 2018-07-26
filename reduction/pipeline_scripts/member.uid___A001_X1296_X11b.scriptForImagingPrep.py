## Image preparation
doconcat=True

#List of files to concatenate:
vislist=['uid___A002_Xc7a409_X351d.ms.split.cal', 'uid___A002_Xc7cf4e_X52fc.ms.split.cal', 'uid___A002_Xc7e4e4_X3ac2.ms.split.cal']

#Concatenate EB:
if doconcat:
  concat(vis=vislist, concatvis='calibrated.ms')
  listobs(vis='calibrated.ms',listfile='calibrated.ms.listobs')
