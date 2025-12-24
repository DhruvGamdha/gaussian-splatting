#!/usr/bin/env python3
"""
This script combines multiple cubemap frame datasets into one sequential dataset.
Each input cubemap dataset is specified via the project_config.ini file.
The script also uses the original equirectangular frames (from a given directory)
to generate intermediate perspective views at transitions between datasets when the
cubemap view changes. The intermediate views are produced via spherical linear
interpolation (slerp) between the two target view directions.
All output frames are renumbered sequentially starting from 00001.jpg,
and a parameters.txt file is written to record all input parameters.

All parameters are read from project_config.ini - no command-line arguments needed.
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from project_config import get_config

import cv2
import numpy as np

# --------------------- Utility Functions --------------------- #

def load_config_entries(config_file="project_config.ini"):
    """
    Load cubemap direction entries from project_config.ini
    This replaces the old load_config_file function that read from .cfg files
    
    Args:
        config_file: Configuration file to use
    
    Returns a list of tuples: (direction, view, directory) preserving order.
    """
    cfg = get_config(config_file)
    entries = cfg.get_cubemap_directions()
    
    # Validate that directories exist
    validated_entries = []
    for direction, view, directory in entries:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"[WARN] Directory does not exist: {directory}")
            continue
        validated_entries.append((direction, view, directory))
    
    return validated_entries

def get_all_jpg_files(directory):
    """
    Lists all .jpg files in 'directory'.
    Returns a list of tuples: (filepath, numeric_index) sorted by numeric_index ascending.
    If filename doesn't contain a number, it's skipped.
    """
    pattern = re.compile(r'(\d+)\.jpg$', re.IGNORECASE)
    matched_files = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.lower().endswith(".jpg"):
            match = pattern.search(entry.name)
            if match:
                try:
                    number_val = int(match.group(1))
                except ValueError:
                    continue
                matched_files.append((entry.path, number_val))
    matched_files.sort(key=lambda x: x[1])
    return matched_files

def list_jpg_files_in_range(directory, start_idx, end_idx):
    """
    Lists all .jpg files in 'directory' whose filenames contain an integer N in the range [start_idx, end_idx].
    If start_idx == -1 and end_idx == -1, returns all .jpg files.
    The integer is matched by finding the first group of digits in the filename (before ".jpg").
    Returns a list of tuples: (filepath, numeric_index) sorted by numeric_index ascending.
    """
    # If both are -1, get all files
    if start_idx == -1 and end_idx == -1:
        return get_all_jpg_files(directory)
    
    pattern = re.compile(r'(\d+)\.jpg$', re.IGNORECASE)
    matched_files = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.lower().endswith(".jpg"):
            match = pattern.search(entry.name)
            if match:
                try:
                    number_val = int(match.group(1))
                except ValueError:
                    continue
                if start_idx <= number_val <= end_idx:
                    matched_files.append((entry.path, number_val))
    matched_files.sort(key=lambda x: x[1])
    return matched_files

def build_equirect_dict(equirect_dir, start_idx, end_idx):
    """
    Builds a dictionary mapping the numeric index to the file path for .jpg files in the equirectangular directory.
    If start_idx == -1 and end_idx == -1, includes all .jpg files.
    """
    files = list_jpg_files_in_range(equirect_dir, start_idx, end_idx)
    return {num: path for (path, num) in files}

def slerp(v0, v1, t):
    """
    Spherical linear interpolation (slerp) between two unit vectors.
    """
    dot = np.clip(np.dot(v0, v1), -1.0, 1.0)
    omega = np.arccos(dot)
    if np.abs(omega) < 1e-10:
        return v0
    so = np.sin(omega)
    return (np.sin((1.0 - t) * omega) / so) * v0 + (np.sin(t * omega) / so) * v1

def sample_perspective_from_equirect(equirect_img, vfov=90, yaw=0, pitch=0, out_size=512):
    """
    Samples a pinhole-perspective view from an equirectangular (360°) image.
    
    :param equirect_img: Input equirectangular image (H x W x 3).
    :param vfov: Vertical field of view in degrees.
    :param yaw: Yaw angle in degrees.
    :param pitch: Pitch angle in degrees.
    :param out_size: Output square image size (pixels).
    :return: perspective_view (out_size x out_size x 3) image.
    """
    h, w, _ = equirect_img.shape
    out = np.zeros((out_size, out_size, 3), dtype=np.uint8)
    
    yaw_rad = np.deg2rad(yaw)
    pitch_rad = np.deg2rad(pitch)
    hfov_rad = np.deg2rad(vfov)  # For a square output, horizontal FOV equals vertical FOV
    vfov_rad = np.deg2rad(vfov)  # For a square output, vertical FOV equals horizontal FOV
    
    for y in range(out_size):
        for x in range(out_size):
            nx = (2.0 * x / out_size) - 1.0  # in [-1,1]
            ny = (2.0 * y / out_size) - 1.0  # in [-1,1]
            tx = np.tan(hfov_rad / 2) * nx
            ty = np.tan(vfov_rad / 2) * ny
            # Initial vector in camera space: assume forward is +Z.
            vec = np.array([tx, -ty, 1.0])
            vec = vec / np.linalg.norm(vec)
            # Apply pitch rotation (around X-axis)
            c_p = np.cos(pitch_rad)
            s_p = np.sin(pitch_rad)
            rot_x = np.array([[1,      0,     0],
                              [0,    c_p,  -s_p],
                              [0,    s_p,   c_p]])
            vec = rot_x.dot(vec)
            # Apply yaw rotation (around Y-axis)
            c_y = np.cos(yaw_rad)
            s_y = np.sin(yaw_rad)
            rot_y = np.array([[c_y, 0, s_y],
                              [0,   1,   0],
                              [-s_y,0, c_y]])
            vec = rot_y.dot(vec)
            x_3d, y_3d, z_3d = vec
            longitude = np.arctan2(z_3d, x_3d)
            latitude = np.arcsin(y_3d)
            x_eq = (longitude + np.pi) / (2.0 * np.pi) * w
            y_eq = (np.pi / 2 - latitude) / np.pi * h
            x_eq = int(np.clip(x_eq, 0, w - 1))
            y_eq = int(np.clip(y_eq, 0, h - 1))
            out[y, x] = equirect_img[y_eq, x_eq]
    return out

def generate_perspective_view(equirect_img, target_direction, vfov=90, out_size=512):
    """
    Generates a perspective view from an equirectangular image for a desired unit direction vector.
    Converts the unit vector into yaw and pitch angles and samples the equirectangular image.
    
    :param equirect_img: Input equirectangular image.
    :param target_direction: Desired view direction as a unit vector [x, y, z].
    :param vfov: Field of view in degrees.
    :param out_size: Output image size (square).
    :return: A perspective view image.
    """
    # Compute yaw and pitch. Here, we assume:
    #   yaw = arctan2(x, z)
    #   pitch = arcsin(y)
    x, y, z = target_direction
    yaw = np.degrees(np.arctan2(x, z))
    pitch = np.degrees(np.arcsin(y))
    return sample_perspective_from_equirect(equirect_img, vfov=vfov, yaw=yaw, pitch=pitch, out_size=out_size)

# Mapping from cubemap view names to unit direction vectors
view_to_vector = {
    "posx": np.array([1, 0, 0]),
    "negx": np.array([-1, 0, 0]),
    "posy": np.array([0, 1, 0]),
    "negy": np.array([0, -1, 0]),
    "posz": np.array([0, 0, 1]),
    "negz": np.array([0, 0, -1])
}

# --------------------- Main Combination Function --------------------- #

def combine_datasets_with_intermediates(config_entries, equirect_dir, start_idx, end_idx,
                                          num_intermediate, vfov, out_size, out_dir):
    """
    Processes multiple cubemap datasets (each with a direction, view name, and directory)
    and combines them into one dataset, inserting intermediate views (generated from 
    equirectangular frames) at transitions where the cubemap view changes.
    
    :param config_entries: List of tuples (direction, view, directory) for cubemap datasets.
    :param equirect_dir: Path to directory containing the original 360° equirectangular frames.
    :param start_idx: Start index for frame selection (common to all). Use -1 for all frames.
    :param end_idx: End index for frame selection. Use -1 for all frames.
    :param num_intermediate: Number of intermediate frames to generate at each transition.
    :param vfov: Field-of-view (in degrees) for perspective sampling.
    :param out_size: Output image size (square).
    :param out_dir: Output directory path.
    """
    os.makedirs(out_dir, exist_ok=True)
    # Create subdirectory "input" to store combined frames
    out_inp_dir = os.path.join(out_dir, "input")
    os.makedirs(out_inp_dir, exist_ok=True)
    
    # Determine range description for parameters file
    if start_idx == -1 and end_idx == -1:
        range_desc = "all frames"
    else:
        range_desc = f"{start_idx} to {end_idx}"
    
    # Write all parameters to a file for reproducibility.
    params_file = os.path.join(out_dir, "parameters.txt")
    with open(params_file, "w") as f:
        f.write("=== COMBINE DATASETS WITH INTERMEDIATES PARAMETERS ===\n")
        f.write(f"equirect_dir: {equirect_dir}\n")
        f.write(f"start_idx: {start_idx}\n")
        f.write(f"end_idx: {end_idx}\n")
        f.write(f"frame_range: {range_desc}\n")
        f.write(f"num_intermediate: {num_intermediate}\n")
        f.write(f"vfov: {vfov}\n")
        f.write(f"out_size: {out_size}\n")
        f.write(f"out_dir: {out_dir}\n")
        f.write("Cubemap datasets:\n")
        for direction, view, directory in config_entries:
            f.write(f"  - {directory} (direction: {direction}, view: {view})\n")
    
    # Build a dictionary for the equirectangular frames (key: numeric index)
    equirect_dict = build_equirect_dict(equirect_dir, start_idx, end_idx)
    
    current_index = 1  # For output naming (e.g., 00001.jpg)
    num_entries = len(config_entries)
    
    # Loop over each cubemap dataset in order.
    # For each one, list its images (by numeric order, reversed if direction=="backward").
    for i, (direction, view, cubemap_dir) in enumerate(config_entries):
        # List matching files from current cubemap directory.
        files = list_jpg_files_in_range(cubemap_dir, start_idx, end_idx)
        if not files:
            if start_idx == -1 and end_idx == -1:
                print(f"[WARN] No .jpg files found in {cubemap_dir}.")
            else:
                print(f"[WARN] No matching .jpg files found in {cubemap_dir} for indices [{start_idx}, {end_idx}].")
            continue
        
        # Reverse ordering if direction is "backward"
        if direction == "backward":
            files = list(reversed(files))
        elif direction != "forward":
            print(f"[WARN] Unknown direction '{direction}' for {cubemap_dir}; using 'forward' ordering.")
        
        # Copy the files to output.
        last_numeric = None
        for filepath, num_val in files:
            out_name = f"{current_index:05d}.jpg"
            dest_path = os.path.join(out_inp_dir, out_name)
            shutil.copy2(filepath, dest_path)
            current_index += 1
            last_numeric = num_val  # keep track of the boundary frame's numeric index
        
        # If there is a next dataset and the view changes, insert intermediate frames.
        if i < num_entries - 1:
            next_direction, next_view, next_dir = config_entries[i + 1]
            if view != next_view:
                if last_numeric is None or last_numeric not in equirect_dict:
                    print(f"[WARN] Boundary index {last_numeric} not found in equirectangular directory; skipping intermediate views.")
                else:
                    equirect_path = equirect_dict[last_numeric]
                    equirect_img = cv2.imread(equirect_path)
                    if equirect_img is None:
                        print(f"[WARN] Could not load equirectangular image: {equirect_path}")
                    else:
                        # Retrieve the unit vectors for the current and next cubemap views.
                        v_current = view_to_vector.get(view)
                        v_next = view_to_vector.get(next_view)
                        if v_current is None or v_next is None:
                            print(f"[WARN] Unknown view names: {view} or {next_view}; cannot generate intermediate views.")
                        else:
                            # Generate intermediate frames in ascending order (from t=1/(N+1) to t=N/(N+1))
                            for j in range(1, num_intermediate + 1):
                                t = j / (num_intermediate + 1)
                                interp_vec = slerp(v_current, v_next, t)
                                inter_img = generate_perspective_view(equirect_img, interp_vec, vfov=vfov, out_size=out_size)
                                out_name = f"{current_index:05d}.jpg"
                                dest_path = os.path.join(out_inp_dir, out_name)
                                cv2.imwrite(dest_path, inter_img)
                                print(f"Generated intermediate frame {out_name} at t={t:.2f}")
                                current_index += 1
    
    num_copied = current_index - 1
    print(f"Done! Combined dataset written to: {out_inp_dir}")
    print(f"Number of frames in the final dataset: {num_copied}")
    print(f"Parameters saved to: {params_file}")

# --------------------- Main Entry Point --------------------- #

def main(config_file="project_config.ini"):
    """
    Main function that reads all parameters from project_config.ini and runs the combination process.
    
    Args:
        config_file: Configuration file to use (default: project_config.ini)
    """
    # Load all configuration from specified config file
    cfg = get_config(config_file)
    
    # Get general parameters from config
    equirect_dir = cfg.equirect_dir
    
    # Get cubemap parameters
    cubemap_params = cfg.cubemap_params
    start_idx = cubemap_params['start_idx']
    end_idx = cubemap_params['end_idx']
    num_intermediate = cubemap_params['num_intermediate']
    vfov = cubemap_params['vfov']
    out_size = cubemap_params['out_size']
    
    # Get output directory
    out_dir = cfg.combined_dir
    
    # Load configuration entries (cubemap directions)
    config_entries = load_config_entries(config_file)
    if not config_entries:
        print(f"No valid cubemap configuration entries found in {config_file}. Exiting.")
        return
    
    # Determine range description for console output
    if start_idx == -1 and end_idx == -1:
        range_desc = "all available frames"
    else:
        range_desc = f"{start_idx} to {end_idx}"
    
    print(f"Configuration loaded from {config_file}:")
    print(f"  Equirectangular directory: {equirect_dir}")
    print(f"  Frame range: {range_desc}")
    print(f"  Intermediate frames: {num_intermediate}")
    print(f"  Field of view: {vfov}°")
    print(f"  Output size: {out_size}px")
    print(f"  Output directory: {out_dir}")
    print(f"  Cubemap entries: {len(config_entries)}")
    print()
    
    combine_datasets_with_intermediates(config_entries, str(equirect_dir),
                                          start_idx, end_idx,
                                          num_intermediate, vfov, out_size,
                                          str(out_dir))

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Combine multiple cubemap datasets with intermediate views")
    parser.add_argument('--config', default='project_config.ini', help='Configuration file to use')
    args = parser.parse_args()
    
    main(args.config)