#!/usr/bin/env python3
"""
Config-Aware Training Script Launcher - Gaussian Splatting
==========================================================
This script bridges the gap between the unified config system and existing training scripts.
It reads parameters from project_config.ini and launches train.py with the appropriate arguments.

Usage:
    python accessories/train_with_config.py [--config CONFIG_FILE] [--source-path SOURCE] [--model-path OUTPUT]

Examples:
    python accessories/train_with_config.py
    python accessories/train_with_config.py --config project_config2.ini
    python accessories/train_with_config.py --source-path data/my_scene --model-path output/my_model
"""

import sys
import argparse
import subprocess
from pathlib import Path
from project_config import get_config

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Config-aware Gaussian Splatting training launcher")
    parser.add_argument('--config', default='project_config.ini', help='Configuration file to use')
    parser.add_argument('--source-path', help='Path to COLMAP scene data (overrides config)')
    parser.add_argument('--model-path', help='Output model path (overrides config)')
    parser.add_argument('--dry-run', action='store_true', help='Show command without running')
    
    args = parser.parse_args()
    
    # Load configuration
    cfg = get_config(args.config)
    
    # Get optimization parameters from config
    gs_params = cfg.gaussian_splatting_params
    
    # Build command arguments for train.py
    cmd = [sys.executable, 'train.py']
      # Add source path
    if args.source_path:
        cmd.extend(['--source_path', args.source_path])
    else:
        # Use training dataset directory from config (user-selected dataset)
        cmd.extend(['--source_path', str(cfg.train_dir)])
      
    # Add model output path
    if args.model_path:
        cmd.extend(['--model_path', args.model_path])
    else:
        # Use output directory from config with same structure as training source path
        output_base = cfg.get_path('paths', 'output_dir')
        current_project = cfg.get_string('paths', 'current_project')
        train_subdir = cfg.get_string('paths', 'train_subdir')
        output_path = output_base / current_project / train_subdir
        cmd.extend(['--model_path', str(output_path)])
      # Add optimization parameters from config
    cmd.extend([
        '--iterations', str(gs_params['iterations']),
        '--position_lr_init', str(gs_params['position_lr_init']),
        '--position_lr_final', str(gs_params['position_lr_final']),
        '--feature_lr', str(gs_params['feature_lr']),
        '--opacity_lr', str(gs_params['opacity_lr']),
        '--scaling_lr', str(gs_params['scaling_lr']),
        '--rotation_lr', str(gs_params['rotation_lr']),
    ])
    
    # Add densification parameters from config
    cmd.extend([
        '--percent_dense', str(gs_params['percent_dense']),
        '--densification_interval', str(gs_params['densification_interval']),
        '--opacity_reset_interval', str(gs_params['opacity_reset_interval']),
        '--densify_from_iter', str(gs_params['densify_from_iter']),
        '--densify_until_iter', str(gs_params['densify_until_iter']),
        '--densify_grad_threshold', str(gs_params['densify_grad_threshold']),
        '--lambda_dssim', str(gs_params['lambda_dssim']),
    ])
    
    # Add iteration checkpoints
    save_iterations = cfg.get_iterations_list('save_iterations')
    test_iterations = cfg.get_iterations_list('test_iterations')
    checkpoint_iterations = cfg.get_iterations_list('checkpoint_iterations')
    
    cmd.extend(['--save_iterations'] + [str(x) for x in save_iterations])
    cmd.extend(['--test_iterations'] + [str(x) for x in test_iterations])
    cmd.extend(['--checkpoint_iterations'] + [str(x) for x in checkpoint_iterations])    # Print configuration summary
    print("=== Config-Aware Training Launcher ===")
    print(f"Configuration: {args.config}")
    print(f"Project: {cfg.project_name}")
    print(f"Training Dataset: {cfg.get_string('paths', 'train_subdir')}")
    print(f"Source: {cmd[cmd.index('--source_path') + 1]}")
    print(f"Output: {cmd[cmd.index('--model_path') + 1]}")
    print(f"Iterations: {gs_params['iterations']}")
    print(f"Save checkpoints: {save_iterations}")
    print(f"Densification: {gs_params['densify_from_iter']}-{gs_params['densify_until_iter']} (interval: {gs_params['densification_interval']})")
    print(f"Learning rates: pos={gs_params['position_lr_init']}, feature={gs_params['feature_lr']}")
    print()
    
    if args.dry_run:
        print("Command that would be executed:")
        print(" ".join(cmd))
        return
    
    # Execute the training command
    print("Starting training with config parameters...")
    try:
        result = subprocess.run(cmd, check=True)
        print("\\nTraining completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\\nTraining failed with return code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("\\nError: train.py not found. Make sure you're running from the project root.")
        sys.exit(1)

if __name__ == "__main__":
    main()
