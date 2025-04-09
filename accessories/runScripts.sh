# python combinecubemap.py \
#     --forward_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver2/posz_posx_negz \
#     --backward_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/2_cubemap/negz/input \
#     --forward_start 1 \
#     --forward_end 123 \
#     --backward_start 20 \
#     --backward_end 60 \
#     --out_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver2

python combinecubemap_multiple.py \
--config /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/accessories/combcube_multi_config.txt \
--start_idx 20 \
--end_idx 100 \
--out_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver4

