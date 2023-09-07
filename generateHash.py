import os
import hashlib
import json

def generate_file_hash(filepath):
    """Generate a hash for a file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_hashes_from_directory(directory):
    """Generate hashes for all files in the specified directory and its subdirectories."""
    hashes = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            file_hash = generate_file_hash(filepath)
            hashes[filepath.replace(directory, '').lstrip(os.sep)] = file_hash
    return hashes

def save_hashes_to_file(hashes, filename):
    """Save the hashes to a file."""
    with open(filename, 'w') as file:
        json.dump(hashes, file)

def get_latest_version_install_directory(mods_directory="__mods/"):
    """Get the path of the _install subdirectory in the latest version directory."""
    versions = [d for d in os.listdir(mods_directory) if os.path.isdir(os.path.join(mods_directory, d))]
    latest_version = sorted(versions)[-1]
    return os.path.join(mods_directory, latest_version, "_install")

if __name__ == "__main__":
    latest_version_install_directory = get_latest_version_install_directory()
    hashes = get_hashes_from_directory(latest_version_install_directory)
    save_hashes_to_file(hashes, os.path.join(latest_version_install_directory, "hash.fdge"))
