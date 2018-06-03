import pylab as pl

def fun(vis, spw, intent='CALIBRATE_BANDPASS#ON_SOURCE', caltable=None, avgchannel=1920,):

    mymsmd = msmdtool()
    mymsmd.open(vis)

    scans = mymsmd.scansforintent(intent).tolist()
    mymsmd.close()

    myms = mstool()
    myms.open(vis)
    myms.selectinit(datadescid=spw)
    myms.select({'scan_number': scans})
    myms.selectchannel(width=avgchannel)

    mydata = myms.getdata(['time', 'corrected_amplitude', 'axis_info',
                           'flag'], ifraxis=True)
    
    myms.close()

    myms = mstool()
    myms.open(vis)
    myms.selectinit(datadescid=spw+1)
    myms.select({'scan_number': scans})

    avgdata = myms.getdata(['time', 'amplitude', 'axis_info', 'flag'],
                           ifraxis=True)
    
    myms.close()

    # do not plot 0's
    avgdata['amplitude'][avgdata['amplitude'] == 0] = np.nan
    mydata['corrected_amplitude'][mydata['corrected_amplitude'] == 0] = np.nan
    mydata['corrected_amplitude'][mydata['flag']] = np.nan
    avgdata['amplitude'][avgdata['flag']] = np.nan

    #print("Any zeros?", np.any(mydata['corrected_amplitude'] == 0))
    #print("Any zeros (avg)?", np.any(avgdata['amplitude'] == 0))

    pl.clf()
    fig = pl.gcf()
    print("Plotting to figure {0}".format(fig.number))
    ax1 = pl.subplot(3,1,1)
    ax1.plot(avgdata['time'], avgdata['amplitude'].squeeze().T[:,:,0],
             linestyle='-', label='Corr1', alpha=0.5)
    ax1.plot(avgdata['time'], avgdata['amplitude'].squeeze().T[:,:,1],
             linestyle='-', label='Corr2', alpha=0.5)

    ax2 = pl.subplot(3,1,2)
    ax2.plot(mydata['time'], mydata['corrected_amplitude'].squeeze().T[:,:,0],
             linestyle='-', label='Corr1', alpha=0.5)
    ax2.plot(mydata['time'], mydata['corrected_amplitude'].squeeze().T[:,:,1],
             linestyle='-', label='Corr2', alpha=0.5)

    if caltable is not None:
        # do something to load caltable data and plot it here
        pass

    return mydata, avgdata
