def bp_amp_var(vis, spw, intent='CALIBRATE_BANDPASS#ON_SOURCE',
                  caltable=None, avgchannel=1920, ant=None):

  try:
    # Step 1: Use the metadata tool to get the intents for later
    # selection.  This allows us to select just the BP cal
    mymsmd = msmdtool()
    mymsmd.open(vis)
    scans = mymsmd.scansforintent(intent).tolist()
    mymsmd.close()

    # Step 2: Select and extract the data from the appropriate SPW
    myms = mstool()
    myms.open(vis)
    # SPW selection is done during selectinit (don't know why)
    myms.selectinit(datadescid=spw)
    # Scan selection is done using the metadata selection above
    myms.select({'scan_number': scans})
    # selectchannel sets the averaging.  Script fails is avgchannel > nchan.
    # Here we work on the uncorrected, but flagged amplitude.
    # Get channel numbers:
    avgchannel = myms.getspectralwindowinfo()[str(spw)].values()[7]
    myms.selectchannel(width=avgchannel)
    mydata = myms.getdata(['time', 'amplitude', 'axis_info',
                           'flag'], ifraxis=True)
    myms.close()
    mydata['amplitude'][mydata['amplitude'] == 0] = np.nan
    mydata['amplitude'][mydata['flag']] = np.nan
 
    import pylab as pl
    pl.clf()
    fig = pl.gcf()
    ax = pl.subplot(1,1,1)
    ax.plot(mydata['time'], mydata['amplitude'].T[:,:,0,1],
             linestyle='-', label='', alpha=0.5)

    # Get the average:
    a=mydata['amplitude'].T[:,:,0,1].flatten()
    amp_mean = np.nanmean(a)
    amp_std  = np.nanstd(a)
    threshold=2*amp_std
    amp_nonan = a[np.logical_not(np.isnan(a))]
    np.where(np.logical_and(amp_nonan>=amp_mean-threshold, amp_nonan<=amp_mean+threshold))
    np.size(amp_nonan)
    np.size(np.where(np.logical_or(amp_nonan<amp_mean-threshold, amp_nonan>amp_mean+threshold)))
    fraction=100*np.float(np.size(np.where(np.logical_or(amp_nonan<amp_mean-threshold, amp_nonan>amp_mean+threshold))))/np.float(np.size(amp_nonan))
    print ("Fraction of outliers: {0:2.4f} % of points outside the threshold.".format(fraction))
  except:
    print ("There is a problem.")

# Example how to use this function
print "SPW 16"
bp_amp_var(vis="uid___A002_Xc6c0d5_X3f2e.ms",spw=16)
bp_amp_var(vis="uid___A002_Xc6d2f9_X4380.ms",spw=16)
print "SPW 18"
bp_amp_var(vis="uid___A002_Xc6c0d5_X3f2e.ms",spw=18)
bp_amp_var(vis="uid___A002_Xc6d2f9_X4380.ms",spw=18)
print "SPW 20"
bp_amp_var(vis="uid___A002_Xc6c0d5_X3f2e.ms",spw=20)
bp_amp_var(vis="uid___A002_Xc6d2f9_X4380.ms",spw=20)
print "SPW 22"
bp_amp_var(vis="uid___A002_Xc6c0d5_X3f2e.ms",spw=22)
bp_amp_var(vis="uid___A002_Xc6d2f9_X4380.ms",spw=22)
