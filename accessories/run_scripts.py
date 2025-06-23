#!/usr/bin/env python3
"""
Pure Script Launcher - Gaussian Splatting
==========================================
Simple cross-platform launcher for project scripts.
All configuration is handled by individual scripts via project_config.ini.

Usage: Run from project root directory with:
    python accessories/run_scripts.py [script_name] [--config CONFIG_FILE]

Available scripts:
    get360frames                  - Extract 360-degree frames from video
    combinecubemap                - Combine multiple cubemap datasets with intermediates
    train                         - Train Gaussian Splatting model with config parameters

Options:
    --config CONFIG_FILE          - Use specified config file (default: project_config.ini)
    
If no script name is provided, an interactive menu will be shown.

Examples:
    python accessories/run_scripts.py get360frames
    python accessories/run_scripts.py get360frames --config project_config2.ini
    python accessories/run_scripts.py --config my_project.ini
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from project_config import get_config

def get_script_path(script_name, config_file="project_config.ini"):
    """Get the full path to a script in the accessories directory"""
    cfg = get_config(config_file)
    accessories_path = cfg.project_root / "accessories"
    
    script_map = {
        'get360frames': accessories_path / 'get360frames.py',
        'combinecubemap': accessories_path / 'combinecubemap_multiple_intermediates.py',
        'train': accessories_path / 'train_with_config.py'
    }
    
    return script_map.get(script_name)

def run_script(script_name, config_file="project_config.ini"):
    """Run a script by name with specified config file"""
    script_path = get_script_path(script_name, config_file)
    
    if not script_path or not script_path.exists():
        print(f"Error: Script '{script_name}' not found")
        return False
    
    print(f"Running {script_name}...")
    print(f"Script: {script_path}")
    print(f"Configuration: {config_file}")
    print()
    
    try:
        # Run the script with config file argument
        cmd = [sys.executable, str(script_path), "--config", config_file]
            
        result = subprocess.run(cmd, check=True)
        print(f"\n{script_name} completed successfully!")
        
        # Copy config file to appropriate output directories for reproducibility
        copy_config_to_outputs(script_name, config_file)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError: {script_name} failed with return code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\nError: Python executable or script not found")
        return False

def copy_config_to_outputs(script_name, config_file):
    """Copy config file to relevant output directories based on script type"""
    cfg = get_config(config_file)
    
    # Define output directories based on script type
    if script_name == "get360frames":
        # Copy to equirect and cubemap output directories
        output_dirs = [cfg.equirect_dir, cfg.cubemap_dir]
    elif script_name == "combinecubemap":
        # Copy to combined output directory
        output_dirs = [cfg.combined_dir]
    elif script_name == "train":
        # Copy to training output directory
        output_base = cfg.get_path('paths', 'output_dir')
        current_project = cfg.get_string('paths', 'current_project')
        train_subdir = cfg.get_string('paths', 'train_subdir')
        output_path = output_base / current_project / train_subdir
        output_dirs = [output_path]
    else:
        # Default: copy to project directory
        output_dirs = [cfg.current_project_dir]
    
    # Copy config to each relevant output directory
    for output_dir in output_dirs:
        try:
            cfg.copy_config_to_output(output_dir, script_name)
        except Exception as e:
            print(f"Warning: Could not copy config to {output_dir}: {e}")

def show_menu(config_file="project_config.ini"):
    """Show interactive menu for script selection"""
    cfg = get_config(config_file)
    
    print("=== Gaussian Splatting Script Launcher ===")
    print(f"Project: {cfg.project_name}")
    print(f"Root: {cfg.project_root}")
    print(f"Configuration: {config_file}")
    print()
    
    while True:
        print("Available Scripts:")
        print("1. get360frames           - Extract 360-degree frames from video")
        print("2. combinecubemap         - Combine multiple cubemap datasets")
        print("3. train                  - Train Gaussian Splatting model with config")
        print("4. Exit")
        print()
        
        choice = input("Select a script [1-4]: ").strip()
        
        if choice == "1":
            run_script("get360frames", config_file)
        elif choice == "2":
            run_script("combinecubemap", config_file)
        elif choice == "3":
            run_script("train", config_file)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Script launcher for Gaussian Splatting project",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'script_name', 
        nargs='?', 
        choices=['get360frames', 'combinecubemap', 'train'],
        help='Script to run (if not provided, interactive menu will be shown)'
    )
    parser.add_argument(
        '--config', 
        default='project_config.ini',
        help='Configuration file to use (default: project_config.ini)'
    )
    
    args = parser.parse_args()
      # Validate config file exists
    script_dir = Path(__file__).parent
    if script_dir.name == "accessories":
        project_root = script_dir.parent
    else:
        project_root = script_dir
    
    config_path = project_root / args.config
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        print(f"Available config files in {project_root}:")
        for config_file in project_root.glob("*.ini"):
            print(f"  {config_file.name}")
        sys.exit(1)
    
    if args.script_name:
        # Run specific script
        if not run_script(args.script_name, args.config):
            sys.exit(1)
    else:
        # Show interactive menu
        show_menu(args.config)

if __name__ == "__main__":
    main()
