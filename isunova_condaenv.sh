# ----------
# Required modules:
# This set has python 3.9.18
# default environment.yml requires python 3.7.13
module purge
module load micromamba
module load cuda/11.8.0-zg46pdv
module load colmap
# ^^^^

# ----------
# conda env create --file environment.yml --prefix /work/mech-ai-scratch/dgamdha/conda_env/envs/gaussian_splatting
eval "$(micromamba shell hook --shell=bash)"
micromamba activate /work/mech-ai-scratch/dgamdha/conda_env/envs/gaussian_splatting
# ^^^^