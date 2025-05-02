#!/usr/bin/env python3
# Copyright (C) 2023, Inria – GRAPHDECO
# Updated: export COLMAP model in ASCII (.txt) instead of binary (.bin)

import os
import shutil
import logging
import subprocess as sp
from argparse import ArgumentParser

def run(cmd: str):
    """Run `cmd`; raise RuntimeError on non-zero exit"""
    print("[CMD]", cmd)
    result = sp.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}):\n{cmd}")

# ────────────────────────────────────────────────────────────────────────────────
parser = ArgumentParser("Colmap converter (ASCII output)")
parser.add_argument("--no_gpu", action="store_true")
parser.add_argument("--skip_matching", action="store_true")
parser.add_argument("--camera", default="OPENCV")
parser.add_argument("--source_path", "-s", required=True)
parser.add_argument("--colmap_executable", default="")
parser.add_argument("--resize", action="store_true")
parser.add_argument("--magick_executable", default="")
args = parser.parse_args()

colmap = f'"{args.colmap_executable}"' if args.colmap_executable else "colmap"
magick = f'"{args.magick_executable}"' if args.magick_executable else "magick"
use_gpu = 0 if args.no_gpu else 1
src      = os.path.abspath(args.source_path)

# folders ----------------------------------------------------------------------
dist_sparse = f"{src}/distorted/sparse"
os.makedirs(dist_sparse, exist_ok=True)

# ────────────────────────────────── COLMAP ────────────────────────────────────
if not args.skip_matching:
    # 1. Feature extraction
    run(f"{colmap} feature_extractor "
        f"--database_path {src}/distorted/database.db "
        f"--image_path {src}/input "
        f"--ImageReader.single_camera 1 "
        f"--ImageReader.camera_model {args.camera} "
        f"--SiftExtraction.use_gpu {use_gpu}")

    # 2. Feature matching
    run(f"{colmap} exhaustive_matcher "
        f"--database_path {src}/distorted/database.db "
        f"--SiftMatching.use_gpu {use_gpu}")

    # 3. Mapping / bundle adjustment
    run(f"{colmap} mapper "
        f"--database_path {src}/distorted/database.db "
        f"--image_path {src}/input "
        f"--output_path {dist_sparse} "
        f"--Mapper.ba_global_function_tolerance=1e-6")

# 4. Image undistortion (pinhole intrinsics)
run(f"{colmap} image_undistorter "
    f"--image_path {src}/input "
    f"--input_path {dist_sparse}/0 "
    f"--output_path {src} "
    f"--output_type COLMAP")

# 5. Move undistorted sparse model into  sparse/0  (colmap writes beside /sparse)
os.makedirs(f"{src}/sparse/0", exist_ok=True)
for f in os.listdir(f"{src}/sparse"):
    if f == "0":                           # keep sub-folder itself
        continue
    shutil.move(f"{src}/sparse/{f}", f"{src}/sparse/0/{f}")

# 6. ── NEW ──  Convert binary ⇢ ASCII and clean binaries
print("\n[INFO] Converting sparse model to ASCII (.txt)")
run(f"{colmap} model_converter "
    f"--input_path  {src}/sparse/0 "
    f"--output_path {src}/sparse/0 "
    f"--output_type TXT")

# remove the old .bin files (optional – comment out if you prefer to keep them)
for fn in ("cameras.bin", "images.bin", "points3D.bin"):
    bin_path = f"{src}/sparse/0/{fn}"
    if os.path.exists(bin_path):
        os.remove(bin_path)

# ───────────────────────────── optional resizing ──────────────────────────────
if args.resize:
    print("[INFO] Copying & resizing images …")
    for scale, folder in [(0.50, "images_2"), (0.25, "images_4"), (0.125, "images_8")]:
        out_dir = f"{src}/{folder}"
        os.makedirs(out_dir, exist_ok=True)
        for fn in os.listdir(f"{src}/images"):
            shutil.copy2(f"{src}/images/{fn}", f"{out_dir}/{fn}")
        run(f"{magick} mogrify -resize {scale*100}% {out_dir}/*.png")

print("\nDone.  ASCII model written to  sparse/0/*.txt")