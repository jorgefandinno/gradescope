from collections import namedtuple
from dataclasses import dataclass, field
import math
import os
import re
from typing import Any, Optional
import gradescope
from datetime import datetime, timedelta
from pprint import pprint
import pandas as pd
from canvasapi import Canvas
from courses import Course

from assigments import Assigment, GradescopeAssigment, CanvasAssigment, CanvasModule, AssigmentFactory, ExamFactory

API_URL = "https://unomaha.instructure.com/"
ACCESS_TOKEN = "9322~cqTpj8aMXoQIsnFcqp7kvtGMGuGRR9f8Q3fSeW7RBwv63ZMwIkt60nTVEHJlYdlf"

START_DATE = datetime(2024, 1, 21)

print("Logging in Canvas...")
canvas = Canvas(API_URL, ACCESS_TOKEN)

ai_course = Course(
    name="Artificial Intelligence",
    midterm_time={ "hour": 13, "minute": 30 },
    assiments_release_date=START_DATE,
    excel_file_path="schedule_ai_spring_2024.xlsx",
    midterm_length = timedelta(hours=1, minutes=15),
    project_slip_days = 2,
    homework_slip_days = 0,
    canvas_course = canvas.get_course("75969"),
    gradescope_course_id = "659956",
    assigments_due_time = { "hour": 23, "minute": 59 },
    assigments_week_day = 2,
)

ai_course.read_and_update()

# assigment_factory = AssigmentFactory(RELEASE_DATE, ASSIGMENTS_DUE_TIME, ASSIGMENTS_WEEK_DAY)
# project_factory = AssigmentFactory(RELEASE_DATE, ASSIGMENTS_DUE_TIME, ASSIGMENTS_WEEK_DAY, PROJECT_SLIP_DAYS)
# exam_factory = ExamFactory(MIDTERM_AVALIABLE_TIME, MIDTERM_LENGHT)



# def read_schedule(excel_file_path: str) -> dict[str, Assigment]:
#     df = pd.read_excel(excel_file_path)
#     assigments = []
#     for _, row in df.iterrows():
#         due_date = pd.to_datetime(row.iloc[0])
#         for col in range(1,9):
#             name = row.iloc[col]
#             if isinstance(name, str):
#                 name = name.strip().replace(" ","")
#                 if name.startswith("HW") or name.startswith("RD"):
#                     assigments.append(assigment_factory.create(name, due_date, type=name[:2]))
#                 elif name.startswith("Project"):
#                     assigments.append(project_factory.create(name, due_date, type="Project"))
#                 elif name.startswith("Exam") or name.startswith("Midterm"):
#                     assigments.append(exam_factory.create(name, pd.to_datetime(row.iloc[col-1])))
#                 else:
#                     matches = re.findall(r"T\d+:", name)
#                     if len(matches) > 0:
#                         name = matches[0].replace("T", "Topic #").replace(":","")
#                         assigments.append(Assigment.create_module(name, pd.to_datetime(row.iloc[col-1])))
#     assigments_by_type = {
#         "HW": [],
#         "Project": [],
#         "Midterm": [],
#         "Module": [],
#         "RD": [],
#     }
#     for assigment in assigments:
#         assigments_by_type[assigment.type].append(assigment)
#     return assigments_by_type

# def name_to_key(name):
#     name = re.sub("[\(\[].*?[\)\]]", "", name)
#     name = name.strip().replace(" ","")
#     return name

# def gradescope_assigment_id(id):
#     return id.replace("assignment_","").strip().replace(" ","")

# def read_gradescope_assigments(course: str, assigments_by_name: dict[str, Assigment]) -> list[GradescopeAssigment]:
#     if not gradescope.api.last_cookies:
#         print(f"Logging in Gradescope...")
#         gradescope.api.get_auth_cookies(username="jorgefandinno@gmail.com", password="D4nuRvPw#%@xG*:") 
#     print(f"Retriving assigments for course {course} ...")
#     gradescope_assigments = []
#     for assigment in gradescope.macros.get_course_assignments(course):
#         key = name_to_key(assigment["title"])
#         id = gradescope_assigment_id(assigment["id"])
#         gradescope_assigments.append(GradescopeAssigment(course, id, assigment["title"], assigments_by_name[key]))
#     return gradescope_assigments


# def read_canvas_assigments(course: Course, assigments_by_name: dict[str, Assigment]) -> list[CanvasAssigment]:
#     readings_count = 1
#     canvas_assigments = []
#     for assignment in course.get_assignments():
#         key = name_to_key(assignment.name)
#         if key.startswith("Reading"):
#             key = "RD" + str(readings_count)
#             readings_count += 1
#         else:
#             key = key.replace(" ", "")
#         if key in assigments_by_name:
#             canvas_assigments.append(CanvasAssigment(assignment.name, assigments_by_name[key], assignment))
#     return canvas_assigments

