import csv
import pathlib

DIRECTORY = "GWA_Calculator"
FILENAME = "grades.csv"

class Grade:
    def __init__(self, raw_grade: float, units: int):
        self.raw = raw_grade
        self.units = units
        self.weighted = raw_grade * units 


def collect_grade_data(grades_reader: iter) -> list[Grade]:
    try:
        return [Grade(float(grade[0]), int(grade[1])) for grade in grades_reader]

    except TypeError:
        print("<SYNTAX ERROR IN FILE>")

        return None

def calculate_total_units(grades: list[Grade]) -> int:
    return sum([grade.units for grade in grades])


def calculate_GWA(grades: list[Grade]) -> float:
    gradeTotal = float(sum([grade.weighted for grade in grades]))
    unitTotal = calculate_total_units(grades)

    return gradeTotal / unitTotal

def read_from_input() -> str:
    grades_reader = []
    print("Enter grades as 'grade, units' (blank line to stop).")

    while True:
        line = input("gwac> ").strip()

        if not line:
            break

        parts = [part.strip() for part in line.split(",")]
        
        if len(parts) != 2:
            print("Format: <grade>, <units>")
            continue

        grades_reader.append(parts)

    grades_list = collect_grade_data(grades_reader)
    
    if not grades_list:
        return "No grades entered."

    gwa = calculate_GWA(grades_list)
    unit_total = calculate_total_units(grades_list)

    lines = [
        f"GWA: {gwa:.2f}", 
        f"Unit Total: {unit_total}", 
        "", 
        "Grades:"]

    for grade in grades_list:
        lines.append(f"{grade.raw:.2f} - {grade.units} unit/s")

    return "\n".join(lines)


def read_from_file(standalone=False) -> None:
    grades_list = []
    unit_total = 0
    gwa = 0.0

    try:
        grades_file = open(pathlib.Path(DIRECTORY).joinpath(FILENAME), 'r')


    except FileNotFoundError:
        grades_file = open(FILENAME, 'r')
    
    except IOError:
        print(f"<UNABLE TO FIND \"{FILENAME}\">")
        
        grades_file = open(pathlib.Path(DIRECTORY).joinpath(FILENAME), "w+")
        
        print(f"<NEW \"{FILENAME.upper()}\" FILE CREATED>")
        
    grades_reader = csv.reader(grades_file)


    print(f"/// GWA CALCULATOR ///")
    print()

    input(f"ARE YOU READY? ")
    print()

    grades_list = collect_grade_data(grades_reader)
    gwa = calculate_GWA(grades_list)
    unit_total = calculate_total_units(grades_list)

    print(f"GWA: {gwa:.2f}")
    print(f"Unit Total: {unit_total}")
    print()

    print("Grades:")
    
    for grade in grades_list:
        print(f"{grade.raw:.2f} - {grade.units} unit/s")
    
    print()


    if standalone:
        input(f"Press ENTER to exit...")

    grades_file.close()