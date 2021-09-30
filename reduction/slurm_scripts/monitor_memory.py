import os, psutil, sys

if __name__ == "__main__":
    pid = sys.argv[1]
    print(pid)
    gb = 1024**3

    t0 = time.time()

    if os.getenv('jobname'):
        jobname = os.getenv('jobname')
    elif os.getenv('LOGFILENAME'):
        jobname = os.path.basename(os.getenv("LOGFILENAME"))
    else:
        jobname = 'unknown'

    if psutil.pid_exists(pid):
        with open(f"{jobname}_{pid}_memlog.log", "a") as fh:
            fh.write(f"{jobname}\n")
            fh.write(f"{'TIME':10s} {'RSS':10s} {'VM':10s} {'SHARED':10s} {'DATA':10s}\n")

            while psutil.pid_exists(pid):
                process = psutil.Process(pid)
                meminfo = process.memory_info()

                t1 = time.time() - t0

                fh.write(f"{t1:10d} {meminfo.rss/gb:10f} {meminfo.vms/gb:10f} {meminfo.shared/gb:10f} {meminfo.data/gb:10f}\n")
                fh.flush()

                time.sleep(10)
