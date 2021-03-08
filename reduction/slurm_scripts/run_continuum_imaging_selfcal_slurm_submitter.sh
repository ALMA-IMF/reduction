export FIELD_ID=$1


CMD=/orange/adamginsburg/ALMA_IMF/reduction/reduction/slurm_scripts/run_continuum_imaging_selfcal_slurm.sh

if [ -z $QOS ]; then
    export QOS=adamginsburg-b
fi

case $QOS in
    *adamginsburg*)
        export ACCOUNT=adamginsburg
        ;;
    *astronomy-dept*)
        export ACCOUNT=astronomy-dept
        ;;
esac


export ONLY_7M=False
export EXCLUDE_7M=True
export BAND_TO_IMAGE=B6

#CMD=/orange/adamginsburg/ALMA_IMF/reduction/reduction/run_continuum_imaging_slurm.sh
#export LOGFILENAME="casa_log_continuum_${FIELD_ID}_${BAND_TO_IMAGE}_12M_$(date +%Y-%m-%d_%H_%M_%S).log"
#jobid=$(sbatch --output=${FIELD_ID}_${BAND_TO_IMAGE}_12Mcont_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12Mcont --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
#echo ${jobid##* }

export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_12M_$(date +%Y-%m-%d_%H_%M_%S).log"
jobid=$(sbatch --output=${FIELD_ID}_${BAND_TO_IMAGE}_12M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
echo ${jobid##* }

export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_$(date +%Y-%m-%d_%H_%M_%S).log"
export DO_BSENS=True
jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
echo ${jobid##* }
export DO_BSENS=False


# export EXCLUDE_7M=False
# export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_$(date +%Y-%m-%d_%H_%M_%S).log"
# jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
# echo ${jobid##* }
# 
# export EXCLUDE_7M=False
# export ONLY_7M=True
# export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_7M_$(date +%Y-%m-%d_%H_%M_%S).log"
# jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
# echo ${jobid##* }



export ONLY_7M=False
export EXCLUDE_7M=True
export BAND_TO_IMAGE=B3
#CMD=/orange/adamginsburg/ALMA_IMF/reduction/reduction/run_continuum_imaging_slurm.sh
#export LOGFILENAME="casa_log_continuum_${FIELD_ID}_${BAND_TO_IMAGE}_12M_$(date +%Y-%m-%d_%H_%M_%S).log"
#jobid=$(sbatch --output=${FIELD_ID}_${BAND_TO_IMAGE}_12Mcont_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12Mcont --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
#echo ${jobid##* }

export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_12M_$(date +%Y-%m-%d_%H_%M_%S).log"
jobid=$(sbatch --output=${FIELD_ID}_${BAND_TO_IMAGE}_12M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
echo ${jobid##* }

export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_$(date +%Y-%m-%d_%H_%M_%S).log"
export DO_BSENS=True
jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_12M_bsens_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
echo ${jobid##* }
export DO_BSENS=False

# export EXCLUDE_7M=False
# export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_$(date +%Y-%m-%d_%H_%M_%S).log"
# jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_7M12M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
# echo ${jobid##* }
# 
# export EXCLUDE_7M=False
# export ONLY_7M=True
# export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_7M_$(date +%Y-%m-%d_%H_%M_%S).log"
# jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
# echo ${jobid##* }
