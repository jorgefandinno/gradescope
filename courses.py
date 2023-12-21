from datetime import timedelta, datetime
import re
from pprint import pprint
from typing import Optional, TypedDict
from dataclasses import dataclass
from canvasapi import Canvas
import pandas as pd
from assigments import Assigment, GradescopeAssigment, CanvasAssigment, CanvasModule, AssigmentFactory, ExamFactory
import gradescope
from canvasapi.course import Course as CanvasCourse

class Time(TypedDict):
    hour: int
    minute: int

def name_to_key(name):
    name = re.sub("[\(\[].*?[\)\]]", "", name)
    name = name.strip().replace(" ","")
    return name

def gradescope_assigment_id(id):
    return id.replace("assignment_","").strip().replace(" ","")

def _module_topic_split_name(name):
    splitted = name.split(":")
    prefix = splitted[0].strip()
    if len(splitted) <= 1 or not prefix.startswith("Topic"):
        return None, name
    name = splitted[1].strip()
    splitted = name.split("|")
    name = splitted[0].strip()
    return prefix, name

@dataclass
class Course:
    midterm_time: Time
    assiments_release_date: datetime
    midterm_length = timedelta(hours=1, minutes=15)
    project_slip_days = 2
    homework_slip_days = 0

    def __init__(self, 
                name: str,
                midterm_time: Time,
                assiments_release_date: datetime,
                excel_file_path: str,
                *,
                midterm_length = timedelta(hours=1, minutes=15),
                project_slip_days = 2,
                homework_slip_days = 0,
                canvas_course: Optional[CanvasCourse] = None,
                gradescope_course_id: Optional[str] = None,
                assigments_due_time = { "hour": 23, "minute": 59 },
                assigments_week_day = 2,
        ):
        self.name = name
        self.canvas_course = canvas_course
        self.gradescope_course_id = gradescope_course_id
        self.excel_file_path = excel_file_path
        self.assigment_factory = AssigmentFactory(assiments_release_date, assigments_due_time, assigments_week_day, homework_slip_days)
        self.project_factory = AssigmentFactory(assiments_release_date, assigments_due_time, assigments_week_day, project_slip_days)
        self.exam_factory = ExamFactory(midterm_time, midterm_length)
        self.assigments_by_name : Optional[dict[str, Assigment]] = None
        self.gradescope_assigments : Optional[list[GradescopeAssigment]] = None


    def read_schedule(self) -> None:
        assert self.excel_file_path is not None, "You must provide an excel file path"
        df = pd.read_excel(self.excel_file_path)
        assigments = []
        for _, row in df.iterrows():
            due_date = pd.to_datetime(row.iloc[0])
            last_col = min(9, len(row))
            for col in range(1,last_col):
                name = row.iloc[col]
                if isinstance(name, str):
                    name = name.strip().replace(" ","")
                    if name.startswith("HW") or name.startswith("RD"):
                        assigments.append(self.assigment_factory.create(name, due_date, type=name[:2]))
                    elif name.startswith("Project"):
                        assigments.append(self.project_factory.create(name, due_date, type="Project"))
                    elif name.startswith("Exam") or name.startswith("Midterm"):
                        assigments.append(self.exam_factory.create(name, pd.to_datetime(row.iloc[col-1])))
                    else:
                        matches = re.findall(r"T\d+:", name)
                        if len(matches) > 0:
                            name = matches[0].replace("T", "Topic #").replace(":","")
                            assigments.append(Assigment.create_module(name, pd.to_datetime(row.iloc[col-1])))
        
        self.assigments_by_name = {}
        for assigment in assigments:
            self.assigments_by_name[name_to_key(assigment.name)] = assigment
    

    def read_gradescope_assigments(self) -> None:
        assert self.assigments_by_name is not None, "You must read the schedule first"
        assert self.gradescope_course_id is not None, "You must provide a gradescope course id"
        if not gradescope.api.last_cookies:
            print(f"Logging in Gradescope...")
            gradescope.api.get_auth_cookies(username="jorgefandinno@gmail.com", password="D4nuRvPw#%@xG*:") 
        print(f"Retriving assigments in Gradescope for course {self.gradescope_course_id} ...")
        self.gradescope_assigments = []
        for assigment in gradescope.macros.get_course_assignments(self.gradescope_course_id):
            key = name_to_key(assigment["title"])
            id = gradescope_assigment_id(assigment["id"])
            self.gradescope_assigments.append(GradescopeAssigment(self.gradescope_course_id, id, assigment["title"], self.assigments_by_name[key]))

    
    def read_canvas_assigments(self) -> None:
        assert self.assigments_by_name is not None, "You must read the schedule first"
        assert self.canvas_course is not None, "You must provide a canvas course id"
        readings_count = 1
        self.canvas_assigments = []
        print(f"Retriving assigments in Canvas for course {self.canvas_course.name} ...")
        for assignment in self.canvas_course.get_assignments():
            key = name_to_key(assignment.name)
            if key.startswith("Reading"):
                key = "RD" + str(readings_count)
                readings_count += 1
                only_sections = [ s.id for s in self.canvas_sections if s.sis_section_id.startswith("CSCI8456")] if self.canvas_sections is not None else None
            else:
                key = key.replace(" ", "")
                only_sections = None
            if key in self.assigments_by_name:
                ignore_release_date = (self.assigments_by_name[key].type != "Midterm")
                self.canvas_assigments.append(CanvasAssigment(assignment.name, self.assigments_by_name[key], assignment, only_sections, ignore_release_date))


    def read_canvas_modules(self) -> None:
        self.canvas_modules = []
        for module in self.canvas_course.get_modules():
            prefix, name = _module_topic_split_name(module.name)
            if prefix is None:
                continue
            key = name_to_key(prefix)
            if key in self.assigments_by_name:
                new_name = f"{prefix}: {name} | {self.assigments_by_name[key].release_date.strftime('%b %d')}"
                self.canvas_modules.append(CanvasModule(new_name, module))


    def read_canvas_sections(self) -> None:
        self.canvas_sections = list(self.canvas_course.get_sections())


    def read_and_download_canvas(self) -> None:
        if self.assigments_by_name is None:
            self.read_schedule()
        self.read_canvas_sections()
        self.read_canvas_assigments()
        self.read_canvas_modules()

    def read_and_download_all(self) -> None:
        self.read_schedule()
        if self.gradescope_course_id is not None:
            self.read_gradescope_assigments()
        if self.canvas_course is not None:
            self.read_and_download_canvas()


    def update_gradescope(self) -> None:
        assert self.gradescope_assigments is not None, "You must read the assigments first"
        for assigment in self.gradescope_assigments:
            assigment.update_gradescope()


    def update_canvas(self) -> None:
        assert self.canvas_assigments is not None, "You must read the assigments first"
        for assigment in self.canvas_assigments:
            assigment.update_canvas()
        assert self.canvas_modules is not None, "You must read the modules first"
        for module in self.canvas_modules:
            module.update_canvas()


    def update(self) -> None:
        if self.gradescope_course_id is not None:
            self.update_gradescope()
        if self.canvas_course is not None:
            self.update_canvas()

    def read_and_update(self) -> None:
        self.read_and_download_all()
        pprint(self.canvas_assigments)
        self.update()