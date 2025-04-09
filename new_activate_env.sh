
# NOVA Modules to load
# source mods_NOVA.sh script to load modules
echo "Loading modules..."
source new_mods_NOVA.sh

# ----------
# conda env create --file basic_environment.yml --prefix /work/mech-ai-scratch/dgamdha/conda_env/envs/gsplat_v2
eval "$(micromamba shell hook --shell=bash)"
micromamba activate /work/mech-ai-scratch/dgamdha/conda_env/envs/gsplat_v2