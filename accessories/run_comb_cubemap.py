#!/usr/bin/env python3
"""
Cross-Platform Run Scripts - Gaussian Splatting
================================================================
Universal Python script to run Python scripts with configurable paths
Works on both Windows and Linux systems

Usage: Run from project root directory with:
    python accessories/run_scripts.py
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# Configuration Variables
# ============================================================================

# Automatically detect project root (parent directory of accessories folder)
SCRIPT_DIR = Path(__file__).parent  # accessories folder
BASE_PATH = SCRIPT_DIR.parent        # project root folder

# Platform-specific config files
if platform.system() == "Windows":
    CONFIG_FILE = "win_combcube_multi_interme_config.txt"
else:  # Linux/Unix
    CONFIG_FILE = "combcube_multi_interme_config.txt"

DATA_PATH = BASE_PATH / "data"
ACCESSORIES_PATH = SCRIPT_DIR  # Use SCRIPT_DIR directly since it's already the accessories folder

# Project configuration (modify as needed)
PROJECT_PATH = "2025_jan_14/customFrames/vid_2/rawFrames"  # Adjust for your project structure
INPUT_FOLDER = "1_equirect"
OUTPUT_FOLDER = "4_cubemap_combined/ver5"

# Script parameters
CONFIG_PATH = ACCESSORIES_PATH / CONFIG_FILE
EQUIRECT_DIR = DATA_PATH / PROJECT_PATH / INPUT_FOLDER
OUT_DIR = DATA_PATH / PROJECT_PATH / OUTPUT_FOLDER
START_IDX = 20
END_IDX = 100
NUM_INTERMEDIATE = 3
VFOV = 90
OUT_SIZE = 512

# Script Execution Functions
# ============================================================================

def show_configuration():
    """Display current configuration"""
    print("=== Current Configuration ===")
    print(f"Platform: {platform.system()}")
    print(f"Base Path: {BASE_PATH}")
    print(f"Project Path: {PROJECT_PATH}")
    print()
    print("Paths:")
    print(f"Config: {CONFIG_PATH}")
    print(f"Input: {EQUIRECT_DIR}")
    print(f"Output: {OUT_DIR}")
    print()
    print("Parameters:")
    print(f"Start Index: {START_IDX}")
    print(f"End Index: {END_IDX}")
    print(f"Intermediates: {NUM_INTERMEDIATE}")
    print(f"VFOV: {VFOV}")
    print(f"Output Size: {OUT_SIZE}")

def run_cubemap_multiple_intermediates():
    """Run the main cubemap multiple intermediates script"""
    print("=== Running Cubemap Multiple Intermediates ===")
    print(f"Config: {CONFIG_PATH}")
    print(f"Input: {EQUIRECT_DIR}")
    print(f"Output: {OUT_DIR}")
    print()
    
    # Check if input directory exists
    if not EQUIRECT_DIR.exists():
        print(f"Error: Input directory does not exist: {EQUIRECT_DIR}")
        return False
    
    # Create output directory if it doesn't exist
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory ready: {OUT_DIR}")
    
    # Prepare command arguments
    cmd = [
        "python", "combinecubemap_multiple_intermediates.py",
        "--config", str(CONFIG_PATH),
        "--equirect_dir", str(EQUIRECT_DIR),
        "--start_idx", str(START_IDX),
        "--end_idx", str(END_IDX),
        "--num_intermediate", str(NUM_INTERMEDIATE),
        "--vfov", str(VFOV),
        "--out_size", str(OUT_SIZE),
        "--out_dir", str(OUT_DIR)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Execute the script
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("Script execution completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Script execution failed with return code {e.returncode}")
        return False
    except FileNotFoundError:
        print("Error: Python or the target script not found")
        return False

def main():
    """Main execution function"""
    print("=== Gaussian Splatting Run Scripts ===")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Project Root: {BASE_PATH}")
    print()
    print("Usage: Run this script from project root with 'python accessories/run_scripts.py'")
    print()
    
    # Simple menu
    while True:
        print("Choose an option:")
        print("1. Run Multiple Intermediates")
        print("2. Show Configuration")
        print("3. Exit")
        
        choice = input("Enter your choice [1-4]: ").strip()
        
        if choice == "1":
            run_cubemap_multiple_intermediates()
        elif choice == "2":
            show_configuration()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()

# Legacy Commands (for reference)
# ============================================================================
# Windows:
# python combinecubemap_multiple_intermediates.py --config "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\code_gaussian-splatting\accessories\win_combcube_multi_interme_config.txt" --equirect_dir "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\data\2025_jan_14\customFrames\vid_2\rawFrames\1_equirect" --start_idx 20 --end_idx 100 --num_intermediate 3 --vfov 90 --out_size 512 --out_dir "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\data\2025_jan_14\customFrames\vid_2\rawFrames\4_cubemap_combined\ver5"

# Linux:
# python combinecubemap_multiple_intermediates.py --config /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/accessories/combcube_multi_interme_config.txt --equirect_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/1_equirect --start_idx 20 --end_idx 100 --num_intermediate 3 --vfov 90 --out_size 512 --out_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver5
