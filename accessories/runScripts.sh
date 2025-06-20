#!/bin/bash

# ==============================================================================
# Linux Run Scripts - Gaussian Splatting
# ==============================================================================
# Simple bash script to run Python scripts with configurable paths

# Configuration Variables
# ==============================================================================

# Base paths
BASE_PATH="/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting"
DATA_PATH="$BASE_PATH/data"
ACCESSORIES_PATH="$BASE_PATH/accessories"

# Project configuration (modify as needed)
PROJECT_PATH="2025_jan_14/customFrames/vid_2/rawFrames"  # Adjust this path for your project structure
INPUT_FOLDER="1_equirect"
OUTPUT_FOLDER="4_cubemap_combined/ver5"

# Script parameters
CONFIG_FILE="$ACCESSORIES_PATH/combcube_multi_interme_config.txt"
EQUIRECT_DIR="$DATA_PATH/$PROJECT_PATH/$INPUT_FOLDER"
OUT_DIR="$DATA_PATH/$PROJECT_PATH/$OUTPUT_FOLDER"
START_IDX=20
END_IDX=100
NUM_INTERMEDIATE=3
VFOV=90
OUT_SIZE=512

# Script Execution
# ==============================================================================

echo "=== Running Cubemap Multiple Intermediates ==="
echo "Config: $CONFIG_FILE"
echo "Input: $EQUIRECT_DIR"
echo "Output: $OUT_DIR"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$OUT_DIR"

# Run the Python script
python combinecubemap_multiple_intermediates.py \
    --config "$CONFIG_FILE" \
    --equirect_dir "$EQUIRECT_DIR" \
    --start_idx $START_IDX \
    --end_idx $END_IDX \
    --num_intermediate $NUM_INTERMEDIATE \
    --vfov $VFOV \
    --out_size $OUT_SIZE \
    --out_dir "$OUT_DIR"

echo "Script execution completed!"

# Additional Scripts (uncomment to use)
# ==============================================================================

# Alternative script with different parameters
: '
python combinecubemap_multiple.py \
    --config "$ACCESSORIES_PATH/combcube_multi_config.txt" \
    --start_idx 20 \
    --end_idx 100 \
    --out_dir "$DATA_PATH/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver4"
'


