from dataclasses import dataclass, field
from typing import Any, Optional
import gradescope
from datetime import datetime, timedelta


@dataclass
class Assigment:
    name: str
    release_date: datetime
    due_date: datetime
    hard_due_date: datetime
    type: Optional[str] = None

    @classmethod
    def create_project(cls, name, due_date: datetime):
        due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + timedelta(days=ASSIGMENTS_WEEK_DAY)
        return cls(
            name=name,
            release_date=RELEaSE_DATE,
            due_date=due_date,
            hard_due_date=due_date + timedelta(days=PROJECT_SLIP_DAYS),
            type="Project",
        )
    
    @classmethod
    def create_homework(cls, name, due_date: datetime, type: Optional[str] = None):
        due_date = due_date.replace(**ASSIGMENTS_DUE_TIME) + timedelta(days=ASSIGMENTS_WEEK_DAY)
        return cls(
            name=name,
            release_date=RELEaSE_DATE,
            due_date=due_date,
            hard_due_date=due_date,
            type=type,
        )

    @classmethod
    def create_exam(cls, name, due_date: datetime):
        release_date = due_date.replace(**MIDTERM_AVALIABLE_TIME)
        due_date = release_date + MIDTERM_LENGHT
        return cls(
            name=name,
            release_date=release_date,
            due_date=due_date,
            hard_due_date=due_date,
            type="Midterm",
        )
    
    @classmethod
    def create_module(cls, name, date: datetime):
        return cls(
            name=name,
            release_date=date,
            due_date=None,
            hard_due_date=None,
            type="Module",
        )
    
@dataclass
class AssigmentFactory:
    release_date: datetime
    due_time: dict
    day_of_week: int
    slip_days: int = 0

    def create(self, name, due_week_date, type) -> Assigment:
        due_date = (due_week_date + timedelta(days=self.day_of_week)).replace(**self.due_time)
        return Assigment(
            name=name,
            release_date = self.release_date,
            due_date = due_date,
            hard_due_date = due_date + timedelta(days=self.slip_days),
            type=type,
        )
    
@dataclass
class ExamFactory:
    time: dict
    lenght: timedelta

    def create(self, name, date) -> Assigment:
        release_date = date.replace(**self.time)
        due_date = release_date + self.lenght
        return Assigment(
            name=name,
            release_date = release_date,
            due_date = due_date,
            hard_due_date = due_date,
            type = "Midterm",
        )
    
@dataclass
class GradescopeAssigment:
    course: str
    id: str
    name: str
    assigment: Assigment
    
    def update_gradescope(self) -> None:
        if not gradescope.api.last_cookies:
            print(f"Logging ...")
            gradescope.api.get_auth_cookies(username="jorgefandinno@gmail.com", password="D4nuRvPw#%@xG*:")
        print(f"Updating '{self.name}' in Gradescope...")
        gradescope.macros.set_course_assignment_settings(
            self.course,
            self.id,
            self.assigment.release_date,
            self.assigment.due_date,
            self.assigment.hard_due_date,
        )

@dataclass
class CanvasAssigment:
    name: str
    assigment: Assigment
    canvas_object: Any = field(repr=False)

    def update_canvas(self) -> None:
        print(f"Updating '{self.name}' in Canvas ...")
        self.canvas_object.edit(assignment= {
            "unlock_at": self.assigment.release_date,
            "due_at": self.assigment.due_date,
            "lock_at": self.assigment.hard_due_date,
        })

@dataclass
class CanvasModule:
    name: str
    canvas_object: Any = field(repr=False)

    def update_canvas(self) -> None:
        print(f"Updating '{self.name}' in Canvas ...")
        self.canvas_object.edit(module={'name': self.name})