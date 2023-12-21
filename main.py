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

# ai_course.read_and_update()
# ai_course.read_and_download_data()
ai_course.read_and_download_canvas()
ai_course.update_canvas()
