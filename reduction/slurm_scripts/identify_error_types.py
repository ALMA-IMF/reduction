# script to scan through log files and search for errors


import glob
import json
from astropy.utils.console import ProgressBar

ignore = ['Leap second table TAI_UTC', 'Until the table is updated', 'times and coordinates derived']

filenames = glob.glob("*.log")

errmsg = {}
for fn in ProgressBar(filenames):
    errmsg[fn] = []
    with open(fn, 'r') as fh:
        for line in fh.readlines():
            if 'SEVERE' in line and not any(x in line for x in ignore):
                errmsg[fn].append(line)
            if 'oom-kill' in line:
                errmsg[fn].append(line)

errmsg = {key: val for key,val in errmsg.items() if val}

classes = ['RuntimeError: Error in making PSF',
           'Error in making PSF : Cannot open existing image :',
           'RuntimeError: Error in Weighting : Table DataManager error: ',
           'cannot be created; it is in use in another process',
           'SEVERE error encountered: model column was not populated!Therefore, populated model column',
           'Please set chanchunks=1 or choose chanchunks',
           'There is a shape mismatch between existing images',
           'RuntimeError: Error in running Minor Cycle : Error (Resource deadlock avoided)',
           'Exception from task_tclean : Error in running Major Cycle : Cannot open existing image :',
           'Exception Reported: Error (Resource deadlock avoided) when acquiring lock on ',
           'RuntimeError: Error in running Major Cycle : Directory: ',
           'RuntimeError: Error initializing the Minor Cycle',
           'RuntimeError: Error (Resource deadlock avoided) when acquiring lock on',
           'oom-kill event',
           'Array has no elements',
           'Exception from task_tclean : Invalid Image Parameter set',
           'Exception from task_tclean : Invalid Deconvolver Parameter set : Mask image ',
           'RuntimeError: Invalid Image Parameter set : Model',
           'No work directory with at least ',
           'RuntimeError: Restoration Error  : Error in copying internal T/F mask',
           'Exception from task_tclean : Restoration Error  : Error in copying internal T/F mask : Invalid Table operation: SetupNewTable',
           'Exception Reported: Binning accounting',
          ]


classified = {key: [logname for logname in errmsg if any(key in x for x in errmsg[logname])]
              for key in classes}
unclassified = {key: val for key, val in errmsg.items() if not any(key in x for x in classified.values())}

len(unclassified)
classified_count = {key: len(val) for key, val in classified.items()}
