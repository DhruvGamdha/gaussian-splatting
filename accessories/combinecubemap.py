#!/usr/bin/env python3

import argparse
import os
import shutil
from pathlib import Path

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
    where the forward subset is in ascending order, and the backward subset is in descending order.
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

    current_index = 1  # This will be used for naming the combined output frames
    
    # 1) Copy forward subset in ascending order
    for i in range(forward_start, forward_end + 1):
        # Construct the file name in forward_dir
        # e.g., if frames are named "00001.jpg", "00002.jpg", etc.
        # We'll match that naming. If your files are zero-padded to 5 digits, do that:
        forward_file_name = f"{i:05d}.jpg"
        source_path = os.path.join(forward_dir, forward_file_name)
        if not os.path.isfile(source_path):
            print(f"[WARN] Forward file not found: {source_path}. Skipping.")
            continue
        
        # Construct the destination path with new index
        out_name = f"{current_index:05d}.jpg"
        dest_path = os.path.join(out_dir, out_name)
        
        shutil.copy2(source_path, dest_path)
        current_index += 1

    # 2) Copy backward subset in descending order
    for i in range(backward_end, backward_start - 1, -1):
        # Construct the file name in backward_dir
        backward_file_name = f"{i:05d}.jpg"
        source_path = os.path.join(backward_dir, backward_file_name)
        if not os.path.isfile(source_path):
            print(f"[WARN] Backward file not found: {source_path}. Skipping.")
            continue
        
        # Construct the destination path with new index
        out_name = f"{current_index:05d}.jpg"
        dest_path = os.path.join(out_dir, out_name)
        
        shutil.copy2(source_path, dest_path)
        current_index += 1

    print(f"Done! Combined dataset written to: {out_dir}")
    print(f"Number of frames in the final dataset: {current_index - 1}")
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
