from collections import namedtuple
import math
import re
import gradescope
import datetime
from pprint import pprint
import pandas as pd
from canvasapi import Canvas

API_URL = "https://unomaha.instructure.com/"
ACCESS_TOKEN = "9322~cqTpj8aMXoQIsnFcqp7kvtGMGuGRR9f8Q3fSeW7RBwv63ZMwIkt60nTVEHJlYdlf"
COURSE_ID = "75969"

RELESE_DATE = datetime.datetime(2024, 1, 21, 0, 0, 0, 0)
ASSIGMENTS_DUE_TIME = { "hour": 23, "minute": 59 }
ASSIGMENTS_WEEK_DAY = 2
PROJECT_SLIP_DAYS = 2

MIDTERM_AVALIABLE_TIME = { "hour": 13, "minute": 30 }
MIDTERM_LENGHT = datetime.timedelta(hours=1, minutes=15)

# Specify the path to your Excel file
EXECEL_FILE_PATH = "schedule_ai_spring_2024.xlsx"


# Specify the path to your Excel file

# ExcelAssigment  = namedtuple("Assigment", "name, due_date")

def read_schedule(excel_file_path):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_file_path)

    # Create empty lists to store the content of the first and sixth columns
    assigments = {}

    # Iterate over all rows and collect/transform the content of the columns
    for _, row in df.iterrows():
        due_date = pd.to_datetime(row.iloc[0])
        for col in range(1,9):
            name = row.iloc[col]
            if isinstance(name, str):
                name = name.strip().replace(" ","")
                if name.startswith("HW") or name.startswith("Project") or name.startswith("RD"):
                    assigments[name] = due_date
                elif name.startswith("Exam") or name.startswith("Midterm"):
                    assigments[name] = pd.to_datetime(row.iloc[col-1])
                else:
                    matches = re.findall(r"T\d+:", name)
                    if len(matches) > 0:
                        key = matches[0].replace("T", "Topic #").replace(":","")
                        assigments[key] = pd.to_datetime(row.iloc[col-1])
        # name1 = row.iloc[6]
        # name2 = row.iloc[7]
        # if isinstance(name1, str):
        #     name1 = name1.strip().replace(" ","")
        #     assigments[name1] = due_date
        # if isinstance(name2, str):
        #     name2 = name2.strip().replace(" ","")
        #     assigments[name2] = due_date
    
    return assigments


def get_assigment_name(name):
    name = name.strip().replace(" ","")
    try:
        index = name.index("(")
        name = name[:index]
    except:
        pass
    return name

def get_assigment_id(id):
    return id.replace("assignment_","").strip().replace(" ","")


def _gradescope_assigment(assigment_name, due_date, relese_date=RELESE_DATE):
    due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + datetime.timedelta(days=ASSIGMENTS_WEEK_DAY)
    hard_due_date = None if assigment_name.startswith("HW") else due_date + datetime.timedelta(days=2)
    return {
        "release_date": relese_date,
        "due_date": due_date,
        "hard_due_date": hard_due_date,
    }

def _cavas_assigment(assigment_name, due_date, relese_date=RELESE_DATE):
    if assigment_name.startswith("Midterm") or assigment_name.startswith("Exam"):
        avaliable_date = due_date.replace(**MIDTERM_AVALIABLE_TIME)
        due_date = avaliable_date + MIDTERM_LENGHT
        avaliable_until_date = due_date
    elif assigment_name.startswith("RD"):
        avaliable_date = ""
        due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + datetime.timedelta(days=ASSIGMENTS_WEEK_DAY)
        avaliable_until_date = due_date
    else:
        avaliable_date = due_date
        due_date = avaliable_date + datetime.timedelta(days=2)
        avaliable_until_date = due_date + datetime.timedelta(days=PROJECT_SLIP_DAYS)
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

def gradescope_and_canvas_assigments(assigments, relese_date=RELESE_DATE):
    gradescope_assigments = {}
    canvas_assigments = {}
    canvas_modules = {}
    for assigment_name, due_date in assigments.items():
        if assigment_name.startswith("HW") or assigment_name.startswith("Project"):
            gradescope_assigments[assigment_name] =  _gradescope_assigment(assigment_name, due_date, relese_date)
            canvas_assigments[assigment_name] = _cavas_assigment_from_gradescope(gradescope_assigments[assigment_name])
        elif assigment_name.startswith("Exam") or assigment_name.startswith("Midterm") or assigment_name.startswith("RD"):
            canvas_assigments[assigment_name] = _cavas_assigment(assigment_name, due_date, relese_date=RELESE_DATE)
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
        id = get_assigment_id(assigment["id"])
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
        id = get_assigment_id(assigment["id"])
        if gradescope_assigments[name]["release_date"] != assigment["submission_window"]["release_date"]:
            print("Error in release_date for assigment: ", name)
        if gradescope_assigments[name]["due_date"] != assigment["submission_window"]["due_date"]:
            print("Error in due_date for assigment: ", name)
        if gradescope_assigments[name]["hard_due_date"] != assigment["submission_window"]["hard_due_date"]:
            print("Error in hard_due_date for assigment: ", name)

    

    # # assiment_settings = gradescope.macros.get_course_assignment_settings("619740", "3328192")
    # # release_date = datetime.datetime(2020, 10, 20, 23, 59, 0, 0)
    # # due_date = datetime.datetime(2024, 10, 20, 23, 59, 0, 0)
    # # hard_due_date = None
    # # assiment_settings = gradescope.macros.set_course_assignment_settings("619740", "3328192", release_date, due_date, hard_due_date)

    # # print(assiment_settings)
            

def set_canvas_due_dates(canvas_assigments, canvas_modules):
    print(f"Logging ...")
    canvas = Canvas(API_URL, ACCESS_TOKEN)
    course = canvas.get_course(COURSE_ID)
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
        # current_due_date = datetime.strptime(assignment.due_at, "%Y-%m-%dT%H:%M:%SZ")

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
gradescope_assigments, canvas_assigments, canvas_modules = gradescope_and_canvas_assigments(assigments)
# pprint(gradescope_assigments)
set_canvas_due_dates(canvas_assigments, canvas_modules)
# set_gradescope_due_dates("659956", assigments)
# print("DONE")




