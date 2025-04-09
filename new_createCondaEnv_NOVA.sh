
echo "Loading modules..."
source new_mods_NOVA.sh

echo "Creating conda environment..."
conda env create --file new_environment.yml --prefix /work/mech-ai-scratch/dgamdha/conda_env/envs/gsplat_v2

echo "Activating environment..."
eval "$(micromamba shell hook --shell=bash)"
micromamba activate /work/mech-ai-scratch/dgamdha/conda_env/envs/gsplat_v2

echo "Installing dependencies..."
echo "Installing PyTorch..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo "Installing submodules..."
pip3 install submodules/diff-gaussian-rasterization
pip3 install submodules/simple-knn
pip3 install submodules/fused-ssim

echo "Installing other..."
pip3 install opencv-python joblib

echo "Installing Completed!"

