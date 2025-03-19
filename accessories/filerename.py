import os
import shutil
import argparse

def rename_images(input_dir, output_dir):
    # Create output directory if it doesn't exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each file in the input directory.
    for file_name in os.listdir(input_dir):
        if file_name.startswith('frame_') and file_name.endswith('.jpg'):
            # Extract the numeric part of the filename.
            number_str = file_name[len('frame_'):-len('.jpg')]
            try:
                original_number = int(number_str)
            except ValueError:
                print(f"Skipping {file_name}: Cannot convert '{number_str}' to an integer.")
                continue

            # Divide the number by 10.
            new_number = original_number // 10
            # Format the new number with six digits (zero-padded).
            new_file_name = f"{new_number:06d}.jpg"

            # Define the full paths.
            src = os.path.join(input_dir, file_name)
            dst = os.path.join(output_dir, new_file_name)

            # Copy the file with the new name.
            shutil.copy(src, dst)
            print(f"Renamed {file_name} -> {new_file_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename images by dividing the numeric part of the filename by 10."
    )
    parser.add_argument("input_dir", help="Path to the directory containing original images.")
    parser.add_argument("output_dir", help="Path to the directory where renamed images will be saved.")
    args = parser.parse_args()

    rename_images(args.input_dir, args.output_dir)
