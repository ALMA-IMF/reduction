import pylab as pl

def plot_bp_stuff(vis, spw, intent='CALIBRATE_BANDPASS#ON_SOURCE',
                  caltable=None, avgchannel=1920, ant=None):

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
    # selectchannel sets the averaging.  Testing with avgchannel > nchan
    # yielded bad results, so this part may require fine-tuning for, e.g., 7m
    # vs 12m data.  There should be a way to automate this, though.
    myms.selectchannel(width=avgchannel)

    # Actually get the data.  We need time for plotting, corrected_amplitude
    # since that's the 'buggy' column we're trying to understand, axis_info
    # for more selection (e.g., on antenna, see below), and 'flag' to remove
    # flagged data.
    mydata = myms.getdata(['time', 'corrected_amplitude', 'axis_info',
                           'flag'], ifraxis=True)
    
    myms.close()

    # We do the same thing on the next spw.
    # The SPWs with 1 channel that are adjacent to the science SPWs are the
    # channel-averaged versions.  They are sampled at a 6x (or maybe 3x?) higher
    # rate, but only give average amplitudes.  This can be useful to see if
    # there were rapid changes in amplitude (or, later, phase) that were
    # averaged out.  We probably want to plot the phases using these data at
    # some point.
    myms = mstool()
    myms.open(vis)
    myms.selectinit(datadescid=spw+1)
    myms.select({'scan_number': scans})

    avgdata = myms.getdata(['time', 'amplitude', 'axis_info', 'flag'],
                           ifraxis=True)
    
    myms.close()

    # These steps remove 0's, which may come from autocorrelations or flagged data
    avgdata['amplitude'][avgdata['amplitude'] == 0] = np.nan
    mydata['corrected_amplitude'][mydata['corrected_amplitude'] == 0] = np.nan
    mydata['corrected_amplitude'][mydata['flag']] = np.nan
    avgdata['amplitude'][avgdata['flag']] = np.nan

    # Select a single antenna if requested
    if ant is not None:
        ant = "{0:02d}".format(ant)
        antsel = np.char.find(data['axis_info']['ifr_axis']['ifr_shortname'], ant) != -1
    else:
        antsel = np.ones_like(data['axis_info']['ifr_axis']['ifr_shortname'], dtype='bool')

    # plotting commands below
    pl.clf()
    fig = pl.gcf()
    print("Plotting to figure {0}".format(fig.number))
    ax1 = pl.subplot(3,1,1)
    ax1.plot(avgdata['time'], avgdata['amplitude'].T[:,antsel,0,0],
             linestyle='-', label='Corr1', alpha=0.5)
    ax1.plot(avgdata['time'], avgdata['amplitude'].T[:,antsel,0,1],
             linestyle='-', label='Corr2', alpha=0.5)

    ax2 = pl.subplot(3,1,2)
    ax2.plot(mydata['time'], mydata['corrected_amplitude'].T[:,antsel,0,0],
             linestyle='-', label='Corr1', alpha=0.5)
    ax2.plot(mydata['time'], mydata['corrected_amplitude'].T[:,antsel,0,1],
             linestyle='-', label='Corr2', alpha=0.5)

    if caltable is not None:
        # do something to load caltable data and plot it here
        tb.open(caltable)
        time, spwid, gain, antennae = (tb.getcol('TIME'),
                                       tb.getcol('SPECTRAL_WINDOW_ID'),
                                       tb.getcol('CPARAM'),
                                       tb.getcol('ANTENNA1'))
        tb.close()

        # select on spw and optionally antenna
        match = spwid == spw
        if ant is not None:
            match &= antennae == int(ant)

        ax3 = pl.subplot(3,1,2)
        # gains are complex, so we plot the angle of the gains.  If this was
        # amplitude calibration, one would use np.abs(gains) instead.
        ax3.plot(time[match], np.angle(gains[:,0,match].T)*180/np.pi,
                 linestyle='-', alpha=0.5)

    return mydata, avgdata
