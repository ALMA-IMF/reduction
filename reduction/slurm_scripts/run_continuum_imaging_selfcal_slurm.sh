#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail	
#SBATCH --ntasks=4
#SBATCH --mem=16gb                     # Job memory request
#SBATCH --nodes=1
#SBATCH --time=96:00:00               # Time limit hrs:min:sec
#SBATCH --qos=adamginsburg-b
#SBATCH --account=adamginsburg
pwd; hostname; date

module load git

which python
which git

git --version
echo $?

export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py


WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'

#export CASA=/blue/adamginsburg/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-release-5.6.0-60.el7/bin/casa
export CASA=/orange/adamginsburg/casa/casa-release-5.7.0-134.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-release-5.8.0-109.el7/bin/casa 

cd ${WORK_DIR}
echo ${WORK_DIR}
echo FIELD=${FIELD_ID}  BAND=${BAND_TO_IMAGE}  EXCLUDE_7M=${EXCLUDE_7M}  ONLY_7M=${ONLY_7M}

export PYTHONPATH=$ALMAIMF_ROOTDIR

echo "Logfilename is ${LOGFILENAME}"
echo xvfb-run -d ${CASA} --logfile=${LOGFILENAME}  --nogui --nologger -c "execfile('$ALMAIMF_ROOTDIR/continuum_imaging_selfcal.py')"
echo "ALMAIMF_ROOTDIR: ${ALMAIMF_ROOTDIR}"

# casa's python requires a DISPLAY for matplot so create a virtual X server
xvfb-run -d ${CASA} --logfile=${LOGFILENAME}  --nogui --nologger -c "execfile('$ALMAIMF_ROOTDIR/continuum_imaging_selfcal.py')"
xvfb-run -d ${CASA} --logfile=${LOGFILENAME}  --nogui --nologger -c "execfile('$ALMAIMF_ROOTDIR/continuum_imaging_finaliter.py')"
