from datetime import datetime, timedelta
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.styles import NamedStyle

YEAR = 2024

FIST_DAY_OF_CLASSES = datetime(YEAR, 1, 22)
LAST_DAY_OF_CLASSES = datetime(YEAR, 5, 11)
WEEK_DAY_OF_CLASSES = 0 # 0 is MW, 1 is TR

LIST_OF_HOLIDAYS = [
    (datetime(YEAR, 3, 10), datetime(YEAR, 3, 17)),
]

EXAMS = {
    datetime(YEAR, 3, 20) : "Midterm 1",
    datetime(YEAR, 4, 17) : "Midterm 2",
    datetime(YEAR, 5,  8) : "Midterm 3",
}

LIST_OF_TOPICS = [
    "Presentation",
    "ASP Introduction 11",
    "ASP introduction cont(choices)",
    "(project example)",
    "",
    "Positive Programs",
    "Modeling 10",
    "Modeling",
    "Modeling/Python",
    "Python/PropLogic 8",
    "PropLogic 8/ Normal 1",
    "Normal 7",
    "Language(Choice)",
    "Language(Cardinality Upper)",
    "Language(Terms&Literals)",
    "Language",
    "Modeling II(arithmetic prog)",
    "Modeling II(Connectivity, yes/no question)",
    "Modeling II(bounded reachability)",    
    "Modeling II",    
    "Ground image",
    "Ground image",
]

EXCEL_FILE_PATH = f"schedule_pl_{YEAR}.xlsx"
# print()

list_of_holidays = [a if isinstance(a, tuple) else (a,a) for a in LIST_OF_HOLIDAYS]
holy_days = set(start + timedelta(days=day) for start, end in LIST_OF_HOLIDAYS for day in range((end - start).days+1))
# print(sorted(holy_days))
# holy_days = { FIST_DAY_OF_CLASSES + day for day in (LAST_DAY_OF_CLASSES - FIST_DAY_OF_CLASSES).days}

def _get_topic(date, topic_index, second_date=None):
    if day1 in holy_days:
        topic = "Holiday"
    elif date in EXAMS:
        topic = EXAMS[date]
    elif second_date is not None and second_date in EXAMS:
        topic = "Recap"
    elif topic_index < len(LIST_OF_TOPICS):
        topic = LIST_OF_TOPICS[topic_index]
        topic_index += 1
    else:
        topic = ""
    return topic, topic_index

date = FIST_DAY_OF_CLASSES
topic_index = 0
data = []
while date <= LAST_DAY_OF_CLASSES:
    day1  = date + timedelta(WEEK_DAY_OF_CLASSES)
    day2 = date + timedelta(WEEK_DAY_OF_CLASSES+2)
    topic1, topic_index = _get_topic(day1, topic_index, day2)
    topic2, topic_index = _get_topic(day2, topic_index)
    row = [date, day1, topic1, "", day2, topic2]
    data.append(row)
    date += timedelta(days=7)

data = pd.DataFrame(data, columns=["Week", "Date1", "Topic1", "", "Date2", "Topic2"])
# data.to_excel("schedule_pl_2024.xlsx", index=False)

with pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl') as writer:
    data.to_excel(writer, sheet_name='Sheet1', index=False)

    # Get the workbook and the sheet
    workbook = writer.book
    sheet = writer.sheets['Sheet1']

    sheet.column_dimensions['A'].width = 20  # Width of column 'A'
    sheet.column_dimensions['B'].width = 20  # Width of column 'B'
    sheet.column_dimensions['C'].width = 50  # Width of column 'C'
    sheet.column_dimensions['D'].width = 10  # Width of column 'D'
    sheet.column_dimensions['E'].width = 20  # Width of column 'E'
    sheet.column_dimensions['F'].width = 50  # Width of column 'F'

    # Define date formatting style
    date_format = NamedStyle(name='date_format', number_format='MM/DD/YYYY')
    red_format  = NamedStyle(name='red_format', font=Font(color='FF0000'))
    workbook.add_named_style(date_format)
    for row in range(2, len(data)+2):
        sheet[f'A{row}'].style = date_format
        sheet[f'B{row}'].style = date_format
        sheet[f'E{row}'].style = date_format
        cell_content = sheet[f'C{row}'].value.strip()
        if cell_content.startswith("Holiday") or cell_content.startswith("Midterm"):
            sheet[f'C{row}'].style = red_format
        cell_content = sheet[f'F{row}'].value.strip()
        if cell_content.startswith("Holiday") or cell_content.startswith("Midterm"):
            sheet[f'F{row}'].style = red_format
            

