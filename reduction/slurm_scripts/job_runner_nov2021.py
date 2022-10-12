import numpy as np
import glob
import shutil
import copy

allfields = "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split()
spws = {'B3': [f'spw{s}' for s in range(4)] + ['n2hp'],
        'B6': [f'spw{s}' for s in range(8)] + ['sio']}

# baseband, spw: name
line_maps = {'n2hp': {'band': 3, 'spw': 0},
             'h41a': {'band': 3, 'spw': 1},
             'sio': {'band': 6, 'spw': 1},
             'c18o': {'band': 6, 'spw': 4},
             '12co': {'band': 6, 'spw': 5},
             }

parameters = {'W51-E': {'12M':
  {'B6': {'spw5': {'mem': 128, 'ntasks': 16, 'mpi': True, 'concat': False, } },
   'B3': {'spw2': {'mem': 256, 'ntasks': 64, 'mpi': True, 'concat': True, } },
   'B3': {'spw0': {'mem': 256, 'ntasks': 16, 'mpi': True, 'concat': True, } }
 }},
 'W43-MM3': {'12M':
  {'B3':
   {'spw0': {'mem': 256, 'ntasks': 32, 'mpi': True, 'concat': True, },
    'spw1': {'mem': 128, 'ntasks': 16, 'mpi': True, 'concat': True, } }
  },
 },
 'W43-MM1': {'12M':
  {'B3':
   {'spw1': {'mem': 256, 'ntasks': 32, 'mpi': True, 'concat': True, } },
   'B6':
   {'sio':  {'mem': 128, 'ntasks': 32, 'mpi': True, 'concat': True, } ,
    'spw0': {'mem': 256, 'ntasks': 32, 'mpi': True, 'concat': True, } },
  },
 },
# 'G327.29':
# {'12M':
#     {'B6':
#         {'spw0': {'do_contsub': True},
#          'spw1': {'do_contsub': True},
#          'spw2': {'do_contsub': True},
#          'spw3': {'do_contsub': True},
#          'spw4': {'do_contsub': True},
#          'spw5': {'do_contsub': True},
#          'spw6': {'do_contsub': True},
#          'spw7': {'do_contsub': True}},
#         }
#     },
 'W43-MM2': {'12M':
  {
   'B6':
   {'sio':  {'mem': 128, 'ntasks': 16, 'mpi': False, 'concat': True, } },
  },
 },
  'G333.60': {'7M12M':
              {'B6': {'spw5': {'mem': 128, 'ntasks': 16, 'mpi': True, 'concat': True},
                     },
              },
              '12M':
                 {"B3":
                     {"spw3": {"mem": 128, "ntasks": 32, "mpi": True, "concat": True},
                     },
                  "B6":
                     {"spw1": {"mem": 256, "ntasks": 32, "mpi": False, "concat": True,},
                      "spw0": {"mem": 256, "ntasks": 8, "mpi": False, "concat": True,}
                     },
                 },
             },
}

newpars = {}
for field, fpars in parameters.items():
    for array, arrpars in fpars.items():
        for band, bandpars in arrpars.items():
            for spw, spwpars in bandpars.items():
                newpars[f'{field}_{array}_{band}_{spw}'] = spwpars

# add the 7m12m merge for n2hp,sio,h41a only
newpars.update({f'{field}_{array}_{band}_{spw}':
                      {'mem': 256, 'ntasks': 32, 'mpi': True, 'concat':True}
    for field in allfields
    for array in ("12M", "7M12M",)# "7M")
    for band, spw in (('B3', 'h41a'), ('B3', 'n2hp'), ('B6', 'sio'), )#('B6', 'spw5'), ('B3', 'spw1'))
})


del band
del field
del spw
del array

default_parameters = {f'{field}_{array}_{band}_{spw}':
                      {'mem': 256, 'ntasks': 32, 'mpi': True, 'concat':True}
    for field in allfields
    for array in ("12M", )
    for band in ("B3", "B6")
    for spw in spws[band]
                     }

assert 'G008.67_12M_B6_n2hp' not in default_parameters

for key in newpars:
    default_parameters[key] = newpars[key]

parameters = default_parameters

for field in ('G333.60', 'G008.67', 'G328.25', 'G010.62', 'W43-MM1'):
    parameters[f'{field}_7M12M_B3_h41a']['mem'] = 128
for field in ('G333.60', 'G008.67', 'G328.25', 'G010.62', 'W43-MM1'):
    parameters[f'{field}_7M12M_B3_n2hp']['mem'] = 128

