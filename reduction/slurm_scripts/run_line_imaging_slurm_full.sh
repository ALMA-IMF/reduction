# Image whole bands
CMD=/orange/adamginsburg/ALMA_IMF/reduction/reduction/slurm_scripts/run_line_imaging_slurm.sh
export FIELD_ID=$1
export BAND_NUMBERS=3
export BAND_TO_IMAGE=B${BAND_NUMBERS}
export MEM=64gb

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

# re-trying without specifying giant memory - chanchunks should be able to handle this, right?
# WRONG! Chanchunks doesn't help because automultithresh is a poop.
#case $FIELD_ID in
#G338.93|W51-E|W51-IRS2|G10.62) # B3 needs bigger; B6 is probably OK w/96
#    declare -A mem_map=( ["0"]="64gb" ["3"]="64gb" ["6"]="64gb" ["7"]="64gb" ) ;;
#G333.60|W43-MM3|G353.41|G351.77|G337.92) #B3 B6
#    export MEM=96gb ;;
#W43-MM1|W43-MM2|G008.67) # only B3 needs more...
#    export MEM=96gb ;;
#esac
#case $FIELD_ID in
#G338.93|W51-E|W51-IRS2|G10.62) # B3 needs bigger; B6 is probably OK w/96
#    export CHANCHUNKS=64 ;;
#G333.60|W43-MM3|G353.41|G351.77|G337.92) #B3 B6
#    export CHANCHUNKS=32 ;;
#W43-MM1|W43-MM2|G008.67) # only B3 needs more...
#    export CHANCHUNKS=16 ;;
#esac

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

if [ -z $DO_CONTSUB ]; then
    suffix_contsub=""
else
    if [ $DO_CONTSUB == "True" ]; then
        suffix_contsub="_cs"
    else
        suffix_contsub=""
    fi
fi

echo field=$FIELD_ID band=$BAND_TO_IMAGE mem=$MEM exclude_7m=$EXCLUDE_7M suffix=${suffix12m} contsub=${suffix_contsub}

if [ $EXCLUDE_7M == "False" ]; then
    if [ $suffix12m != "7M12M" ]; then
        exit 1;
    fi
fi

jobid=""
for SPW in {0..3}; do
    export LINE_NAME=spw${SPW}

    jobname=${FIELD_ID}_${BAND_TO_IMAGE}_fullcube_${suffix12m}_${SPW}${suffix_contsub} 

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


    jobid=$(sbatch --mem=${MEM} --output=${jobname}_%j.log --job-name=${jobname} --account=${ACCOUNT} --qos=${QOS} --export=ALL ${dependency} $CMD)
    echo ${jobid##* }
    #export EXCLUDE_7M=False
    #export LOGFILENAME="casa_log_line_${FIELD_ID}_${BAND_TO_IMAGE}_${SPW}_fullcube_7M${suffix12m}_$(date +%Y-%m-%d_%H_%M_%S).log"
    #jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_fullcube_7M${suffix12m}_${SPW}_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_fullcube_7M12M_${SPW} --export=ALL $CMD)
    #echo ${jobid##* }
done

export BAND_NUMBERS=6
export BAND_TO_IMAGE=B${BAND_NUMBERS}
jobid=""

export MEM=32gb

case $FIELD_ID in
W51-IRS2|G10.62|G333.60|W51-E|W43-MM3|G353.41|G351.77|G338.93|G337.92)
    declare -A mem_map=( ["0"]="64gb" ["3"]="64gb" ["6"]="64gb" ["7"]="64gb" ) ;;
esac

echo field=$FIELD_ID band=$BAND_TO_IMAGE mem=$MEM exclude_7m=$EXCLUDE_7M suffix=${suffix12m} contsub=${suffix_contsub}

for SPW in {0..7}; do
    export LINE_NAME=spw${SPW}

    if [ ${jobid##* } ]; then
        if [ -z $NODEPS ]; then
            dependency="--dependency=afterok:${jobid##* }"
        else
            dependency=""
        fi
    else
        dependency=""
    fi

    # ternary operator - if `mem_map` doesn't exist, or if `mem_map[$blah]` doesn't exist, will set back to default
    [[ ${mem_map[$SPW]} ]] && export MEM=${mem_map[$SPW]} || export MEM=32gb

    jobname=${FIELD_ID}_${BAND_TO_IMAGE}_fullcube_${suffix12m}_${SPW}${suffix_contsub}
    export LOGFILENAME="casa_log_line_${jobname}_$(date +%Y-%m-%d_%H_%M_%S).log"

    jobid=$(sbatch --mem=${MEM} --output=${jobname}_%j.log --job-name=$jobname --account=${ACCOUNT} --qos=${QOS} --export=ALL ${dependency} $CMD)
    echo ${jobid##* }
    #export EXCLUDE_7M=False
    #export LOGFILENAME="casa_log_line_${FIELD_ID}_${BAND_TO_IMAGE}_${SPW}_fullcube_7M${suffix12m}_$(date +%Y-%m-%d_%H_%M_%S).log"
    #jobid=$(sbatch --dependency=afterok:${jobid##* } --output=${FIELD_ID}_${BAND_TO_IMAGE}_${SPW}_fullcube_7M${suffix12m}_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_fullcube_7M12M_${SPW} --export=ALL $CMD)
    #echo ${jobid##* }
done
