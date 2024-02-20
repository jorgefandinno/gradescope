import os
import argparse
import subprocess



def remove_common_prefix_from_directories(base_directory):
    dirs = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
    for dir in dirs:
        print("Fetching from " + dir + "...")
        result = subprocess.run(['git', 'fetch', '--all'], cwd=os.path.join(base_directory, dir))
        result = subprocess.run(['git', 'commit', '-am"Instructor update: correcting typo in autograder.json"'], cwd=os.path.join(base_directory, dir))
        result = subprocess.run(['git', 'push'], cwd=os.path.join(base_directory, dir))


def main():
    parser = argparse.ArgumentParser(description='Commits and pushes all repositories in a given directory.')
    parser.add_argument('base_directory', help='Path to the base directory')

    args = parser.parse_args()
    base_directory = args.base_directory

    remove_common_prefix_from_directories(base_directory)
    print("Prefix removed from directories.")

if __name__ == "__main__":
    main()