#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail
#SBATCH --nodes=1
#SBATCH --time=96:00:00               # Time limit hrs:min:sec

# set the path to exclude conda
export PATH=/apps/gcc/9.3.0/gsl/2.6/bin:/apps/compilers/gcc/9.3.0/bin:/apps/libfuse/3.10.4/bin:/apps/ufrc/bin:/apps/screen/4.8.0/bin:/opt/slurm/bin:/usr/lib64/qt-3.3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/puppetlabs/bin:/bin:/opt/dell/srvadmin/bin:/home/adamginsburg/bin

env
pwd; hostname; date
echo "Memory=${MEM}"

# need to force WORK_DIRECTORY to be $TMPDIR because it's dynamically assigned
#export WORK_DIRECTORY=$TMPDIR
#WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'
if [ -z $WORK_DIRECTORY ]; then
    export WORK_DIRECTORY='/blue/adamginsburg/adamginsburg/almaimf/workdir'
    #export WORK_DIRECTORY=$TMPDIR
fi
export PRODUCT_DIRECTORY='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/'
echo "WORK_DIRECTORY=${WORK_DIRECTORY}, PRODUCT_DIRECTORY=${PRODUCT_DIRECTORY}"

echo "Available temp drive: "
df -h /local

#module load git intel/2020.0.166 openmpi/4.1.1
module load git gcc/9.3.0 openmpi/4.1.1

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
    CASAVERSION=casa-6.5.0-9-py3.8
    CASAVERSION=casa-6.4.0-16
    #CASAVERSION=casa-6.3.0-48
    #CASAVERSION=casa-6.2.1-3
    #CASAVERSION=casa-6.1.0-118
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
export CASA=/blue/adamginsburg/adamginsburg/casa/${CASAVERSION}/bin/casa
export MPICASA=/blue/adamginsburg/adamginsburg/casa/${CASAVERSION}/bin/mpicasa


export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py

cd ${WORK_DIRECTORY}

export USE_TEMPORARY_WORKING_DIRECTORY=True
export TEMP_WORKDIR=$(pwd)/${FIELD_ID}_${LINE_NAME}_${suffix12m}_${BAND_TO_IMAGE}
if ! [[ -d ${TEMP_WORKDIR} ]]; then
    mkdir -v ${TEMP_WORKDIR}
fi

PROJECT_DIRECTORY=/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/
cp -v ${PROJECT_DIRECTORY}/to_image.json ${TEMP_WORKDIR}/to_image.json
cp -v ${PROJECT_DIRECTORY}/metadata.json ${TEMP_WORKDIR}/metadata.json

cd ${TEMP_WORKDIR}
pwd
echo "Listing contents of directory ${TEMP_WORKDIR}: json files $(ls -lhrt *.json), others: $(ls)"
echo "Working in ${TEMP_WORKDIR} = $(pwd)"
echo "Publishing to  ${PRODUCT_DIRECTORY}"
echo ${LINE_NAME} ${BAND_NUMBERS}

export PYTHONPATH=$ALMAIMF_ROOTDIR
export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR

cp -v ~/.casa/config.py ${TMPDIR}/
cp -v ~/.casarc ${TMPDIR}/rc
cp -v ~/.casarc ${TMPDIR}/.casarc
casamem=$(python -c "print(${SLURM_MEM_PER_NODE}/${NTASKS})")
echo "system.resources.memory: ${casamem}" >> ${TMPDIR}/rc

echo "config.py: (cat ${TMPDIR}/config.py) "
cat ${TMPDIR}/config.py
echo "rc: (cat ${TMPDIR/.casarc}) "
cat ${TMPDIR}/.casarc

echo "rc: (cat ${TMPDIR/rc}) "
cat ${TMPDIR}/rc
echo "Which is used, rc or .casarc?  I think .casarc"

echo "CASA memory set to: ${casamem} in principle, but see system.resources.memory above"

# Kumar's suggestion 4/23: try to make sure gcc isn't linked from system gcc
export LD_LIBRARY_PATH=""

echo "ldd /blue/adamginsburg/adamginsburg/casa/${CASAVERSION}/lib/libcasatools.so.4011.25.171:"
ldd /blue/adamginsburg/adamginsburg/casa/${CASAVERSION}/lib/libcasatools.so.4011.25.171

echo logfile=$LOGFILENAME

echo "DEBUG STUFF"
echo "Printing CASA path"
${CASA} --nogui --nologger --ipython-dir=${TMPDIR} --rcdir=${TMPDIR}  --logfile=${LOGFILENAME} -c "import sys; print(sys.path)"


echo "global env var CASAPATH=$CASAPATH"
echo "Using MPICASA to determine CASAPATH"
${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --ipython-dir=${TMPDIR} --rcdir=${TMPDIR}  --logfile=${LOGFILENAME} -c "import os; print(f'mpi inside casa CASAPATH=', os.getenv('CASAPATH'))"



echo Running command: ${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --ipython-dir=${TMPDIR} --rcdir=${TMPDIR}  --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')" &

${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --ipython-dir=${TMPDIR} --rcdir=${TMPDIR}  --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')" &
ppid="$!"; childPID="$(ps -C ${CASA} -o ppid=,pid= | awk -v ppid="$ppid" '$1==ppid {print $2}')"
echo PID=${ppid} childPID=${childPID}
echo "DEBUG: ps -C CASA -o ppid=,pid= : $(ps -C ${CASA} -o ppid=,pid=)"
sleep 10
date
childPID="$(ps -C ${CASA} -o ppid=,pid= | awk -v ppid="$ppid" '$1==ppid {print $2}')"
echo PID=${ppid} childPID=${childPID}
echo "DEBUG: ps -C CASA -o ppid=,pid= : $(ps -C ${CASA} -o ppid=,pid=)"

sleep 10
date
childPID="$(ps -C ${CASA} -o ppid=,pid= | awk -v ppid="$ppid" '$1==ppid {print $2}')"
echo PID=${ppid} childPID=${childPID}
echo "DEBUG: ps -C CASA -o ppid=,pid= : $(ps -C ${CASA} -o ppid=,pid=)"


date
echo "Temp drive: "
df -h /local

if [[ ! -z $childPID ]]; then 
    /orange/adamginsburg/miniconda3/bin/python ${ALMAIMF_ROOTDIR}/slurm_scripts/monitor_memory.py ${childPID}
else
    echo "FAILURE to run monitor_memory: PID=$PID was not set."
fi

wait $ppid
exitcode=$?

date
echo "Temp drive: "
df -h /local


cd -

if [[ -z $(ls -A ${TEMP_WORKDIR}) ]]; then
    rmdir -v ${TEMP_WORKDIR}
fi

exit $exitcode
