# Gaussian Splatting for 360° Video Reconstruction - Setup Guide

## Overview
This is a customized implementation of 3D Gaussian Splatting optimized for 360° video processing and reconstruction. The workflow supports extracting frames from equirectangular videos, converting to cubemap projections, running COLMAP for camera calibration, and training Gaussian Splatting models.

## Prerequisites

### Hardware Requirements
- **GPU**: CUDA-ready GPU with Compute Capability 7.0+
- **VRAM**: 24 GB recommended (minimum 8-12 GB for smaller scenes)
- **OS**: Windows 10/11 or Ubuntu Linux 22.04+

### Software Requirements
1. **Python 3.11.9** - via pyenv (Windows) or conda (HPC)
2. **CUDA Toolkit 11.8 or 12.4**
   - Install **after** Visual Studio on Windows
   - **Avoid CUDA 11.6** (known issues)
3. **Visual Studio 2019+** (Windows only) - C++ compiler for PyTorch extensions
4. **COLMAP** - For structure-from-motion processing
   - Install from: https://colmap.github.io/install.html
5. **Meshroom** (Optional) - Alternative for 360° to cubemap conversion
   - Download from: https://www.fosshub.com/Meshroom-old.html?
   - Recommended version: Meshroom v2021.1.0
   - Provides `aliceVision_utils_split360Images` tool
6. **FFmpeg** (optional) - For video frame extraction
7. **Git** - For cloning the repository


---

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url> --recursive
cd code_gaussian-splatting
```
The --recursive flag is important as it includes required submodules.

### 2. Set Up Python Environment
Option A: Windows (pyenv + venv)

```bash
# Install Python 3.11.9 via pyenv
pyenv install 3.11.9
pyenv local 3.11.9

# Create virtual environment
python -m venv gsplat_v2

# Activate environment
gsplat_v2\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies
pip install plyfile tqdm

# Install PyTorch with CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Upgrade wheel
pip install --upgrade wheel

# Install submodules
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn
pip install submodules/fused-ssim

# Install other dependencies
pip install opencv-python joblib
```

If submodule installation fails, try:
```bash
pip install --no-build-isolation submodules/diff-gaussian-rasterization
```

Option B: HPC (Nova)

```bash
# Run automated setup script
bash new_createCondaEnv_NOVA.sh
```

This automatically:
- Loads required HPC modules (CUDA, GCC, etc.)
- Creates conda environment with custom prefix
- Installs PyTorch with CUDA 12.4
- Installs all submodules and dependencies

Manual HPC setup:
```bash
# Load modules
source new_mods_NOVA.sh

# Create environment
conda env create --file new_environment.yml --prefix /work/mech-ai-scratch/<username>/conda_env/envs/gsplat_v2

# Activate environment
eval "$(micromamba shell hook --shell=bash)"
micromamba activate /work/mech-ai-scratch/<username>/conda_env/envs/gsplat_v2

# Install PyTorch
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install submodules
pip install --upgrade wheel
pip3 install submodules/diff-gaussian-rasterization
pip3 install submodules/simple-knn
pip3 install submodules/fused-ssim

# Install other dependencies
pip3 install opencv-python joblib
```

### 3. Verify Installation
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Project Structure

```bash
code_gaussian-splatting/
├── data/                    # Input data (videos, images)
├── output/                  # Trained models and renders
├── accessories/             # Utility scripts
│   ├── get360frames.py     # Extract frames from 360° video
│   ├── combinecubemap_multiple_intermediates.py  # Combine cubemap datasets
│   ├── run_scripts.py      # Unified script launcher
│   └── train_with_config.py # Config-based training launcher
├── train.py                # Main training script
├── render.py               # Rendering script
├── convert.py              # COLMAP preprocessing
├── project_config.ini      # Main configuration file (copy and modify)
└── submodules/             # Required dependencies
```

### Workflow
Step 1: Prepare Your Configuration
Copy one of the example config files:

```bash
cp project_config.ini my_project_config.ini
```

Edit my_project_config.ini to set:
- current_project - Your project name/folder
- video_name - Input 360° video filename
- skip_frames - Frame extraction rate
- cubemap_face_size - Resolution per cubemap face
- COLMAP and training parameters

Step 2: Extract Frames from 360° Video
```bash
python accessories/run_scripts.py --config my_project_config.ini get360frames
```

This will:
- Extract equirectangular frames from your video
- Convert to cubemap projections (6 faces per frame)
- Save to data/<current_project>/rawFrames/

Manual alternative:
```bash
python accessories/get360frames.py --config my_project_config.ini
```

Step 2-Alt: Convert Equirectangular to Cubemap Using Meshroom (Alternative Method)
If you prefer using Meshroom's AliceVision tools instead of the Python script:

Windows:
```bash
# Navigate to Meshroom bin directory
cd C:\Users\<username>\libraries\Meshroom-2021.1.0\aliceVision\bin

