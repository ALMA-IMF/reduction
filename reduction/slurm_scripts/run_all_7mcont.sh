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


for BAND_TO_IMAGE in B3 B6; do
    for FIELD_ID in G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41; do
        export FIELD_ID
        export BAND_TO_IMAGE
        export EXCLUDE_7M=False
        export ONLY_7M=True
        export LOGFILENAME="casa_log_selfcalcont_${FIELD_ID}_${BAND_TO_IMAGE}_7M_$(date +%Y-%m-%d_%H_%M_%S).log"
        jobid=$(sbatch --mem=4gb --output=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal_%j.log --job-name=${FIELD_ID}_${BAND_TO_IMAGE}_7M_selfcal --account=${ACCOUNT} --qos=${QOS} --export=ALL $CMD)
        echo ${jobid##* }
    done
done