# def _module_topic_split_name(name):
#     splitted = name.split(":")
#     prefix = splitted[0].strip()
#     if len(splitted) <= 1 or not prefix.startswith("Topic"):
#         return None, name
#     name = splitted[1].strip()
#     splitted = name.split("|")
#     name = splitted[0].strip()
#     return prefix, name

# def read_canvas_modules(course: Course, assigments_by_name: dict[str, Assigment]) -> list[CanvasAssigment]:
#     readings_count = 1
#     canvas_assigments = []
#     for module in course.get_modules():
#         prefix, name = _module_topic_split_name(module.name)
#         if prefix is None:
#             continue
#         key = name_to_key(prefix)
#         if key in assigments_by_name:
#             new_name = f"{prefix}: {name} | {assigments_by_name[key].release_date.strftime('%b %d')}"
#             canvas_assigments.append(CanvasModule(new_name, module))
#     return canvas_assigments

# assigments_by_type = read_schedule(EXECEL_FILE_PATH)
# assigments_by_name = { name_to_key(a.name) : a for l in assigments_by_type.values() for a in l }
# gradescope_assigments = read_gradescope_assigments(GRADESCOPE_COURSE, assigments_by_name)
# print(f"Logging in Canvas...")
# canvas = Canvas(API_URL, ACCESS_TOKEN)
# course = canvas.get_course(CANVAS_COURSE_ID)
# canvas_assigments = read_canvas_assigments(course, assigments_by_name)
# canvas_modules = read_canvas_modules(course, assigments_by_name)

# # pprint(gradescope_assigments)
# # pprint(canvas_assigments)
# # pprint(canvas_modules)

# for assigment in gradescope_assigments:
#     assigment.update_gradescope()

# for assigment in canvas_assigments:
#     assigment.update_canvas()

# for module in canvas_modules:
#     module.update_canvas()

os._exit(0)

# def read_schedule(excel_file_path):
    # Read the Excel file into a DataFrame
    # df = pd.read_excel(excel_file_path)

    # # Create empty lists to store the content of the first and sixth columns
    # assigments = {}

    # # Iterate over all rows and collect/transform the content of the columns
    # for _, row in df.iterrows():
    #     due_date = pd.to_datetime(row.iloc[0])
    #     for col in range(1,9):
    #         name = row.iloc[col]
    #         if isinstance(name, str):
    #             name = name.strip().replace(" ","")
    #             if name.startswith("HW") or name.startswith("Project") or name.startswith("RD"):
    #                 assigments[name] = due_date
    #             elif name.startswith("Exam") or name.startswith("Midterm"):
    #                 assigments[name] = pd.to_datetime(row.iloc[col-1])
    #             else:
    #                 matches = re.findall(r"T\d+:", name)
    #                 if len(matches) > 0:
    #                     key = matches[0].replace("T", "Topic #").replace(":","")
    #                     assigments[key] = pd.to_datetime(row.iloc[col-1])
    #     # name1 = row.iloc[6]
    #     # name2 = row.iloc[7]
    #     # if isinstance(name1, str):
    #     #     name1 = name1.strip().replace(" ","")
    #     #     assigments[name1] = due_date
    #     # if isinstance(name2, str):
    #     #     name2 = name2.strip().replace(" ","")
    #     #     assigments[name2] = due_date
    
    # return assigments





def _gradescope_assigment(assigment_name, due_date, release_date=RELEASE_DATE):
    due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + timedelta(days=ASSIGMENTS_WEEK_DAY)
    hard_due_date = None if assigment_name.startswith("HW") else due_date + timedelta(days=2)
    return {
        "release_date": release_date,
        "due_date": due_date,
        "hard_due_date": hard_due_date,
    }

def _cavas_assigment(assigment_name, due_date, release_date=RELEASE_DATE):
    if assigment_name.startswith("Midterm") or assigment_name.startswith("Exam"):
        avaliable_date = due_date.replace(**MIDTERM_AVALIABLE_TIME)
        due_date = avaliable_date + MIDTERM_LENGHT
        avaliable_until_date = due_date
    elif assigment_name.startswith("RD"):
        avaliable_date = ""
        due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + timedelta(days=ASSIGMENTS_WEEK_DAY)
        avaliable_until_date = due_date
    else:
        avaliable_date = due_date
        due_date = avaliable_date + timedelta(days=2)
        avaliable_until_date = due_date + timedelta(days=PROJECT_SLIP_DAYS)
    return {
        "unlock_at": avaliable_date,
        "due_at": due_date,
        "lock_at": avaliable_until_date,
    }

def _cavas_assigment_from_gradescope(gradescope_assigment):
    return {
        "unlock_at": gradescope_assigment["release_date"],
        "due_at": gradescope_assigment["due_date"],
        "lock_at": gradescope_assigment["hard_due_date"],
    }

