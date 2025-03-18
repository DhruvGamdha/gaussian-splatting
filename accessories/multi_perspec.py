import cv2
import numpy as np

def sample_perspective_from_equirect(equirect_img, vfov=90, yaw=0, pitch=0, out_size=512):
    """
    Samples a pinhole-perspective view from an equirectangular (360°) image.
    
    :param equirect_img: Input equirectangular frame (H x W x 3).
    :param vfov: Vertical field of view in degrees (horizontal is determined by aspect).
    :param yaw: Yaw angle in degrees (left-right, 0 = center).
    :param pitch: Pitch angle in degrees (up-down, 0 = center).
    :param out_size: Size of the output square image in pixels.
    :return: perspective_view, a (out_size x out_size x 3) image
    """
    h, w, _ = equirect_img.shape
    out = np.zeros((out_size, out_size, 3), dtype=np.uint8)
    
    # Convert angles to radians
    yaw_rad = np.deg2rad(yaw)
    pitch_rad = np.deg2rad(pitch)
    
    # Convert FOV to radians
    vfov_rad = np.deg2rad(vfov)
    hfov_rad = vfov_rad  # For a square output, horizontal = vertical FOV
    
    for y in range(out_size):
        for x in range(out_size):
            # Map pixel (x, y) in output to a direction relative to center
            # Normalized coords in range [-1, 1]
            nx = (2.0 * x / out_size) - 1.0
            ny = (2.0 * y / out_size) - 1.0
            
            # Scale by half-FOV
            # For example, if vfov = 90°, half_fov = 45°, so nx * tan(45°)
            # We'll treat the center as looking at yaw=0, pitch=0
            tx = np.tan(hfov_rad / 2) * nx
            ty = np.tan(vfov_rad / 2) * ny
            
            # We now have a direction (tx, ty, 1) in "camera space"
            # We need to rotate this direction by the yaw, pitch
            # 1) Construct direction in 3D
            # By convention, let's say forward = +Z, right = +X, up = -Y (varies by pipeline).
            dz = 1.0
            dx = tx
            dy = -ty
            
            # Normalize
            vec = np.array([dx, dy, dz])
            vec = vec / np.linalg.norm(vec)
            
            # Apply pitch rotation around X
            # pitch moves the view up/down
            # R_x(pitch)
            c_p = np.cos(pitch_rad)
            s_p = np.sin(pitch_rad)
            rot_x = np.array([
                [1,    0,   0],
                [0,   c_p, -s_p],
                [0,   s_p,  c_p]
            ])
            vec = rot_x @ vec
            
            # Apply yaw rotation around Y
            c_y = np.cos(yaw_rad)
            s_y = np.sin(yaw_rad)
            rot_y = np.array([
                [ c_y, 0, s_y],
                [   0, 1,   0],
                [-s_y, 0, c_y]
            ])
            vec = rot_y @ vec
            
            # Now convert vec back to spherical coords for equirectangular sampling
            x_3d, y_3d, z_3d = vec
            longitude = np.arctan2(x_3d, z_3d)  # range [-pi, pi]
            latitude = np.arcsin(y_3d)         # range [-pi/2, pi/2]
            
            # Map to equirect coords
            x_eq = (longitude + np.pi) / (2.0 * np.pi) * w
            y_eq = (np.pi/2 - latitude) / np.pi * h
            
            # Clip and sample
            x_eq = int(np.clip(x_eq, 0, w-1))
            y_eq = int(np.clip(y_eq, 0, h-1))
            
            out[y, x] = equirect_img[y_eq, x_eq]
    
    return out

# Example usage:
img_pth = '/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/1_equirect/frame_000120.jpg'
out_pth = '/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/3_multiPerspective'
eq_img = cv2.imread(img_pth)
# Sample perspective views at different yaw angles, same pitch
for i, yaw_angle in enumerate([0, 90, 180, 270]):
    subview = sample_perspective_from_equirect(eq_img, vfov=90, yaw=yaw_angle, pitch=0, out_size=512)
    cv2.imwrite(f"{out_pth}/view_yaw_{yaw_angle}.jpg", subview)
    # cv2.imwrite(f"view_yaw_{yaw_angle}.jpg", subview)
