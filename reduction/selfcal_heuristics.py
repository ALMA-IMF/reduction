import numpy as np
try:
    from casatools import table
    tb = table()
except ImportError:
    from taskinit import tbtool
    tb = tbtool()

def goodenough_field_solutions(tablename, minsnr=5, maxphasenoise=np.pi/4.,
                               makeplot=False):
    """
    After an initial self-calibration run, determine which fields have good
    enough solutions.  This only inspects the *phase* component of the
    solutions.  Both polarizations are assessed together.

    Parameters
    ----------
    tablename : str
        The name of the calibration table (e.g., phase.cal)
    minsnr : float
        The minimum *average* signal to noise ratio for a given field
    maxphasenoise : float
        The maximum average phase noise permissible for a given field in
        radians
    makeplot : bool
        If set, plot the phase centers good / bad as blue circles, red squares

    Returns
    -------
    An array of field IDs.  This will need to be converted to a list of strings
    for use in CASA tasks.

    Examples
    --------
    >>> okfields,notokfields = goodenough_field_solutions('phase.cal', minsnr=3)
    >>> okfields_str = ",".join(["{0}".format(x) for x in okfields])
    >>> applycal(vis=selfcal_vis, field=okfields_str, gaintable=["phase.cal"],
    ...          interp="linear", applymode='calonly', calwt=False)
    """
    tb.open(tablename)
    solns = tb.getcol('CPARAM')
    fields = tb.getcol('FIELD_ID')
    snr = tb.getcol('SNR')
    if makeplot:
        ra, dec = tb.getcol('PHASE_DIR')
    tb.close()

    okfields=[]
    not_ok_fields = []

    ufields = np.unique(fields)

    for field in ufields:
        sel = fields==field
        angles = np.angle(solns[:,:,sel])
        field_ok = ((angles.std() < maxphasenoise) &
                    (snr[:,:,sel].mean() > minsnr))
        if field_ok:
            okfields.append(field)
        else:
            not_ok_fields.append(field)

    if makeplot:
        import pylab as pl
        pl.plot(ra[0][okfields]*180/np.pi,
                dec[0][okfields]*180/np.pi,
                color='b', marker='o', linestyle='none')
        pl.plot(ra[0][not_ok_fields]*180/np.pi,
                dec[0][not_ok_fields]*180/np.pi,
                color='r', marker='s', linestyle='none')


    return okfields, not_ok_fields

def flag_extreme_amplitudes(tablename, maxpctchange=50, pols=[0], channels=[0]):
    """
    Flag out all gain amplitudes with >``maxpctchange``% change (e.g., for the
    default 50%, flag everything outside the range 0.5 < G < 1.5).  This is a
    *very simple* cut, but it cannot be easily applied with existing tools
    since it is cutting on the value of the amplitude correction, not on any
    particular normal data selection type.  It is still highly advisable to
    plot the amp vs snr or similar diagnostics after running this to make sure
    you understand what's going on.  For example, after I ran this on a data
    set, I discovered that one antenna had high gain corrections even in the
    high SNR regime, which probably indicates a problem with that antenna.

    Parameters
    ----------
    maxpctchange : float
        The maximum percent change permitted in an amplitude
    pols : list
        The list of polarizations to include in the heuristics
    channels : list
        The list of channels to include in the heuristics

    Returns
    -------
    None
    """

    tb.open(tablename)
    solns = tb.getcol('CPARAM')
    snr = tb.getcol('SNR')
    # true flag = flagged out, bad data
    flags = tb.getcol('FLAG')
    tb.close()

    amp = np.abs(solns)
    maxfrac = maxpctchange / 100.

    bad = ((amp[pols, channels] > (1+maxfrac)) |
           (amp[pols, channels] < (1-maxfrac)))

    bad_snr = snr[pols, channels, :][bad]

    print("Found {0} bad amplitudes with mean snr={1}".format(bad.sum(), bad_snr.mean()))
    print("Total flags in tb.flag: {0}".format(flags.sum()))

    flags[pols, channels, :] = bad | flags[pols, channels, :]
    assert all(flags[pols, channels, :][bad]), "Failed to modify array"

    tb.open(tablename, nomodify=False)
    tb.putcol(columnname='FLAG', value=flags)
    tb.flush()
    tb.close()

    tb.open(tablename, nomodify=True)
    flags = tb.getcol('FLAG')
    print("Total flags in tb.flag after: {0}".format(flags.sum()))

    assert all(flags[pols, channels, :][bad]), "Failed to modify table"

    tb.close()
