# Lab Program 10: Pandas DataFrame Operations
try:
    import pandas as pd

    data = {
        "Roll No": ["212M1A0501", "212M1A0502", "212M1A0503", "212M1A0504"],
        "Name": ["K. Sravani", "M. Anusha", "P. Divya", "T. Swapna"],
        "Python Marks": [95, 88, 92, 90],
        "Attendance %": [98.5, 92.0, 96.0, 94.5]
    }

    df = pd.DataFrame(data)
    print("=== GITAMW CSE Student Performance Table ===")
    print(df.to_string(index=False))

    print("
Average Python Marks:", df["Python Marks"].mean())
except ImportError:
    print("Pandas is not installed. Please install Pandas using the Package Manager.")
