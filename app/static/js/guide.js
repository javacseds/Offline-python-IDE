/**
 * GITAMW Python Smart IDE - User Guide & Syntax Cheat Sheet Controller
 * Interactive, clickable Python syntax reference card.
 */

const PYTHON_SYNTAX_GUIDE = [
    {
        id: "basics",
        icon: "fa-cubes",
        title: "1. Basics & Variables",
        category: "Fundamentals",
        description: "Variable assignment, data types, type casting, operators, and comments.",
        syntax: `# ── Variables & Data Types ────────────────────────────────
x = 10              # Integer (int)
pi = 3.14159        # Floating point (float)
name = "GITAMW"     # String (str)
is_active = True    # Boolean (bool)

# ── Type Casting ──────────────────────────────────────────
age_str = "20"
age_int = int(age_str)         # 20
val_float = float("12.34")     # 12.34
text_val = str(100)            # "100"

# ── Arithmetic Operators ──────────────────────────────────
sum_val   = 10 + 5    # Addition: 15
diff_val  = 10 - 5    # Subtraction: 5
prod_val  = 10 * 5    # Multiplication: 50
div_val   = 10 / 4    # Division: 2.5 (always float)
floor_div = 10 // 4   # Floor Division: 2 (integer truncation)
mod_val   = 10 % 3    # Modulo (remainder): 1
power_val = 2 ** 3    # Exponentiation: 8

# ── Comments ──────────────────────────────────────────────
# Single line comment
"""
Multi-line comment string
Docstring representation
"""`
    },
    {
        id: "input_output",
        icon: "fa-terminal",
        title: "2. Input & Output",
        category: "I/O",
        description: "Reading stdin with input(), printing output, and string formatting.",
        syntax: `# ── Reading User Input ────────────────────────────────────
user_name = input("Enter your name: ")
user_age = int(input("Enter your age: ")) # Convert string input to int

# ── Printing Output ────────────────────────────────────────
print("Hello", user_name)
print("Multiple", "values", sep=", ", end="\\n")

# ── String Formatting (f-strings - Recommended) ──────────
print(f"Student {user_name} is {user_age} years old.")
print(f"Calculated Value: {3.14159:.2f}") # Format to 2 decimal places

# ── Legacy str.format() ────────────────────────────────────
print("Roll: {} | Branch: {}".format("212M1A0501", "CSE"))`
    },
    {
        id: "control_flow",
        icon: "fa-code-branch",
        title: "3. Control Flow",
        category: "Logic",
        description: "Conditional branching (if/elif/else) and loops (for/while).",
        syntax: `# ── Conditional Statements ────────────────────────────────
score = 85
if score >= 90:
    grade = "A+"
elif score >= 75:
    grade = "A"
else:
    grade = "B"

# ── For Loop & range() ────────────────────────────────────
for i in range(1, 6):          # Generates 1, 2, 3, 4, 5
    print("Item:", i)

for char in "PYTHON":          # Iterate over string
    print(char)

# ── While Loop ────────────────────────────────────────────
count = 0
while count < 3:
    print("Count:", count)
    count += 1

# ── Loop Control Keywords ─────────────────────────────────
for num in range(10):
    if num == 3:
        continue               # Skip remainder of current iteration
    if num == 7:
        break                  # Exit loop immediately
    print(num)`
    },
    {
        id: "data_structures",
        icon: "fa-layer-group",
        title: "4. Data Structures",
        category: "Collections",
        description: "Lists, Tuples, Dictionaries, and Sets creation and methods.",
        syntax: `# ── Lists (Mutable, Ordered) ──────────────────────────────
items = [10, 20, 30]
items.append(40)               # Add to end: [10, 20, 30, 40]
items.insert(1, 15)            # Insert at index: [10, 15, 20, 30, 40]
last = items.pop()             # Remove & return last element
items.sort()                   # Sort in-place

# ── Tuples (Immutable, Ordered) ───────────────────────────
point = (10, 20, 30)
x, y, z = point                # Tuple Unpacking

# ── Dictionaries (Key-Value Pairs) ─────────────────────────
student = {"name": "Sravani", "roll": "501", "branch": "CSE"}
student["year"] = 3            # Add / update key
val = student.get("age", 20)   # Safe lookup with default

for key, val in student.items():
    print(f"{key}: {val}")

# ── Sets (Unique, Unordered) ──────────────────────────────
nums = {1, 2, 2, 3, 4}         # Result: {1, 2, 3, 4}
nums.add(5)
nums.remove(1)`
    },
    {
        id: "strings",
        icon: "fa-font",
        title: "5. Strings & Slicing",
        category: "Text Processing",
        description: "String indexing, slicing syntax, and standard string methods.",
        syntax: `# ── Indexing & Slicing [start:stop:step] ───────────────────
text = "GITAMW CSE Department"

first = text[0]                # 'G' (first char)
last  = text[-1]               # 't' (last char)
sub   = text[0:6]              # 'GITAMW' (slice index 0..5)
rev   = text[::-1]             # Reverse entire string

# ── Common String Methods ─────────────────────────────────
text.lower()                   # 'gitamw cse department'
text.upper()                   # 'GITAMW CSE DEPARTMENT'
text.strip()                   # Remove leading/trailing whitespace
text.replace("CSE", "IT")      # Replace substring
words = text.split(" ")        # ['GITAMW', 'CSE', 'Department']
joined = "-".join(words)       # 'GITAMW-CSE-Department'
text.startswith("GITAMW")      # Returns True
text.endswith("Department")    # Returns True`
    },
    {
        id: "functions",
        icon: "fa-project-diagram",
        title: "6. Functions & Lambdas",
        category: "Modular Code",
        description: "Function definition, parameters, return values, *args, **kwargs, lambda.",
        syntax: `# ── Function Definition & Default Arguments ──────────────
def calculate_total(price, tax_rate=0.05):
    """Calculate price with tax."""
    return price + (price * tax_rate)

result = calculate_total(100.0)    # Returns 105.0

# ── Variable Arguments (*args & **kwargs) ─────────────────
def add_all(*args):
    return sum(args)               # args is a tuple of all positional args

def print_profile(**kwargs):
    for k, v in kwargs.items():    # kwargs is a dict of keyword args
        print(f"{k}: {v}")

# ── Lambda (Anonymous) Functions ──────────────────────────
square = lambda x: x ** 2
print(square(5))                   # Returns 25`
    },
    {
        id: "exceptions",
        icon: "fa-exclamation-triangle",
        title: "7. Exception Handling",
        category: "Error Handling",
        description: "Try/except/else/finally blocks and raising custom exceptions.",
        syntax: `# ── Try / Except / Else / Finally ─────────────────────────
try:
    num = int(input("Enter number: "))
    result = 100 / num
except ZeroDivisionError:
    print("Error: Cannot divide by zero!")
except ValueError as err:
    print(f"Error: Invalid integer input ({err})")
else:
    print("Division succeeded:", result)  # Executes if NO exception occurred
finally:
    print("Cleanup completed.")           # ALWAYS executes

# ── Raising Exceptions ────────────────────────────────────
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative!")
    return True`
    },
    {
        id: "file_handling",
        icon: "fa-file-alt",
        title: "8. File Handling",
        category: "I/O",
        description: "Opening, reading, writing files using 'with' context manager.",
        syntax: `# ── Writing to File ('w' overwrites, 'a' appends) ──────────
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Line 1: GITAMW Smart IDE\\n")
    f.write("Line 2: Offline Execution\\n")

# ── Reading File Contents ──────────────────────────────────
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()             # Read entire file as string
    # lines = f.readlines()        # Read as list of line strings

# ── Iterating File Line by Line ────────────────────────────
with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())`
    },
    {
        id: "oop",
        icon: "fa-sitemap",
        title: "9. Object-Oriented Programming",
        category: "OOP",
        description: "Classes, objects, __init__ constructor, methods, and inheritance.",
        syntax: `# ── Class & Constructor Definition ─────────────────────────
class Student:
    def __init__(self, name, roll_no):
        self.name = name
        self.roll_no = roll_no

    def display(self):
        print(f"Student: {self.name} | Roll: {self.roll_no}")

# ── Inheritance ───────────────────────────────────────────
class CSEStudent(Student):
    def __init__(self, name, roll_no, lab_group="A"):
        super().__init__(name, roll_no)  # Call parent constructor
        self.lab_group = lab_group

# Instantiate & Invoke
s1 = CSEStudent("Sravani", "212M1A0501")
s1.display()`
    },
    {
        id: "modules",
        icon: "fa-cubes",
        title: "10. Modules & Imports",
        category: "Standard Library",
        description: "Importing modules, aliases, and common standard library tools.",
        syntax: `# ── Import Syntax Variations ──────────────────────────────
import math
from math import sqrt, pi, ceil
import random as rnd
from datetime import datetime

# ── Standard Library Examples ──────────────────────────────
print("Square root:", sqrt(25))        # 5.0
print("Ceiling:", ceil(4.2))           # 5

random_val = rnd.randint(1, 100)      # Random integer between 1 and 100
picked = rnd.choice(["CSE", "ECE", "EEE"])

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
    },
    {
        id: "comprehensions",
        icon: "fa-magic",
        title: "11. Comprehensions",
        category: "Pythonic Syntax",
        description: "List, dictionary, and set comprehension syntax patterns.",
        syntax: `# ── List Comprehension ────────────────────────────────────
# [expression for item in iterable if condition]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
# Result: [0, 4, 16, 36, 64]

# ── Dictionary Comprehension ──────────────────────────────
# {key_expr: val_expr for item in iterable}
square_dict = {x: x**2 for x in range(1, 6)}
# Result: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# ── Set Comprehension ─────────────────────────────────────
unique_lengths = {len(word) for word in ["python", "ide", "code", "ide"]}
# Result: {6, 3, 4}`
    },
    {
        id: "builtins",
        icon: "fa-tools",
        title: "12. Built-in Functions",
        category: "Built-ins",
        description: "len(), range(), enumerate(), zip(), map(), filter(), sorted(), sum().",
        syntax: `# ── len(), range(), enumerate(), zip() ─────────────────────
names = ["Sravani", "Anusha", "Divya"]
marks = [95, 88, 92]

print("Length:", len(names))

for idx, name in enumerate(names, start=1):
    print(f"{idx}. {name}")

for name, mark in zip(names, marks):
    print(f"{name}: {mark}")

# ── map(), filter(), sorted(), sum() ───────────────────────
nums = [-5, 2, -8, 10, 3]
positives = list(filter(lambda x: x > 0, nums))    # [2, 10, 3]
doubled   = list(map(lambda x: x * 2, nums))       # [-10, 4, -16, 20, 6]
sorted_n  = sorted(nums, reverse=True)             # [10, 3, 2, -5, -8]
total_sum = sum(nums)                              # 2`
    }
];

