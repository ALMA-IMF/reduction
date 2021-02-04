#!/bin/bash
#SBATCH --mail-type=NONE          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail
#SBATCH --ntasks=8                    # Run on a single CPU
#SBATCH --nodes=1
#SBATCH --mem=32gb                     # Job memory request
#SBATCH --time=96:00:00               # Time limit hrs:min:sec
#SBATCH --output=stats_stuff_%j.log
#SBATCH --export=ALL
#SBATCH --job-name=stats_stuff
#SBATCH --qos=adamginsburg-b
#SBATCH --account=adamginsburg
pwd; hostname; date

export WORK_DIR="/orange/adamginsburg/ALMA_IMF/reduction/analysis"
export WORK_DIR="/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results"

module load git

which python
which git

git --version
echo $?



#export CASA=/orange/adamginsburg/casa/casa-pipeline-release-5.6.1-8.el7/bin/casa
export IPYTHON=/orange/adamginsburg/miniconda3/envs/casa6_py36/bin/ipython 


cd ${WORK_DIR}
python /orange/adamginsburg/ALMA_IMF/reduction/reduction/getversion.py

cd ${WORK_DIR}
echo ${WORK_DIR}
echo ${LINE_NAME} ${BAND_NUMBERS}

export SCRIPT_DIR="/orange/adamginsburg/ALMA_IMF/reduction/analysis"
export PYTHONPATH=$SCRIPT_DIR

echo $LOGFILENAME

env

xvfb-run -d ${IPYTHON} ${SCRIPT_DIR}/do_all_stats_stuff.py
