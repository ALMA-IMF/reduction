#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail
#SBATCH --nodes=1
#SBATCH --time=96:00:00               # Time limit hrs:min:sec

env
pwd; hostname; date
echo "Memory=${MEM}"

#WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'
if [ -z $WORK_DIRECTORY ]; then
    export WORK_DIRECTORY='/blue/adamginsburg/adamginsburg/almaimf/workdir'
fi
export PRODUCT_DIRECTORY='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/'

module load git
#module load cuda/11.0.207  gcc/9.3.0 openmpi/4.0.4
module load intel/2020.0.166
module load openmpi/4.1.1 

which python
which git

git --version
echo $?

if [ -z $SLURM_NTASKS ]; then
    echo "FAILURE - SLURM_NTASKS=${SLURM_NTASKS}, i.e., empty"
    exit
fi

# MPI stuff
# https://www.open-mpi.org/faq/?category=running#mpi-environmental-variables
# OMPI_COMM_WORLD_SIZE - the number of processes in this process's MPI_COMM_WORLD
OMPI_COMM_WORLD_SIZE=$SLURM_NTASKS
# OMPI_COMM_WORLD_RANK - the MPI rank of this process in MPI_COMM_WORLD
# OMPI_COMM_WORLD_LOCAL_RANK - the relative rank of this process on this node within its job. For example, if four processes in a job share a node, they will each be given a local rank ranging from 0 to 3.
# OMPI_UNIVERSE_SIZE - the number of process slots allocated to this job. Note that this may be different than the number of processes in the job.
# OMPI_COMM_WORLD_LOCAL_SIZE - the number of ranks from this job that are running on this node.
# OMPI_COMM_WORLD_NODE_RANK - the relative rank of this process on this node looking across ALL jobs.

if [[ ! $CASAVERSION ]]; then
    #CASAVERSION=casa-6.4.3-4
    CASAVERSION=casa-6.4.4-31-py3.8
    echo "Set CASA version to default ${CASAVERSION}"
fi
echo "CASA version = ${CASAVERSION}"

#export CASA=/orange/adamginsburg/casa/casa-release-5.6.0-60.el7/bin/casa
#export CASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/casa
#export MPICASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/mpicasa
#export CASA=/orange/adamginsburg/casa/casa-release-5.8.0-109.el7/bin/casa
#export MPICASA=/orange/adamginsburg/casa/casa-pipeline-release-5.8.0-109.el7/bin/mpicasa
#export CASA=/orange/adamginsburg/casa/casa-6.2.1-3/bin/casa
#export MPICASA=/orange/adamginsburg/casa/casa-6.2.1-3/bin/mpicasa
#export CASA=/orange/adamginsburg/casa/casa-6.3.0-39/bin/casa
#export MPICASA=/orange/adamginsburg/casa/casa-6.3.0-39/bin/mpicasa
#export CASA=/blue/adamginsburg/adamginsburg/casa/casa-CAS-13609-1/bin/casa
#export MPICASA=/blue/adamginsburg/adamginsburg/casa/casa-CAS-13609-1/bin/mpicasa
#export CASA=/orange/adamginsburg/casa/casa-6.4.0-12/bin/casa
#export MPICASA=/blue/adamginsburg/adamginsburg/casa/casa-6.4.0-12/bin/mpicasa
export CASA=/orange/adamginsburg/casa/${CASAVERSION}/bin/casa
export MPICASA=/blue/adamginsburg/adamginsburg/casa/${CASAVERSION}/bin/mpicasa


export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py

cd ${WORK_DIRECTORY}

export USE_TEMPORARY_WORKING_DIRECTORY=True
export TEMP_WORKDIR=$(pwd)/${FIELD_ID}_${LINE_NAME}_${suffix12m}_${BAND_TO_IMAGE}
if ! [[ -d ${TEMP_WORKDIR} ]]; then
    mkdir ${TEMP_WORKDIR}
fi

ln ${WORK_DIRECTORY}/to_image.json ${TEMP_WORKDIR}/to_image.json
ln ${WORK_DIRECTORY}/metadata.json ${TEMP_WORKDIR}/metadata.json

cd ${TEMP_WORKDIR}
pwd
echo "Listing contents of directory ${TEMP_WORKDIR}: json files $(ls -lhrt *.json), others: $(ls)"
echo "Working in ${TEMP_WORKDIR} = $(pwd)"
echo "Publishing to  ${PRODUCT_DIRECTORY}"
echo ${LINE_NAME} ${BAND_NUMBERS}

export PYTHONPATH=$ALMAIMF_ROOTDIR
export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR

echo logfile=$LOGFILENAME

echo Running command: ${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --ipython-dir=/tmp  --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')" &

${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --ipython-dir=/tmp  --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')" &
ppid="$!"; childPID="$(ps -C ${CASA} -o ppid=,pid= | awk -v ppid="$ppid" '$1==ppid {print $2}')"
echo PID=${ppid} childPID=${childPID}

if [[ ! -z $childPID ]]; then 
    /orange/adamginsburg/miniconda3/bin/python ${ALMAIMF_ROOTDIR}/slurm_scripts/monitor_memory.py ${childPID}
else
    echo "FAILURE: PID=$PID was not set."
fi

wait $ppid
exitcode=$?

cd -

if [[ -z $(ls -A ${TEMP_WORKDIR}) ]]; then
    rmdir ${TEMP_WORKDIR}
fi

exit $exitcode
