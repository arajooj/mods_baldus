import os
import zipfile
from tqdm import tqdm

def get_latest_version_directory_and_name(mods_directory="__mods/"):
    """Get the path and name of the latest version directory."""
    versions = [d for d in os.listdir(mods_directory) if os.path.isdir(os.path.join(mods_directory, d))]
    latest_version = sorted(versions)[-1]
    return os.path.join(mods_directory, latest_version), latest_version

def create_zip_from_directory(directory, zip_name):
    """Create a zip file from the contents of a directory."""
    with zipfile.ZipFile(zip_name + ".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in tqdm(files, desc=f"Compressing {root}", unit="file"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                zipf.write(full_path, relative_path)

if __name__ == "__main__":
    print("Getting the latest version directory...")
    latest_version_directory, latest_version_name = get_latest_version_directory_and_name()
    
    install_directory = os.path.join(latest_version_directory, "_install")
    zip_name = os.path.join(latest_version_directory, latest_version_name)
    
    print(f"Compressing files from {install_directory} into {zip_name}.zip...")
    create_zip_from_directory(install_directory, zip_name)
    print("Compression completed!")
