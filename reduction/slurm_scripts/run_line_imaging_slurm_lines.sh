# Image selected lines
# Specify EXCLUDE_7M=True if that's what you want
if [ $CMD ]; then
    echo $CMD
else
    CMD=/orange/adamginsburg/ALMA_IMF/reduction/reduction/slurm_scripts/run_line_imaging_slurm.sh
fi
export FIELD_ID=$1
if [ -z $EXCLUDE_7M ]; then
    export EXCLUDE_7M=True
    suffix12m="12M"
else
    if [ $EXCLUDE_7M == "True" ]; then
        suffix12m="12M"
    else 
        suffix12m="7M12M"
    fi
fi
echo "Exclude 7m = ${EXCLUDE_7M}"

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

if [ -z $DO_CONTSUB ]; then
    suffix_contsub=""
else
    if [ $DO_CONTSUB == "True" ]; then
        suffix_contsub="_cs"
    else
        suffix_contsub=""
    fi
fi
echo "Contsub = ${suffix_contsub}"

MEM=32gb
case $FIELD_ID in
W43-MM2|W51-IRS2) #B3 B6
    export MEM=64gb ;;
esac

echo field=$FIELD_ID band=$BAND_TO_IMAGE mem=$MEM exclude_7m=$EXCLUDE_7M suffix=${suffix12m} contsub=${suffix_contsub} nodeps=${NODEPS} QOS=${QOS}

export NTASKS=8
export SLURM_NTASKS=$NTASKS

# first one has to be done separately b/c it has no dependencies
export BAND_NUMBERS=3
export BAND_TO_IMAGE=B${BAND_NUMBERS}
export LINE_NAME='n2hp'
export jobname=${FIELD_ID}_${BAND_TO_IMAGE}_${LINE_NAME}_${suffix12m}${suffix_contsub}
export LOGFILENAME="casa_log_line_${jobname}_$(date +%Y-%m-%d_%H_%M_%S).log"
jobid=$(sbatch --ntasks=${NTASKS} --mem=${MEM} --output=${jobname}_%j.log --job-name=${jobname} --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
echo ${jobid##* }

# export BAND_NUMBERS=3
# export BAND_TO_IMAGE=B${BAND_NUMBERS}
# for LINE_NAME in h41a ch3cn 'ch3cnv8=1' ch3cch; do
# 
#     export jobname=${FIELD_ID}_${BAND_TO_IMAGE}_${LINE_NAME}_${suffix12m}${suffix_contsub}
#     export LOGFILENAME="casa_log_line_${jobname}_$(date +%Y-%m-%d_%H_%M_%S).log"
# 
#     if [ ${jobid##* } ]; then
#         if [ -z $NODEPS ]; then
#             dependency="--dependency=afterok:${jobid##* }"
#         else
#             dependency=""
#         fi
#     else
#         dependency=""
#     fi
# 
# 
#     jobid=$(sbatch --ntasks=${NTASKS} --mem=${MEM} --output=${jobname}_%j.log --job-name=${jobname} --account=${ACCOUNT} --qos=${QOS} ${dependency} --export=ALL $CMD)
#     echo ${jobid##* }
# 
# done


export BAND_NUMBERS=6
export BAND_TO_IMAGE=B${BAND_NUMBERS}
for LINE_NAME in sio; do # h2co303 h30a 12co c18o; do

    export jobname=${FIELD_ID}_${BAND_TO_IMAGE}_${LINE_NAME}_${suffix12m}${suffix_contsub}
    export LOGFILENAME="casa_log_line_${jobname}_$(date +%Y-%m-%d_%H_%M_%S).log"

    if [ ${jobid##* } ]; then
        if [ -z $NODEPS ]; then
            dependency="--dependency=afterok:${jobid##* }"
        else
            dependency=""
        fi
    else
        dependency=""
    fi

    jobid=$(sbatch --ntasks=${NTASKS} --mem=${MEM} --output=${jobname}_%j.log --job-name=${jobname} --account=${ACCOUNT} --qos=${QOS} ${dependency} --export=ALL $CMD)
    echo ${jobid##* }

done