# Convert equirectangular frames to cubemap
.\aliceVision_utils_split360Images.exe `
  -i C:\path\to\project\data\<project>\rawFrames\1_equirect `
  -o C:\path\to\project\data\<project>\rawFrames\cubemap\input `
  --equirectangularNbSplits 8 `
  --equirectangularSplitResolution 1200
```

Linux/HPC:

```bash
# Navigate to Meshroom bin directory
cd /path/to/Meshroom/aliceVision/bin

# Convert equirectangular frames to cubemap
./aliceVision_utils_split360Images \
  -i /path/to/project/data/<project>/rawFrames/1_equirect \
  -o /path/to/project/data/<project>/rawFrames/cubemap/input \
  --equirectangularNbSplits 8 \
  --equirectangularSplitResolution 1200
```

Parameters:
   - -i - Input directory with equirectangular images
   - -o - Output directory for cubemap splits
   - --equirectangularNbSplits - Number of splits (8 = 8 cubemap faces)
   - --equirectangularSplitResolution - Resolution per face (e.g., 1200x1200)

Advantages of Meshroom method:
   - Faster processing (optimized C++ implementation)
   - More stable for large images
   - No Python memory issues

Example:
```bash
# Full example for Windows
cd C:\Users\dgamdha\libraries\Meshroom-2021.1.0\aliceVision\bin

.\aliceVision_utils_split360Images.exe `
  -i C:\Users\dgamdha\work\Projects\others\gaussian_splatting\code_gaussian-splatting\data\360vid2stl\blackEng_grid_20251218_aruco\rawFrames_skipframes10\1_equirect `
  -o C:\Users\dgamdha\work\Projects\others\gaussian_splatting\code_gaussian-splatting\data\360vid2stl\blackEng_grid_20251218_aruco\rawFrames_skipframes10\cubmap_combined_v1\input `
  --equirectangularNbSplits 8 `
  --equirectangularSplitResolution 1200
```

Step 3: Combine Cubemaps (if using multiple datasets)
```bash
python accessories/run_scripts.py --config my_project_config.ini combinecubemap
```

Step 4: Run COLMAP for Camera Calibration
```bash
python convert.py -s data/<your_project>/input
```

Or use the automated script:
```bash
python accessories/run_scripts.py --config my_project_config.ini convert
```

This creates COLMAP camera calibration in data/<your_project>/distorted/sparse/

Step 5: Train Gaussian Splatting Model
Using config file:
```bash
python accessories/train_with_config.py --config my_project_config.ini
```

Manual command:
```bash
python train.py -s data/<your_project> -m output/<your_project>
```

Training arguments in config:
- iterations - Total training iterations (default: 30000)
- position_lr_init - Initial learning rate for positions
- feature_lr - Learning rate for features
- save_iterations - When to save checkpoints

Step 6: Render Results

```bash
python render.py -m output/<your_project>
```

### Key Configuration Parameters
Video Processing ([video_processing] section)
- skip_frames = 10 → Extract 1 frame every 10 frames
- output_format = jpg
- video_quality = 95

Cubemap ([cubemap] section)
- face_size = 1024 → Resolution per cubemap face

COLMAP ([colmap] section)
- camera_model = OPENCV
- feature_extractor = sift
- matcher_type = sequential

Training ([gaussian_splatting] section)
- iterations = 30000
- test_iterations = 7000,30000
- save_iterations = 7000,15000,30000


### Common Issues & Troubleshooting
1. CUDA/PyTorch Mismatch
```bash
# Check versions match
python -c "import torch; print(torch.version.cuda)"
nvcc --version
```

2. Submodule Build Errors (Windows)
Ensure Visual Studio C++ tools are installed and CUDA is in PATH:

```bash
SET PATH=%PATH%;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin
```

3. Out of Memory Errors
Reduce resolution or use --data_device cpu flag:

```bash
python train.py -s data/scene -m output/scene --data_device cpu
```

4. COLMAP Not Found
Specify COLMAP path explicitly:

```bash
python convert.py -s data/scene --colmap_executable "C:/Program Files/COLMAP/COLMAP.bat"
```

### Quick Start Example

```bash
# 1. Activate environment
conda activate gsplat_v2

# 2. Copy and edit config
cp project_config.ini test_project.ini
# Edit: Set video_name, current_project

# 3. Run full pipeline
python accessories/run_scripts.py --config test_project.ini get360frames
python accessories/run_scripts.py --config test_project.ini convert
python accessories/run_scripts.py --config test_project.ini train

# 4. Render results
python render.py -m output/<project_name>
```

Note: This codebase includes custom modifications for 360° video processing not present in the original Gaussian Splatting implementation. The configuration system (project_config.ini) centralizes all parameters for easier workflow management.
