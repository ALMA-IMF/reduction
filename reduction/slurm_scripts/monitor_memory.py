import os, psutil, sys
import time

virtmem_fields = ['active', 'available', 'buffers', 'cached', 'free',
                  'inactive', 'percent', 'shared', 'slab', 'total',
                  'used']
swapmem_fields = ['free', 'percent', 'sin', 'sout', 'total',
                  'used']

if __name__ == "__main__":
    pid = int(sys.argv[1])
    print(f"PID being memory monitored: {pid}")
    gb = 1024**3

    if len(sys.argv) > 2:
        savedir = sys.argv[2]
    else:
        savedir = '/blue/adamginsburg/adamginsburg/slurmjobs'

    t0 = time.time()

    if os.getenv('jobname'):
        jobname = os.getenv('jobname')
    elif os.getenv('LOGFILENAME'):
        jobname = os.path.basename(os.getenv("LOGFILENAME"))
    else:
        jobname = 'unknown'
    print(f"Jobname: {jobname}")

    if psutil.pid_exists(pid):
        logfn = f"{savedir}/{jobname}_{pid}_memlog.log"
        print(f'Memory log file: {logfn}')
        with open(logfn, "a") as fh:
            fh.write(f"# {jobname}\n")
            header = ' '.join([f"{x:10s}" for x in virtmem_fields])
            fh.write(f"{'TIME':10s} {'RSS':10s} {'VM':10s} {'SHARED':10s} {'DATA':10s} {header}\n")

            while psutil.pid_exists(pid):
                process = psutil.Process(pid)
                meminfo = process.memory_info()
                vmem = psutil.virtual_memory()

                t1 = time.time() - t0

                vals = ' '.join([f"{getattr(vmem, x)/gb:10.2f}" for x in virtmem_fields])
                fh.write(f"{t1:10.1f} {meminfo.rss/gb:10.2f} {meminfo.vms/gb:10.2f} {meminfo.shared/gb:10.2f} {meminfo.data/gb:10.2f} {vals}\n")
                fh.flush()

                time.sleep(10)



    from astropy.table import Table

    tbl = Table.read(logfn, format='ascii.csv', header_start=1, delimiter=' ')

    import matplotlib
    matplotlib.use('agg')
    import pylab as pl

    pl.clf()
    pl.plot(tbl['TIME'], tbl['RSS'], label='rss', linewidth=2)
    pl.plot(tbl['TIME'], tbl['cached'], label='cached')
    pl.plot(tbl['TIME'], tbl['shared'], label='shared')
    #pl.plot(tbl['TIME'], tbl['free'], label='free')
    pl.plot(tbl['TIME'], tbl['used'], label='used')
    pl.plot(tbl['TIME'], tbl['active'], label='active')
    pl.plot(tbl['TIME'], tbl['inactive'], label='inactive')
    pl.xlabel('Time [s]')
    pl.ylabel('Memory [GB]')
    pl.legend(loc='best')

    pl.savefig(f"{savedir}/{jobname}_{pid}_memlog.png", bbox_inches='tight')
