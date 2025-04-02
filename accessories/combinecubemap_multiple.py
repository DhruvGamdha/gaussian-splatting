#!/usr/bin/env python3

import argparse
import os
import re
import shutil
from pathlib import Path

def load_config_file(config_path):
    """
    Reads a configuration text file where each non-comment line
    has the format:
        direction path/to/directory
    e.g.:
        forward /very/long/path/to/dir1
        backward /very/long/path/to/dir2
    Returns (dirs, directions) lists, preserving order.
    """
    dirs = []
    directions = []
    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip blank lines or lines beginning with '#'
            if not line or line.startswith('#'):
                continue
            
            # Each valid line: "<direction> <directory>"
            # e.g., "forward /path/dir1"
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                print(f"[WARN] Ignoring malformed config line: '{line}'")
                continue
            
            dir_direction, dir_path = parts[0], parts[1]
            dirs.append(dir_path)
            directions.append(dir_direction.lower())  # store in lower just to standardize
    return dirs, directions

def list_jpg_files_in_range(directory, start_idx, end_idx):
    """
    Lists all .jpg files in 'directory' whose filenames contain an integer N in the range [start_idx, end_idx].
    The integer is matched by finding the first group of digits in the file name (before the .jpg).
    Returns a list of (filepath, numeric_index) sorted by numeric_index ascending.
    """
    pattern = re.compile(r'(\d+)\.jpg$', re.IGNORECASE)
    
    matched_files = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.lower().endswith(".jpg"):
            match = pattern.search(entry.name)
            if match:
                number_str = match.group(1)
                try:
                    number_val = int(number_str)
                except ValueError:
                    continue

                if start_idx <= number_val <= end_idx:
                    matched_files.append((entry.path, number_val))

    # Sort ascending by numeric index
    matched_files.sort(key=lambda x: x[1])
    return matched_files

def combine_multi_datasets(
    dirs,
    directions,
    start_idx,
    end_idx,
    out_dir
):
    """
    Combines frames from multiple cubemap/image folders in a specified order.
    Each folder is appended in either forward (ascending) or backward (descending) order.
    All frames are renamed starting from 1 in the output dataset.
    
    :param dirs: List of input directory paths.
    :param directions: Corresponding list of "forward" or "backward" for each dir in 'dirs'.
    :param start_idx: Start image index for each dataset subset (same for all).
    :param end_idx: End image index for each dataset subset (same for all).
    :param out_dir: Path to the output directory.
    """

    if len(dirs) != len(directions):
        raise ValueError("The number of directories must match the number of directions.")

    # Create main output directory if needed
    os.makedirs(out_dir, exist_ok=True)

    # Create subdirectory for the combined frames
    out_inp_dir = os.path.join(out_dir, "input")
    os.makedirs(out_inp_dir, exist_ok=True)

    # Write parameters to a file
    params_file = os.path.join(out_dir, "parameters.txt")
    with open(params_file, "w") as f:
        f.write("=== COMBINE MULTI DATASETS PARAMETERS ===\n")
        f.write(f"start_idx: {start_idx}\n")
        f.write(f"end_idx: {end_idx}\n")
        f.write(f"out_dir: {out_dir}\n")
        f.write("Directories:\n")
        for d, dr in zip(dirs, directions):
            f.write(f"  - {d} (direction: {dr})\n")

    current_index = 1  # Used for naming output frames

    # Process each directory in the given order
    for dir_path, dir_direction in zip(dirs, directions):
        # Gather files in ascending numeric order
        files_in_range = list_jpg_files_in_range(dir_path, start_idx, end_idx)

        if not files_in_range:
            print(f"[WARN] No matching .jpg files found in {dir_path} within [{start_idx}, {end_idx}].")
            continue

        # Reverse if direction is 'backward'
        if dir_direction == 'backward':
            files_in_range.reverse()
        elif dir_direction != 'forward':
            print(f"[WARN] Unknown direction '{dir_direction}' for {dir_path}. "
                  f"Using 'forward' by default.")

        # Copy files to the output directory with new naming
        for filepath, number_val in files_in_range:
            out_name = f"{current_index:05d}.jpg"
            dest_path = os.path.join(out_inp_dir, out_name)
            shutil.copy2(filepath, dest_path)
            current_index += 1

    num_copied = current_index - 1
    print(f"Done! Combined dataset written to: {out_inp_dir}")
    print(f"Number of frames in the final dataset: {num_copied}")
    print(f"Parameters saved to: {params_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Combine multiple cubemap/image datasets in a specified order/direction. "
                    "Reads a config file with lines: '<direction> <full/path/to/directory>'."
    )
    parser.add_argument("--config", required=True,
                        help="Path to the configuration text file.")
    parser.add_argument("--start_idx", type=int, required=True,
                        help="Start index for each dataset subset.")
    parser.add_argument("--end_idx", type=int, required=True,
                        help="End index for each dataset subset.")
    parser.add_argument("--out_dir", required=True,
                        help="Path to the output folder.")
    args = parser.parse_args()

    # 1. Load directories & directions from config file
    dirs, directions = load_config_file(args.config)

    # 2. Combine them
    combine_multi_datasets(
        dirs=dirs,
        directions=directions,
        start_idx=args.start_idx,
        end_idx=args.end_idx,
        out_dir=args.out_dir
    )

if __name__ == "__main__":
    main()
