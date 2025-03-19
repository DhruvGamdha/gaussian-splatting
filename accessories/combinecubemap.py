#!/usr/bin/env python3

import argparse
import os
import re
import shutil
from pathlib import Path

def list_jpg_files_in_range(directory, start_idx, end_idx):
    """
    Lists all .jpg files in 'directory' whose filenames contain an integer N in the range [start_idx, end_idx].
    The integer is matched by finding the first group of digits in the file name (before the .jpg).
    Returns a list of (filepath, numeric_index) sorted by numeric_index ascending.
    """
    # Regex to capture digits before .jpg (e.g., 123456 in "123456.jpg" or "image_123456.jpg")
    pattern = re.compile(r'(\d+)\.jpg$', re.IGNORECASE)
    
    matched_files = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.lower().endswith(".jpg"):
            match = pattern.search(entry.name)
            if match:
                number_str = match.group(1)
                # Safely parse integer
                try:
                    number_val = int(number_str)
                except ValueError:
                    continue

                if start_idx <= number_val <= end_idx:
                    matched_files.append((entry.path, number_val))

    # Sort ascending by the numeric index
    matched_files.sort(key=lambda x: x[1])
    return matched_files

def combine_datasets(
    forward_dir: str,
    backward_dir: str,
    forward_start: int,
    forward_end: int,
    backward_start: int,
    backward_end: int,
    out_dir: str
):
    """
    Combines frames from two cubemap folders (forward and backward) into a new dataset,
    where the forward subset is in ascending numeric order, and the backward subset is in descending numeric order.
    The result is saved in out_dir, with images numbered starting from 1.
    Also writes a 'parameters.txt' file containing the user-specified parameters.
    """

    # Create output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)

    # Store user parameters in a text file for reference
    params_file = os.path.join(out_dir, "parameters.txt")
    with open(params_file, "w") as f:
        f.write("=== COMBINE DATASETS PARAMETERS ===\n")
        f.write(f"forward_dir: {forward_dir}\n")
        f.write(f"backward_dir: {backward_dir}\n")
        f.write(f"forward_start: {forward_start}\n")
        f.write(f"forward_end: {forward_end}\n")
        f.write(f"backward_start: {backward_start}\n")
        f.write(f"backward_end: {backward_end}\n")
        f.write(f"out_dir: {out_dir}\n")

    # 1) Gather forward subset
    forward_files = list_jpg_files_in_range(forward_dir, forward_start, forward_end)
    # forward_files is a list of (filepath, numeric_index), sorted ascending

    # 2) Gather backward subset
    backward_files = list_jpg_files_in_range(backward_dir, backward_start, backward_end)
    # We'll want to process them in descending order eventually

    current_index = 1  # This will be used for naming the combined output frames

    # Copy forward subset in ascending order
    for filepath, number_val in forward_files:
        out_name = f"{current_index:05d}.jpg"
        dest_path = os.path.join(out_dir, out_name)
        shutil.copy2(filepath, dest_path)
        current_index += 1

    # Copy backward subset in descending order
    for filepath, number_val in reversed(backward_files):
        out_name = f"{current_index:05d}.jpg"
        dest_path = os.path.join(out_dir, out_name)
        shutil.copy2(filepath, dest_path)
        current_index += 1

    num_copied = current_index - 1
    print(f"Done! Combined dataset written to: {out_dir}")
    print(f"Number of frames in the final dataset: {num_copied}")
    print(f"Parameters saved to: {params_file}")

def main():
    parser = argparse.ArgumentParser(description="Combine two cubemap subsets (forward/backward) into one dataset.")
    parser.add_argument("--forward_dir", required=True, help="Path to the forward dataset folder.")
    parser.add_argument("--backward_dir", required=True, help="Path to the backward dataset folder.")
    parser.add_argument("--forward_start", type=int, required=True, help="Start index for forward dataset subset.")
    parser.add_argument("--forward_end", type=int, required=True, help="End index for forward dataset subset.")
    parser.add_argument("--backward_start", type=int, required=True, help="Start index for backward dataset subset.")
    parser.add_argument("--backward_end", type=int, required=True, help="End index for backward dataset subset.")
    parser.add_argument("--out_dir", required=True, help="Path to the output folder.")
    args = parser.parse_args()

    combine_datasets(
        args.forward_dir,
        args.backward_dir,
        args.forward_start,
        args.forward_end,
        args.backward_start,
        args.backward_end,
        args.out_dir
    )

if __name__ == "__main__":
    main()
