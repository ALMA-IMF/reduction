'''
Script that runs a tclean identical to the ALMA-IMF pipeline, to test self-cal results. 
'''

import os

###### User defined #####
spw_vis = ['uid___A002_Xcc626d_X9fda_G010.62_B3_spw1.split', 'uid___A002_Xc86fe5_X7a9e_G010.62_B3_spw1.split', 'uid___A002_Xc89480_X57ef_G010.62_B3_spw1.split'] #['uid___A002_Xcd07af_X41d5_G333.60_B3_spw1.split.sc2','uid___A002_Xc8ed16_X5c3d_G333.60_B3_spw1.split.sc2']
concat_vis = 'G010.62_B3_spw1_12M.concat.ms.nosc' #'G333.60_B3_spw1_12M.concat.ms.sc-test2' #'G333.60_B3_spw1_12M.concat.ms'
imagename = 'G010.62_B3_spw1_12M_h41a_nosc' 
startmodel = 'G010.62_B3_spw1_12M_h41a.contcube.model'
field = ['G010.62']
nchan = 65
start = '-60.0km/s'
width = '1.84km/s'
restfreq = '92.034434GHz'
imsize = [1890, 1890]
cell = ['0.11arcsec', '0.11arcsec']
phasecenter="ICRS 272.620166667deg -19.9300832267deg"
niter_tclean2 = 5000000

########################

os.system("rm -rf "+concat_vis)

concat(vis=spw_vis,concatvis=concat_vis,freqtol="",dirtol="",respectname=False,timesort=False,copypointing=True,visweightscale=[],forcesingleephemfield="")

flagdata(vis=concat_vis,mode="summary",autocorr=False,inpfile="",reason="any",tbuff=0.0,spw="",field="",antenna="",uvrange="0~1m",timerange="",correlation="",scan="",intent="",array="",observation="",feed="",clipminmax=[],datacolumn="DATA",clipoutside=True,channelavg=False,chanbin=1,timeavg=False,timebin="0s",clipzeros=False,quackinterval=1.0,quackmode="beg",quackincrement=False,tolerance=0.0,addantenna="",lowerlimit=0.0,upperlimit=90.0,ntime="scan",combinescans=False,timecutoff=4.0,freqcutoff=3.0,timefit="line",freqfit="poly",maxnpieces=7,flagdimension="freqtime",usewindowstats="none",halfwin=1,extendflags=True,winsize=3,timedev="",freqdev="",timedevscale=5.0,freqdevscale=5.0,spectralmax=1000000.0,spectralmin=0.0,antint_ref_antenna="",minchanfrac=0.6,verbose=False,extendpols=True,growtime=50.0,growfreq=50.0,growaround=False,flagneartime=False,flagnearfreq=False,minrel=0.0,maxrel=1.0,minabs=0,maxabs=-1,spwchan=False,spwcorr=False,basecnt=False,fieldcnt=False,name="Summary",action="apply",display="",flagbackup=True,savepars=False,cmdreason="",outfile="",overwrite=True,writeflags=True)

os.system("rm -rf "+imagename+".*")

tclean(vis=concat_vis,selectdata=True,field=field,spw="",timerange="",uvrange="",antenna="",scan="",observation="",intent="",datacolumn="corrected",imagename=imagename,imsize=imsize,cell=cell,phasecenter=phasecenter,stokes="I",projection="SIN",startmodel="",specmode="cube",reffreq="",nchan=nchan,start=start,width=width,outframe="LSRK",veltype="radio",restfreq=restfreq,interpolation="linear",perchanweightdensity=False,gridder="mosaic",facets=1,psfphasecenter="",chanchunks=1,wprojplanes=1,vptable="",mosweight=True,aterm=True,psterm=False,wbawp=True,conjbeams=False,cfcache="",usepointing=False,computepastep=360.0,rotatepastep=360.0,pointingoffsetsigdev=[],pblimit=0.05,normtype="flatnoise",deconvolver="hogbom",scales=[],nterms=2,smallscalebias=0.0,restoration=True,restoringbeam="",pbcor=False,outlierfile="",weighting="briggs",robust=0,noise="1.0Jy",npixels=0,uvtaper=[],niter=0,gain=0.1,threshold="5mJy",nsigma=0.0,cycleniter=-1,cyclefactor=1.0,minpsffraction=0.05,maxpsffraction=0.8,interactive=False,usemask="pb",mask="",pbmask=0.1,sidelobethreshold=3.0,noisethreshold=5.0,lownoisethreshold=1.5,negativethreshold=0.0,smoothfactor=1.0,minbeamfrac=0.3,cutthreshold=0.01,growiterations=75,dogrowprune=True,minpercentchange=-1.0,verbose=False,fastnoise=True,restart=True,savemodel="none",calcres=True,calcpsf=True,parallel=False)


os.system("rm -rf "+imagename+".model")


tclean(vis=concat_vis,selectdata=True,field=field,spw="",timerange="",uvrange="",antenna="",scan="",observation="",intent="",datacolumn="corrected",imagename=imagename,imsize=imsize,cell=cell,phasecenter=phasecenter,stokes="I",projection="SIN",startmodel=startmodel,specmode="cube",reffreq="",nchan=nchan,start=start,width=width,outframe="LSRK",veltype="radio",restfreq=restfreq,interpolation="linear",perchanweightdensity=False,gridder="mosaic",facets=1,psfphasecenter="",chanchunks=1,wprojplanes=1,vptable="",mosweight=True,aterm=True,psterm=False,wbawp=True,conjbeams=False,cfcache="",usepointing=False,computepastep=360.0,rotatepastep=360.0,pointingoffsetsigdev=[],pblimit=0.05,normtype="flatnoise",deconvolver="hogbom",scales=[],nterms=2,smallscalebias=0.0,restoration=True,restoringbeam="",pbcor=False,outlierfile="",weighting="briggs",robust=0,noise="1.0Jy",npixels=0,uvtaper=[],niter=niter_tclean2,gain=0.1,threshold="5mJy",nsigma=0.0,cycleniter=-1,cyclefactor=1.0,minpsffraction=0.05,maxpsffraction=0.8,interactive=False,usemask="pb",mask="",pbmask=0.1,sidelobethreshold=3.0,noisethreshold=5.0,lownoisethreshold=1.5,negativethreshold=0.0,smoothfactor=1.0,minbeamfrac=0.3,cutthreshold=0.01,growiterations=75,dogrowprune=True,minpercentchange=-1.0,verbose=False,fastnoise=True,restart=True,savemodel="none",calcres=False,calcpsf=True,parallel=False)
