#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail
#SBATCH --nodes=1
#SBATCH --time=96:00:00               # Time limit hrs:min:sec

env
pwd; hostname; date
echo "Memory=${MEM}"

export WORK_DIRECTORY='/blue/adamginsburg/adamginsburg/almaimf/workdir'
export PRODUCT_DIRECTORY='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/'

# https://github.com/ipython/ipython/issues/2426/#issuecomment-8822369
export IPYTHONDIR=/tmp

module load git
# for MPI module load cuda/11.0.207  gcc/9.3.0 openmpi/4.0.4

which python
which git

git --version
echo $?



#export CASA=/orange/adamginsburg/casa/casa-release-5.6.0-60.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-release-5.8.0-109.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-6.2.1-3/bin/casa
export CASA=/orange/adamginsburg/casa/casa-6.3.0-39/bin/casa


export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py

cd ${WORK_DIRECTORY}

export TEMP_WORKDIR=$(pwd)/${FIELD_ID}_${LINE_NAME}_${suffix12m}_${BAND_TO_IMAGE}
if ! [[ -d ${TEMP_WORKDIR} ]]; then
    mkdir ${TEMP_WORKDIR}
fi

ln ${WORK_DIRECTORY}/to_image.json ${TEMP_WORKDIR}/to_image.json
ln ${WORK_DIRECTORY}/metadata.json ${TEMP_WORKDIR}/metadata.json

cd ${TEMP_WORKDIR}
pwd
echo "Listing contents of directory $(pwd): json files $(ls -lhrt *.json), others: $(ls)"
echo "Working in ${TEMP_WORKDIR} = $(pwd)"
echo "Publishing to  ${PRODUCT_DIRECTORY}"
echo ${LINE_NAME} ${BAND_NUMBERS}


export PYTHONPATH=$ALMAIMF_ROOTDIR
export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR

echo $LOGFILENAME

# do one band at a time to enable _disabling_ one or the other
#export BAND_NUMBERS="3"
echo xvfb-run -d ${CASA} --nogui --nologger --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')"
xvfb-run -d ${CASA} --nogui --nologger --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')" &
PID=$!

/orange/adamginsburg/miniconda3/bin/python ${ALMAIMF_ROOTDIR}/slurm_scripts/monitor_memory.py ${PID}

#export BAND_NUMBERS="6"
#xvfb-run -d ${CASA} --nogui --nologger -c "execfile('$SCRIPT_DIR/line_imaging.py')"
