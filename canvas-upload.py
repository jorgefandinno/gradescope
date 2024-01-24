API_URL = "https://unomaha.instructure.com/"
ACCESS_TOKEN = "9322~1uwKH80flFtxxG6PeXCQwlfwIa1EEMXMysrqTqGATqoKhlraa3bh2ZBcuuNfhk5W"

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to Canvas.")
    parser.add_argument("file_path", help="Path to the file to be uploaded")

    args = parser.parse_args()

from canvasapi import Canvas

canvas = Canvas(API_URL, ACCESS_TOKEN)

canvas_course = canvas.get_course("75929")


def upload_file(course, file_path):
    params = {
        'parent_folder_path': ''
    }
    try:
        uploaded_file = course.upload(file_path, **params)
        print(f"File uploaded successfully! File ID: {uploaded_file[1]['id']}")
    except Exception as e:
        print(f"Failed to upload file. Error: {e}")

if __name__ == "__main__":
    upload_file(canvas_course, args.file_path)