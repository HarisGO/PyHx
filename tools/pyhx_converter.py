# PyHx/tools/pyhx_converter.py

import sys
import os
import shutil

def create_pyhx_package(source_folder, output_dir):
    """
    Validates the source folder and compresses it into a .pyhx file.

    A .pyhx package is simply a .zip archive with a custom extension.
    """
    # 1. Validate the source folder
    if not os.path.isdir(source_folder):
        print(f"Error: Source '{source_folder}' is not a valid directory.")
        return

    entry_point = os.path.join(source_folder, 'main.py')
    if not os.path.isfile(entry_point):
        print(f"Error: Source folder '{source_folder}' must contain a 'main.py' file.")
        return

    # 2. Determine output filename and path
    folder_name = os.path.basename(source_folder.rstrip('/\\')) # Get folder name
    archive_name = folder_name
    archive_format = 'zip'
    output_filename = f"{archive_name}.{archive_format}"
    
    # 3. Create the archive (e.g., 'my_app.zip')
    try:
        # shutil.make_archive will zip the contents of source_folder
        shutil.make_archive(
            base_name=archive_name,      # Name of the file to create, without extension
            format=archive_format,       # The archive format ('zip', 'tar', etc.)
            root_dir=source_folder       # The directory to archive
        )
    except Exception as e:
        print(f"Error: Failed to create archive. {e}")
        return

    # 4. Rename the archive to .pyhx and move it
    final_pyhx_path = os.path.join(output_dir, f"{archive_name}.pyhx")
    try:
        # Rename 'my_app.zip' to 'my_app.pyhx'
        os.rename(output_filename, final_pyhx_path)
        print(f"Successfully created '{final_pyhx_path}'")
    except Exception as e:
        print(f"Error: Failed to rename/move archive. {e}")


if __name__ == '__main__':
    # This part allows the script to be run from the command line
    if len(sys.argv) != 2:
        print("Usage: python pyhx_converter.py /path/to/folder")
    else:
        source_directory = sys.argv[1]
        # For now, let's place the output in a 'packages' directory relative to where the command is run
        output_directory = 'packages' 
        os.makedirs(output_directory, exist_ok=True) # Ensure the output directory exists
        create_pyhx_package(source_directory, output_directory)
