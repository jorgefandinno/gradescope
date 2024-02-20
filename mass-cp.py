import os
import argparse
import shutil


def mass_copy(file, base_directory, path):
    dirs = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
    filename = os.path.basename(file)
    for dir in dirs:
        new_path = os.path.join(base_directory, dir, path, filename)
        shutil.copy(file, new_path)
        print(f"Copied: {file} -> {new_path}")

def main():
    parser = argparse.ArgumentParser(description='Copies a file to all directories in a given directory.')
    parser.add_argument('file', help='Path to the file to copy')
    parser.add_argument('base_directory', help='Path to the base directory')
    parser.add_argument('--path', help='Relative path where the file will be copied relative to each of the directories', default='')

    args = parser.parse_args()
    file = args.file
    base_directory = args.base_directory
    path = args.path

    mass_copy(file, base_directory, path)
    print("Copied to all directories.")

if __name__ == "__main__":
    main()