def gradescope_and_canvas_assigments(assigments, release_date=RELEASE_DATE):
    gradescope_assigments = {}
    canvas_assigments = {}
    canvas_modules = {}
    for assigment_name, due_date in assigments.items():
        if assigment_name.startswith("HW") or assigment_name.startswith("Project"):
            gradescope_assigments[assigment_name] =  _gradescope_assigment(assigment_name, due_date, release_date)
            canvas_assigments[assigment_name] = _cavas_assigment_from_gradescope(gradescope_assigments[assigment_name])
        elif assigment_name.startswith("Exam") or assigment_name.startswith("Midterm") or assigment_name.startswith("RD"):
            canvas_assigments[assigment_name] = _cavas_assigment(assigment_name, due_date, release_date=RELEASE_DATE)
        elif assigment_name.startswith("Topic"):
            canvas_modules[assigment_name] = due_date
    return gradescope_assigments, canvas_assigments, canvas_modules


def set_gradescope_due_dates(course, gradescope_assigments):
    print(f"Logging ...")
    gradescope.api.get_auth_cookies(username="jorgefandinno@gmail.com", password="D4nuRvPw#%@xG*:") 
    print(f"Retriving assigments for course {course} ...")
    assigments = gradescope.macros.get_course_assignments(course)
    
    # pprint(assigments)

    for assigment in assigments:
        print(f"Updating {assigment['title']} ...")
        name = get_assigment_name(assigment["title"])
        id = gradescope_assigment_id(assigment["id"])
        gradescope.macros.set_course_assignment_settings(
            course,
            id,
            gradescope_assigments[name]["release_date"],
            gradescope_assigments[name]["due_date"],
            gradescope_assigments[name]["hard_due_date"],
        )

    print(f"Checking assigments  ...")
    assigments_check = gradescope.macros.get_course_assignments(course)
    
    # pprint(assigments_check)

    for assigment in assigments_check:
        name = get_assigment_name(assigment["title"])
        id = gradescope_assigment_id(assigment["id"])
        if gradescope_assigments[name]["release_date"] != assigment["submission_window"]["release_date"]:
            print("Error in release_date for assigment: ", name)
        if gradescope_assigments[name]["due_date"] != assigment["submission_window"]["due_date"]:
            print("Error in due_date for assigment: ", name)
        if gradescope_assigments[name]["hard_due_date"] != assigment["submission_window"]["hard_due_date"]:
            print("Error in hard_due_date for assigment: ", name)

    

    # # assiment_settings = gradescope.macros.get_course_assignment_settings("619740", "3328192")
    # # release_date = datetime(2020, 10, 20, 23, 59, 0, 0)
    # # due_date = datetime(2024, 10, 20, 23, 59, 0, 0)
    # # hard_due_date = None
    # # assiment_settings = gradescope.macros.set_course_assignment_settings("619740", "3328192", release_date, due_date, hard_due_date)

    # # print(assiment_settings)
            

def set_canvas_due_dates(canvas_assigments, canvas_modules):
    print(f"Logging ...")
    canvas = Canvas(API_URL, ACCESS_TOKEN)
    course = canvas.get_course(CANVAS_COURSE_ID)
    assignments = course.get_assignments()
    modules = course.get_modules()
    readings_count = 1
    for assignment in assignments:
        key = re.sub("[\(\[].*?[\)\]]", "", assignment.name)
        if key.startswith("Reading"):
            key = "RD" + str(readings_count)
            readings_count += 1
        else:
            key = key.replace(" ", "")
        if key in canvas_assigments:
            print(f"Updating {assignment.name} ...")
            assignment.edit(assignment=canvas_assigments[key])

    for module in modules:
        module_name_splitted = module.name.split("|")
        if len(module_name_splitted) > 1:
            module_name = module_name_splitted[0].strip()
            module_name_splitted = module_name.split(":")
            if len(module_name_splitted) > 1:
                topic = module_name_splitted[0].strip()
                module_name = module_name_splitted[1].strip()
                if topic in canvas_modules:
                    new_name = f"{topic}: {module_name} | {canvas_modules[topic].strftime('%b %d')}"
                    print(f"Updating name of '{module.name}' to '{new_name}' ...")
                    module.edit(module={'name': new_name})
        # print(name)

            # print(f"Updated assignment: {assignment.name}, New Due Date: {canvas_assigments[assignment.name]['due_date']}")
        # Get the current due date
        # current_due_date = strptime(assignment.due_at, "%Y-%m-%dT%H:%M:%SZ")

        # # Increment the due date by 1 day
        # new_due_date = current_due_date + increment_value

        # # Format the new due date as required by Canvas
        # new_due_date_str = new_due_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # # Update the assignment with the new due date
        # # assignment.edit(assignment={'due_at': new_due_date_str})
        # print(f"Updated assignment: {assignment.name}, New Due Date: {new_due_date_str}")





# Call the function to read the Excel file, transform the first column, and collect the 6th column in a tuple
print("Reading Excel file ...")
assigments = read_schedule(EXECEL_FILE_PATH)
pprint(assigments)
# gradescope_assigments, canvas_assigments, canvas_modules = gradescope_and_canvas_assigments(assigments)
# # pprint(gradescope_assigments)
# set_canvas_due_dates(canvas_assigments, canvas_modules)
# set_gradescope_due_dates("659956", assigments)
# print("DONE")




