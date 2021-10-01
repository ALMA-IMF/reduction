import os, psutil, sys
import time

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
        print(f'Memory log file: {jobname}_{pid}_memlog.log')
        with open(f"{jobname}_{pid}_memlog.log", "a") as fh:
            fh.write(f"{jobname}\n")
            fh.write(f"{'TIME':10s} {'RSS':10s} {'VM':10s} {'SHARED':10s} {'DATA':10s}\n")

            while psutil.pid_exists(pid):
                process = psutil.Process(pid)
                meminfo = process.memory_info()

                t1 = time.time() - t0

                fh.write(f"{t1:10.1f} {meminfo.rss/gb:10.2f} {meminfo.vms/gb:10.2f} {meminfo.shared/gb:10.2f} {meminfo.data/gb:10.2f}\n")
                fh.flush()

                time.sleep(10)
