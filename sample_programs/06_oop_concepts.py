# Lab Program 06: Object-Oriented Programming (OOP)

class Student:
    def __init__(self, name: str, roll_no: str, branch: str = "CSE"):
        self.name = name
        self.roll_no = roll_no
        self.branch = branch
        self.marks = {}

    def add_marks(self, subject: str, score: float):
        self.marks[subject] = score

    def calculate_average(self) -> float:
        if not self.marks:
            return 0.0
        return sum(self.marks.values()) / len(self.marks)

    def display(self):
        print(f"Student Name: {self.name} | Roll: {self.roll_no} | Branch: {self.branch}")
        print(f"Average Marks: {self.calculate_average():.2f}")

# Instantiate Student Object
s1 = Student("A. Harshitha", "212M1A0505")
s1.add_marks("Python Programming", 92)
s1.add_marks("Data Structures", 88)
s1.add_marks("Database Systems", 95)
s1.display()
