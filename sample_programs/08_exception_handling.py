# Lab Program 08: Exception Handling Demonstration

print("=== Smart Exception Handling Test ===")

def safe_divide(a, b):
    try:
        result = a / b
        print(f"Division ({a} / {b}) = {result:.2f}")
    except ZeroDivisionError as e:
        print(f"[Caught Exception]: Cannot divide {a} by zero!")
    except TypeError as e:
        print(f"[Caught Exception]: Invalid input types provided.")
    finally:
        print("Execution of safe_divide block complete.\n")

safe_divide(100, 5)
safe_divide(50, 0)
