#!/bin/bash
#SBATCH --job-name=line_quicklooks      # Job name
#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adamginsburg@ufl.edu     # Where to send mail	
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32gb                     # Job memory request
#SBATCH --time=96:00:00               # Time limit hrs:min:sec
#SBATCH --output=line_quicklooks_%j.log   # Standard output and error log
#SBATCH --qos=adamginsburg
#SBATCH --account=adamginsburg-b


WORK_DIR='/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results'

cd ${WORK_DIR}
echo ${WORK_DIR}

export ALMAIMF_ROOTDIR="/orange/adamginsburg/ALMA_IMF/reduction/reduction"
export SCRIPT_DIR=$ALMAIMF_ROOTDIR
export PYTHONPATH=$SCRIPT_DIR
export NO_PROGRESSBAR=True
export DASK_THREADS=8 # TODO: make this = cpus-per-task
export OVERWRITE=True


env


echo xvfb-run -d /orange/adamginsburg/miniconda3/envs/python39/bin/python /orange/adamginsburg/ALMA_IMF/reduction/analysis/line_quicklooks.py

xvfb-run -d /orange/adamginsburg/miniconda3/envs/python39/bin/python /orange/adamginsburg/ALMA_IMF/reduction/analysis/line_quicklooks.py
