import cv2
import os
import numpy as np

def extract_equirectangular_frames(video_path, output_dir, skip_frames=1):
    """
    Extracts equirectangular frames from a 360° video file.
    
    :param video_path: Path to the input 360° equirectangular video.
    :param output_dir: Directory to save extracted frames.
    :param skip_frames: Extract one frame out of every `skip_frames`.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % skip_frames == 0:
            out_path = os.path.join(output_dir, f"frame_{frame_idx:06d}.jpg")
            cv2.imwrite(out_path, frame)
            saved_count += 1
        
        frame_idx += 1
    
    cap.release()
    print(f"Extracted {saved_count} frames to {output_dir}")
    
def equirect_to_cubemap(equirect_img, face_size=512):
    """
    Converts an equirectangular image to a cubemap with 6 faces.
    
    :param equirect_img: Input equirectangular image (H x W x 3).
    :param face_size: Size of each face in the cubemap.
    :return: A dict of face_name -> face_image, each face_image is (face_size x face_size x 3).
    """
    h, w, _ = equirect_img.shape
    
    # Define cube faces with (target direction) and (up vector)
    # face_name -> (center_direction, up_vector)
    # Directions are in 3D: +X, -X, +Y, -Y, +Z, -Z
    # This is one possible convention; you can change orientation as needed.
    faces = {
        'posx': (np.array([ 1,  0,  0]), np.array([0, -1, 0])),
        'negx': (np.array([-1,  0,  0]), np.array([0, -1, 0])),
        'posy': (np.array([ 0,  1,  0]), np.array([0,  0,  1])),
        'negy': (np.array([ 0, -1,  0]), np.array([0,  0, -1])),
        'posz': (np.array([ 0,  0,  1]), np.array([0, -1,  0])),
        'negz': (np.array([ 0,  0, -1]), np.array([0, -1,  0]))
    }
    
    # Prepare output dictionary
    cube_faces = {}

    for face_name, (center_dir, up_dir) in faces.items():
        face_img = np.zeros((face_size, face_size, 3), dtype=np.uint8)

        for y in range(face_size):
            for x in range(face_size):
                # Convert (x, y) on the face to direction in 3D
                # Map from [-1,1] range
                u = (2.0 * x / face_size) - 1.0
                v = (2.0 * y / face_size) - 1.0
                
                # We assume a 90-degree FOV for each face
                # right_dir = cross(center_dir, up_dir)
                right_dir = np.cross(center_dir, up_dir)
                
                # direction = center_dir + u*right_dir + v*up_dir
                dir_3d = center_dir + u * right_dir + v * up_dir
                dir_3d = dir_3d / np.linalg.norm(dir_3d)
                
                # Convert dir_3d to spherical coordinates
                # Theta (longitude) range [-pi, pi], Phi (latitude) range [-pi/2, pi/2]
                # dir_3d = [X, Y, Z]
                x_3d, y_3d, z_3d = dir_3d
                longitude = np.arctan2(z_3d, x_3d)
                latitude = np.arcsin(y_3d)

                # Map longitude, latitude to equirectangular coords
                # Equirect: x = (longitude + pi) / (2*pi) * w
                #           y = (pi/2 - latitude) / pi * h
                # Make sure these are clipped in valid range [0, w-1], [0, h-1]
                
                # Scale from [-pi, pi] to [0, w], [-pi/2, pi/2] to [0, h]
                x_eq = (longitude + np.pi) / (2.0 * np.pi) * w
                y_eq = (np.pi/2 - latitude) / np.pi * h
                
                x_eq = int(np.clip(x_eq, 0, w-1))
                y_eq = int(np.clip(y_eq, 0, h-1))
                
                face_img[y, x] = equirect_img[y_eq, x_eq]
        
        cube_faces[face_name] = face_img
    
    return cube_faces

if __name__ == "__main__":
    # vid_1_pth = '/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/vid_1/1_VID_20241024_192309_00_028.mp4'
    equirect_pth = '/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/1_equirect'
    cubemap_pth = '/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/2_cubemap'
    # skip_frames=10 
    # extract_equirectangular_frames(vid_1_pth, equirect_pth, skip_frames)
    
    facenames = ['posx', 'negx', 'posy', 'negy', 'posz', 'negz']
    
    # Check if cubemap_pth exist else create the folder
    if not os.path.exists(cubemap_pth):
        os.makedirs(cubemap_pth)
        
    # Check if facenames folders exist inside the cubemap_pth else create the folders
    for face in facenames:
        face_path = os.path.join(cubemap_pth, face)
        if not os.path.exists(face_path):
            os.makedirs(face_path)
            
    # Loop through each equirectangular image inside the equirect_pth and convert to cubemap
    for img_name in os.listdir(equirect_pth):
        if img_name.endswith('.jpg') or img_name.endswith('.png'):
            equirect_img_path = os.path.join(equirect_pth, img_name)
            equirect_img = cv2.imread(equirect_img_path)
            
            # Convert to cubemap
            cube_faces = equirect_to_cubemap(equirect_img)
            
            # Save each face of the cubemap
            for face_name, face_img in cube_faces.items():
                face_path = os.path.join(cubemap_pth, face_name, img_name)
                cv2.imwrite(face_path, face_img)
            print(f"Converted {img_name} to cubemap faces in {cubemap_pth}")
        # break
    print("Cubemap conversion completed for all images.")
