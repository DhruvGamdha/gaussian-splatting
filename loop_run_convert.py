#!/usr/bin/env python3
"""
Retry COLMAP Reconstruction Script
Repeatedly runs convert.py until reconstruction quality threshold is met.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime
import struct

def count_reconstructed_images(source_path):
    """Count the number of images in the reconstruction output."""
    images_dir = Path(source_path) / "images"
    if not images_dir.exists():
        return 0
    
    # Count only .jpg files (COLMAP outputs lowercase .jpg)
    image_files = list(images_dir.glob("*.jpg"))
    return len(image_files)

def count_reconstruction_points(source_path):
    """Count the number of 3D points in the sparse reconstruction."""
    # Check for binary format first
    points_bin = Path(source_path) / "sparse" / "0" / "points3D.bin"
    if points_bin.exists():
        return count_points_binary(points_bin)
    
    # Check for text format
    points_txt = Path(source_path) / "sparse" / "0" / "points3D.txt"
    if points_txt.exists():
        return count_points_text(points_txt)
    
    return 0

def count_points_binary(points_file):
    """Count points from binary COLMAP format."""
    try:
        with open(points_file, 'rb') as f:
            num_points = struct.unpack('Q', f.read(8))[0]
            return num_points
    except Exception as e:
        print(f"  Warning: Could not read binary points file: {e}")
        return 0

def count_points_text(points_file):
    """Count points from text COLMAP format."""
    try:
        with open(points_file, 'r') as f:
            count = 0
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    count += 1
            return count
    except Exception as e:
        print(f"  Warning: Could not read text points file: {e}")
        return 0

def cleanup_reconstruction_outputs(source_path):
    """Delete all reconstruction outputs except input folder, parameters.txt, and config files."""
    source_path = Path(source_path)
    
    # List of items to preserve
    preserve_exact = ['input', 'parameters.txt']
    
    # Get all items in source_path
    for item in source_path.iterdir():
        # Preserve exact matches
        if item.name in preserve_exact:
            continue
        
        # Preserve config files (any .ini file starting with 'config')
        if item.name.startswith('config') and item.name.endswith('.ini'):
            print(f"  Preserving config: {item.name}")
            continue
        
        # Delete everything else
        try:
            if item.is_dir():
                shutil.rmtree(item)
                print(f"  Deleted directory: {item.name}")
            else:
                item.unlink()
                print(f"  Deleted file: {item.name}")
        except Exception as e:
            print(f"  Warning: Could not delete {item.name}: {e}")

def run_convert(source_path, convert_args=""):
    """Run convert.py with the given source path."""
    cmd = f"python convert.py -s {source_path} {convert_args}".strip()
    print(f"\nRunning: {cmd}")
    print("=" * 80)
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def log_result(log_file, attempt, num_images, num_points, threshold, elapsed_time, source_path):
    """Append reconstruction result to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if num_images >= threshold else "RETRY"
    
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} | Attempt {attempt} | Images: {num_images} | Points: {num_points} | Threshold: {threshold} | Status: {status} | Time: {elapsed_time:.1f}s | Path: {source_path}\n")

def main():
    print("=" * 80)
    print("COLMAP Reconstruction Retry Script")
    print("=" * 80)
    
    # Get user inputs
    source_path = input("\nEnter source path (e.g., data/360vid2stl/.../4_cubemap_combined): ").strip()
    
    if not os.path.exists(source_path):
        print(f"Error: Source path '{source_path}' does not exist!")
        sys.exit(1)
    
    threshold = int(input("Enter minimum number of reconstructed images required: ").strip())
    max_attempts = int(input("Enter maximum number of attempts (default 10): ").strip() or "10")
    
    # Get convert.py arguments
    convert_args = input("Enter convert.py arguments (e.g., --no_gpu, --camera SIMPLE_RADIAL --no_gpu): ").strip()
    
    # Get log file path
    default_log = "colmap_reconstruction.log"
    log_file = input(f"Enter log file path (default: {default_log}): ").strip() or default_log
    
    print("\n" + "=" * 80)
    print(f"Configuration:")
    print(f"  Source Path: {source_path}")
    print(f"  Threshold: {threshold} images")
    print(f"  Max Attempts: {max_attempts}")
    print(f"  Convert Args: {convert_args if convert_args else '(none)'}")
    print(f"  Log File: {log_file}")
    print("=" * 80)
    
    # Track results
    attempt_results = []
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n{'=' * 80}")
        print(f"ATTEMPT {attempt}/{max_attempts}")
        print(f"{'=' * 80}")
        
        # Run convert.py
        start_time = time.time()
        exit_code = run_convert(source_path, convert_args)
        elapsed_time = time.time() - start_time
        
        if exit_code != 0:
            print(f"\n⚠️  Warning: convert.py exited with code {exit_code}")
        
        # Count reconstructed images and points
        num_images = count_reconstructed_images(source_path)
        num_points = count_reconstruction_points(source_path)
        attempt_results.append((num_images, num_points))
        
        # Log the result
        log_result(log_file, attempt, num_images, num_points, threshold, elapsed_time, source_path)
        
        print(f"\n{'=' * 80}")
        print(f"ATTEMPT {attempt} RESULTS:")
        print(f"  Reconstructed Images: {num_images}")
        print(f"  Reconstructed Points: {num_points}")
        print(f"  Threshold: {threshold}")
        print(f"  Time Elapsed: {elapsed_time:.1f} seconds")
        print(f"  Logged to: {log_file}")
        print(f"{'=' * 80}")
        
        # Check if threshold met
        if num_images >= threshold:
            print(f"\n✅ SUCCESS! Reconstruction meets threshold ({num_images} >= {threshold})")
            print(f"\nAttempt History:")
            for i, (imgs, pts) in enumerate(attempt_results, 1):
                print(f"  Attempt {i}: {imgs} images, {pts} points")
            print(f"Total Attempts: {attempt}")
            break
        else:
            print(f"\n❌ Below threshold ({num_images} < {threshold})")
            
            if attempt < max_attempts:
                print(f"\nCleaning up and retrying...")
                cleanup_reconstruction_outputs(source_path)
                print(f"Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                print(f"\n⚠️  Maximum attempts ({max_attempts}) reached!")
                print(f"\nAttempt History:")
                for i, (imgs, pts) in enumerate(attempt_results, 1):
                    print(f"  Attempt {i}: {imgs} images, {pts} points")
                
                best_idx = max(range(len(attempt_results)), key=lambda i: attempt_results[i][0])
                best_imgs, best_pts = attempt_results[best_idx]
                print(f"\nBest Result: {best_imgs} images, {best_pts} points (Attempt {best_idx + 1})")
                print(f"\nConsider:")
                print(f"  - Reducing skip_frames in config")
                print(f"  - Reducing num_intermediate in config")
                print(f"  - Using a different cubemap face or dataset")
    
    print(f"\n{'=' * 80}")
    print("Script Complete")
    print(f"Results logged to: {log_file}")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)