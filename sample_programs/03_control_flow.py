# Lab Program 03: Control Flow (Loops & Conditionals)
print("=== Even / Odd Classifier (1 to 10) ===")

for num in range(1, 11):
    if num % 2 == 0:
        print(f"Number {num:2d} is EVEN")
    else:
        print(f"Number {num:2d} is ODD")

print("
Grade Evaluator Example:")
marks = 87
if marks >= 90:
    grade = "A+ (Outstanding)"
elif marks >= 80:
    grade = "A (Excellent)"
elif marks >= 70:
    grade = "B (Good)"
else:
    grade = "Pass"

print(f"Marks: {marks} -> Grade: {grade}")