// Active open topic index (-1 means all closed)
let activeTopicIndex = 0;

/** Renders the User Guide accordion list */
function renderUserGuide() {
    const container = document.getElementById("guide-topics-accordion");
    if (!container) return;

    container.innerHTML = "";

    PYTHON_SYNTAX_GUIDE.forEach((topic, idx) => {
        const isOpen = idx === activeTopicIndex;
        const card = document.createElement("div");
        card.className = "guide-topic-card mb-2";
        card.id = `guide-card-${idx}`;

        const escapedSyntax = escapeHtml(topic.syntax);

        card.innerHTML = `
            <div class="guide-topic-header" onclick="toggleGuideTopic(${idx})">
                <span>
                    <i class="fas ${topic.icon} me-2 text-warning"></i>
                    <strong>${topic.title}</strong>
                </span>
                <div>
                    <span class="badge bg-secondary me-2" style="font-size:0.65rem;">${topic.category}</span>
                    <i class="fas ${isOpen ? 'fa-chevron-up' : 'fa-chevron-down'} text-muted icon-chevron"></i>
                </div>
            </div>
            <div class="guide-topic-body" id="guide-body-${idx}" style="display: ${isOpen ? 'block' : 'none'};">
                <div class="small text-muted mb-2">${topic.description}</div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="small fw-bold text-info"><i class="fas fa-code me-1"></i>Syntax Reference</span>
                    <button class="syntax-insert-btn" onclick="insertSyntaxSnippet(${idx})" title="Insert snippet into Monaco Editor">
                        <i class="fas fa-paste me-1"></i>Insert to Editor
                    </button>
                </div>
                <pre class="syntax-code-block"><code>${escapedSyntax}</code></pre>
            </div>
        `;
        container.appendChild(card);
    });
}

