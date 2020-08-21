#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail
#SBATCH --ntasks=8                    # Run on a single CPU
#SBATCH --ntasks-per-node=8
#SBATCH --nodes=1
#SBATCH --time=96:00:00               # Time limit hrs:min:sec

env
pwd; hostname; date
echo "Memory=${MEM}"

WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L'

module load git
module load cuda/11.0.207  gcc/9.3.0 openmpi/4.0.4

which python
which git

git --version
echo $?

# MPI stuff
# https://www.open-mpi.org/faq/?category=running#mpi-environmental-variables
# OMPI_COMM_WORLD_SIZE - the number of processes in this process's MPI_COMM_WORLD
OMPI_COMM_WORLD_SIZE=$SLURM_NTASKS
# OMPI_COMM_WORLD_RANK - the MPI rank of this process in MPI_COMM_WORLD
# OMPI_COMM_WORLD_LOCAL_RANK - the relative rank of this process on this node within its job. For example, if four processes in a job share a node, they will each be given a local rank ranging from 0 to 3.
# OMPI_UNIVERSE_SIZE - the number of process slots allocated to this job. Note that this may be different than the number of processes in the job.
# OMPI_COMM_WORLD_LOCAL_SIZE - the number of ranks from this job that are running on this node.
# OMPI_COMM_WORLD_NODE_RANK - the relative rank of this process on this node looking across ALL jobs.


export CASA=/orange/adamginsburg/casa/casa-release-5.6.0-60.el7/bin/casa
export CASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/casa
export MPICASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/mpicasa


export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
cd ${ALMAIMF_ROOTDIR}
python getversion.py

cd ${WORK_DIR}
echo ${WORK_DIR}
echo ${LINE_NAME} ${BAND_NUMBERS}

export PYTHONPATH=$ALMAIMF_ROOTDIR
export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR

echo $LOGFILENAME

# do one band at a time to enable _disabling_ one or the other
#export BAND_NUMBERS="3"
echo srun --mpi=pmix_v3 ${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')"
# srun --mpi=pmix_v3 
${MPICASA} -n ${SLURM_NTASKS} ${CASA} --nogui --nologger --logfile=${LOGFILENAME} -c "execfile('$SCRIPT_DIR/line_imaging.py')"

#export BAND_NUMBERS="6"
#xvfb-run -d ${CASA} --nogui --nologger -c "execfile('$SCRIPT_DIR/line_imaging.py')"
