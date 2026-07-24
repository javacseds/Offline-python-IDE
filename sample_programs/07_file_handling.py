# Lab Program 07: Local File I/O Operations

file_path = "sample_output.txt"

# Write to local file
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Gouthami Institute of Technology for Women, Proddatur\n")
    f.write("Department of Computer Science & Engineering\n")
    f.write("Python Smart IDE Offline File Creation Test\n")

print(f"Successfully wrote data to '{file_path}'.")

# Read from local file
print("
Reading file contents:")
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
