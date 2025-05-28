# python combinecubemap.py \
#     --forward_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver2/posz_posx_negz \
#     --backward_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/2_cubemap/negz/input \
#     --forward_start 1 \
#     --forward_end 123 \
#     --backward_start 20 \
#     --backward_end 60 \
#     --out_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver2

# python combinecubemap_multiple.py \
# --config /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/accessories/combcube_multi_config.txt \
# --start_idx 20 \
# --end_idx 100 \
# --out_dir /work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver4

python combinecubemap_multiple_intermediates.py `
    --config "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\code_gaussian-splatting\accessories\win_combcube_multi_interme_config.txt" `
    --equirect_dir "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\data\onedrive_2023_12_13\type1\original" `
    --start_idx 0 `
    --end_idx 14 `
    --num_intermediate 3 `
    --vfov 90 `
    --out_size 512 `
    --out_dir "C:\Users\dgamdha\work\Projects\others\gaussian_splatting\data\onedrive_2023_12_13\type1\cubemap_combined\ver1"


