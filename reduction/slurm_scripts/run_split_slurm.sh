#!/bin/bash
#SBATCH --job-name=split_windows      # Job name
#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail	
#SBATCH --ntasks=1
#SBATCH --mem=4gb                     # Job memory request
#SBATCH --time=168:00:00               # Time limit hrs:min:sec
#SBATCH --output=split_windows_%j.log   # Standard output and error log


WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'

module load git

which python
which git

git --version
echo $?

export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py

cd ${WORK_DIR}
echo ${WORK_DIR}

export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR

export CASA=/orange/adamginsburg/casa/casa-release-5.6.0-60.el7/bin/casa

export LOGFILENAME="casa_log_split_$(date +%Y-%m-%d_%H_%M_%S).log"

echo $LOGFILENAME

# casa's python requires a DISPLAY for matplot so create a virtual X server
xvfb-run -d ${CASA} --nogui --nologger --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/split_windows.py')"