parameters['W51-IRS2_7M12M_B3_n2hp']['mem'] = 256
parameters['G333.60_7M12M_B3_h41a']['mem'] = 256
parameters['G333.60_12M_B3_spw3']['mem'] = 256

# G327 experiments
parameters['G327.29_7M12M_B6_spw0'] = copy.copy(parameters['G327.29_12M_B6_spw0'])
parameters['G327.29_7M12M_B6_spw0']['array'] = '7M12M'
# we're not doing 7m fullcubes parameters['G327.29_7M_B6_spw0'] = copy.copy(parameters['G327.29_12M_B6_spw0'])
# we're not doing 7m fullcubes parameters['G327.29_7M_B6_spw0']['array'] = '7M'

# G327: do the continuum subtraction for an experiment
#for spwii in range(8):
#    parameters[f'G327.29_12M_B6_spw{spwii}']['do_contsub'] = True

assert 'G008.67_12M_B6_n2hp' not in parameters
assert 'W43-MM1_12M_B3_spw1' in parameters

# something's really broken about the ms here
if 'W43-MM1_7M12M_B6_sio' in parameters:
    del parameters['W43-MM1_7M12M_B6_sio']


if __name__ == "__main__":
    import subprocess
    import datetime
    import os
    import json
    from astropy.io import ascii
    import sys

    verbose = '--verbose' in sys.argv

    with open('/orange/adamginsburg/web/secure/ALMA-IMF/tables/line_completeness_grid.json', 'r') as fh:
        imaging_status = json.load(fh)

    sacct = subprocess.check_output(['sacct',
                                   '--format=JobID,JobName%45,Account%15,QOS%17,State,Priority%8,ReqMem%8,CPUTime%15,Elapsed%15,Timelimit%15,NodeList%20'])
    tbl = ascii.read(sacct.decode().split("\n"))

    scriptpath = '/orange/adamginsburg/ALMA_IMF/reduction/reduction/slurm_scripts/'

    qos = os.getenv('QOS')
    if qos:
        account = os.environ['ACCOUNT'] = 'adamginsburg' if 'adamginsburg' in qos else 'astronomy-dept'
        if 'astronomy-dept' not in qos and 'adamginsburg' not in qos:
            raise ValueError(f"Invalid QOS {qos}")
    else:
        account = 'astronomy-dept'
        qos = 'astronomy-dept-b'
    logpath = os.environ['LOGPATH']='/blue/adamginsburg/adamginsburg/slurmjobs/'


    for row,spwpars in parameters.items():
        field, array, band, spw = row.split("_")

        do_contsub = bool(spwpars.get('do_contsub'))
        contsub_suffix = '.contsub' if do_contsub else ''

        #print(f'row={row}')
        imstatus = imaging_status[field][band][spw][array+contsub_suffix]
        if imstatus['image'] and imstatus['pbcor']:
            #print(f"field {field} {band} {spw} {array} is done: imstatus={imstatus}")
            continue
        elif imstatus['WIP']:
            if '--redo-wip' in sys.argv:
                print(f"field {field} {band} {spw} {array} is in progress: imstatus={imstatus['WIP']}; trying anyway (if it is not in the 'PENDING' or 'RUNNING' queue)")
            else:
                continue
        else:
            if verbose:
                print(f"field {field} {band} {spw} {array} has not begun: imstatus={imstatus}")

        if verbose:
            print(f"spw={spw}, spwpars={spwpars}")
        if 'spw' in spw:
            fullcube = 'fullcube'
            suffix = '_' + spw.lstrip('spw')
        else:
            fullcube = spw
            suffix = ''


        workdir = os.getenv('WORK_DIRECTORY') or '/blue/adamginsburg/adamginsburg/almaimf/workdir'
        jobname = f"{field}_{band}_{fullcube}_{array}{suffix}{contsub_suffix}"

        match = tbl['JobName'] == jobname
        if any(match):
            states = np.unique(tbl['State'][match])
            if 'RUNNING' in states:
                jobid = tbl['JobID'][match & (tbl['State'] == 'RUNNING')]
                continue
                print(f"Skipped job {jobname} because it's RUNNING as {set(jobid)}")
            elif 'PENDING' in states:
                jobid = tbl['JobID'][match & (tbl['State'] == 'PENDING')]
                print(f"Skipped job {jobname} because it's PENDING as {set(jobid)}")
                continue
            elif 'COMPLETED' in states:
                jobid = tbl['JobID'][match & (tbl['State'] == 'COMPLETED')]
                if '--redo-completed' in sys.argv:
                    print(f"Redoing job {jobname} even though it's COMPLETED as {set(jobid)} (if it is not pending)")
                else:
                    print(f"Skipped job {jobname} because it's COMPLETED as {set(jobid)}")
                    continue
            elif 'FAILED' in states:
                jobid = tbl['JobID'][match & (tbl['State'] == 'FAILED')]
                if '--redo-failed' in sys.argv:
                    print(f"Redoing job {jobname} even though it's FAILED as {set(jobid)}")
                else:
                    print(f"Skipped job {jobname} because it's FAILED as {set(jobid)}")
                    continue
            elif 'TIMEOUT' in states:
                jobid = tbl['JobID'][match & (tbl['State'] == 'TIMEOUT')]
                print(f"Restarting job {jobname} because it TIMED OUT as {set(jobid)}")


        # handle specific parameters
        mem = int(spwpars["mem"])
        os.environ['MEM'] = mem = f'{mem}gb'
        ntasks = spwpars["ntasks"]
        os.environ['NTASKS'] = str(ntasks)
        os.environ['DO_CONTSUB'] = str(do_contsub)
        os.environ['SLURM_NTASKS'] = str(ntasks)
        os.environ['DO_NOT_CONCAT'] = str(not spwpars["concat"])
        os.environ['EXCLUDE_7M'] = str('7M' not in array)
        os.environ['ONLY_7M'] = str(array == '7M')
        os.environ['WORK_DIRECTORY'] = workdir
        os.environ['BAND_TO_IMAGE'] = band
        os.environ['BAND_NUMBERS'] = band[1]
        if spw in line_maps:
            spwn = line_maps[spw]['spw']
            os.environ['SPW_TO_IMAGE'] = str(spwn)
        else:
            spwn = int(spw[-1]) # check that is int
            os.environ['SPW_TO_IMAGE'] = str(spwn)
        os.environ['LINE_NAME'] = spw
        os.environ['FIELD_ID'] = field


        exclusive = ' --exclusive' if spwpars.get('EXCLUSIVE') else ''
        partition = f" --partition={spwpars.get('partition')}" if spwpars.get('partition') else ''

        basename = f'{field}_{band}_spw{spwn}_{array}_{spw}{contsub_suffix}'
        # basename = "{0}_{1}_spw{2}_{3}".format(field, band, spw, arrayname)

        # it is safe to remove things beyond here because at this point we're committed
        # to re-running
        if '--dry-run' not in sys.argv:
            if '--remove-failed' in sys.argv:
                #print(f"Removing files matching '{workdir}/{basename}.*'")
                failed_files = glob.glob(f'{workdir}/{basename}.*')
                if any('.image' in x for x in failed_files):
                    print(f"Found a .image in the failed file list: {failed_files}.  Continuing.")
                    #raise ValueError(f"Found a .image in the failed file list: {failed_files}")
                else:
                    for ff in failed_files:
                        print(f"Removing {ff}")
                        shutil.rmtree(ff)
            
            tempdir_name = f'{field}_{spw}_{array}_{band}{contsub_suffix}'
            print(f"Removing files matching '{workdir}/{tempdir_name}/IMAGING_WEIGHT.*'")
            old_tempfiles = (glob.glob(f'{workdir}/{tempdir_name}/IMAGING_WEIGHT*') +
                             glob.glob(f'{workdir}/{tempdir_name}/TempLattice*'))
            for tfn in old_tempfiles:
                print(f"Removing {tfn}")
                shutil.rmtree(tfn)

        if spwpars['mpi']:
            mpisuffix = '_mpi'
            cpus_per_task = 1
            os.environ['SLURM_TASKS_PER_NODE'] = str(ntasks)
        else:
            #assert ntasks == 1
            mpisuffix = ''
            cpus_per_task = ntasks
            ntasks = 1

        os.environ['CPUS_PER_TASK'] = str(cpus_per_task)

        runcmd = f'{scriptpath}/run_line_imaging_slurm{mpisuffix}.sh'

        now = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        os.environ['LOGFILENAME'] = f"{logpath}/casa_log_line_{jobname}_{now}.log"


        cmd = f'sbatch --ntasks={ntasks} --cpus-per-task={cpus_per_task} --mem={mem} {exclusive} {partition} --output={jobname}_%j.log --job-name={jobname} --account={account} --qos={qos} --export=ALL  {runcmd}'

        if '--dry-run' in sys.argv:
            if verbose:
                print(cmd)
            print()
            #print(subprocess.check_output('env').decode())
            #raise
        else:
            sbatch = subprocess.check_output(cmd.split())

            print(f"Started sbatch job {row} with jobid={sbatch.decode()} and parameters {spwpars}")
