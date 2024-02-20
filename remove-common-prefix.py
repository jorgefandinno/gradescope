import os
import argparse

def longest_common_prefix(strings):
    if not strings:
        return ""
    prefix = strings[0]
    for string in strings[1:]:
        i = 0
        while i < len(prefix) and i < len(string) and prefix[i] == string[i]:
            i += 1
        prefix = prefix[:i]
    return prefix

def remove_common_prefix_from_directories(base_directory):
    dirs = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
    prefix_to_remove = longest_common_prefix(dirs)
    if not prefix_to_remove:
        return
    for dir in dirs:
        old_path = os.path.join(base_directory, dir)
        new_path = os.path.join(base_directory, dir[len(prefix_to_remove):])
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")

def main():
    parser = argparse.ArgumentParser(description='Remove the common prefix from directories in a given directory.')
    parser.add_argument('base_directory', help='Path to the base directory')

    args = parser.parse_args()
    base_directory = args.base_directory

    remove_common_prefix_from_directories(base_directory)
    print("Prefix removed from directories.")

if __name__ == "__main__":
    main()