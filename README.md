# sv-callers

Structural variants (SVs) are an important class of genetic variation implicated in a wide array of genetic diseases. _sv-callers_ is a Snakemake-based workflow that combines several state-of-the-art tools for detecting SVs in whole genome sequencing (WGS) data. The workflow is easy to use and deploy on any Linux-based machine. In particular, the workflow supports automated software deployment, easy configuration and addition of new analysis tools as well as enables to scale from a single computer to different HPC clusters with minimal effort.

### Dependencies

- python (>=3.6)
- [conda](https://conda.io/) (>=4.5)
- [snakemake](https://snakemake.readthedocs.io/) (>=4.7)
- [xenon-cli](https://github.com/NLeSC/xenon-cli) (2.4)

**1. Clone this git repo.**

```bash
git clone https://github.com/GooglingTheCancerGenome/sv-callers.git
```

**2. Install dependencies.**

```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh # python 3
bash Miniconda3-latest-Linux-x86_64.sh # install & add conda to your PATH
source ~/.bashrc
conda update -y conda # update conda
conda create -n wf activate wf # create & activate a new environment
conda install snakemake
conda install -c nlesc xenon-cli # optional but recommended;)
```

**3. Execute the workflow.**
- **input**:
   - tumor/normal (T/N) sample pairs in `.bam` (incl. index files)
   - reference genome in `.fasta` (incl. index files)
- **output**: somatic SVs in `.vcf` (incl. index files)

Note: One pair of T/N samples will generate eight SV calling jobs (i.e. 1 x Manta, 1 x LUMPY, 1 x GRIDSS and 5 x DELLY) and one DELLY post-processing job that merges the SV type calls into one VCF file. See an instance of the workflow [here](https://github.com/GooglingTheCancerGenome/sv-callers/blob/master/doc/sv_calling_workflow.png).


```bash
cd sv-callers/snakemake
snakemake -np # dry run doesn't execute anything only checks I/O files
snakemake -C echo_run=1 # dummy run executes 'echo' for each caller and outputs (dummy) *.vcf files
```

_Submit to Grid Engine-based cluster_

```bash
#   dummy run: set echo_run=1 (default)
#   SV calling:
#     set echo_run=0 and increase the runtime limit e.g. to 60 (in minutes)
#     or selectively enable_callers="['manta','delly']" etc.
snakemake -C echo_run=1 --use-conda --latency-wait 30 --jobs  9 \
--cluster 'xenon scheduler gridengine --location local:// submit --name smk.{rule} --inherit-env --option parallel.environment=threaded --option parallel.slots={threads} --max-run-time 1 --max-memory {resources.mem_mb} --working-directory . --stderr stderr-\\\$JOB_ID.log --stdout stdout-\\\$JOB_ID.log' &>smk.log&
```

_Submit to Slurm-based cluster_

```bash
snakemake -C echo_run=1 --use-conda --latency-wait 30 --jobs  9 \
--cluster 'xenon scheduler slurm --location local:// submit --name smk.{rule} --inherit-env --procs-per-node {threads} --start-single-process --max-run-time 1 --max-memory {resources.mem_mb} --working-directory . --stderr stderr-%j.log --stdout stdout-%j.log' &>smk.log&
```
