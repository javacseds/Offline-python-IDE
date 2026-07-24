# Lab Program 05: Lists, Tuples, Sets, and Dictionaries

# List Operations
students = ["Sravani", "Anusha", "Priya", "Divya"]
students.append("Lakshmi")
print("CSE Students List:", students)

# Dictionary Operations
student_info = {
    "name": "K. Sravani",
    "roll_no": "222M1A0512",
    "branch": "CSE",
    "skills": ["Python", "HTML", "C++"]
}
print("
Student Profile Dictionary:")
for key, val in student_info.items():
    print(f"  {key.title()}: {val}")
