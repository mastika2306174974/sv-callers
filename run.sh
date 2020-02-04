#!/usr/bin/env bash

set -xe

CALLERS=(manta delly lumpy gridss)
STR_CALLERS="[$(printf "'%s'," "${CALLERS[@]}"|sed 's/,$//')]"
EXIT_CODE=0
ECHO=$1
MODE=$2
SCH=$3
SAMPLES="samples.csv"
USE_CONDA=$([ "$ECHO" -eq "0" ] && echo "--use-conda" || echo "")
MY_ENV=wf

eval "$(conda shell.bash hook)"
conda activate $MY_ENV
conda list
cd snakemake && ls -alh
echo "Selected callers: $STR_CALLERS"
snakemake -C echo_run=$ECHO samples=$SAMPLES mode=$MODE \
  enable_callers="$STR_CALLERS" $USE_CONDA \
  --configfile analysis_test.yaml \
  --latency-wait 60 --jobs \
  --cluster "xenon -vvv scheduler $SCH --location local:// submit \
  --name smk.{rule} --cores-per-task {threads} --inherit-env \
  --max-run-time 15 --working-directory . \
  --stderr stderr-%j.log --stdout stdout-%j.log"

echo -e "\nVCF output files:"
if [ "$ECHO" -eq "0" ]; then
  for caller in "${CALLERS[@]}"; do
    VCF_FILE="$(find data -mindepth 6 -name $caller.vcf)"
    BOOL=$([ -e  "$VCF_FILE" ] && echo 0 || echo 1)
    INFO=$([ $BOOL -eq 0 ] && echo "$VCF_FILE" || echo "None")
    if [ $BOOL -gt $EXIT_CODE ]; then
      EXIT_CODE=1
    fi
    echo " $caller: $INFO"
  done
  echo " merge:" $(find data -name all.vcf)
fi

echo -e "\nLog files:"
ls *.log
for f in *.log; do
  echo -e "\n### $f ###\n"
  cat $f
done

exit $EXIT_CODE