/** Toggles accordion open/close state */
function toggleGuideTopic(idx) {
    if (activeTopicIndex === idx) {
        // Close if already open
        activeTopicIndex = -1;
    } else {
        activeTopicIndex = idx;
    }
    renderUserGuide();
}

/** Live search/filter topics */
function filterGuideTopics(query) {
    const q = (query || "").toLowerCase().strip ? query.toLowerCase().strip() : (query || "").toLowerCase();
    const container = document.getElementById("guide-topics-accordion");
    if (!container) return;

    PYTHON_SYNTAX_GUIDE.forEach((topic, idx) => {
        const card = document.getElementById(`guide-card-${idx}`);
        if (!card) return;

        const match = topic.title.toLowerCase().includes(q) ||
                      topic.category.toLowerCase().includes(q) ||
                      topic.description.toLowerCase().includes(q) ||
                      topic.syntax.toLowerCase().includes(q);

        card.style.display = match ? "block" : "none";
        if (match && q.length > 1) {
            // Auto open matching card when searching
            const body = document.getElementById(`guide-body-${idx}`);
            if (body) body.style.display = "block";
        }
    });
}

/** Inserts topic syntax snippet into the active Monaco Editor */
function insertSyntaxSnippet(idx) {
    const topic = PYTHON_SYNTAX_GUIDE[idx];
    if (!topic || !window.IDE_STATE.editor) return;

    const editor = window.IDE_STATE.editor;
    const position = editor.getPosition();
    editor.executeEdits("insert-syntax", [
        {
            range: new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column),
            text: topic.syntax + "\n",
            forceMoveMarkers: true
        }
    ]);
    editor.focus();
    showToast(`Inserted '${topic.title}' syntax into editor!`, "success");
}

/** HTML Escape Helper */
function escapeHtml(str) {
    return (str || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize guide when document is ready
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(renderUserGuide, 300);
});
