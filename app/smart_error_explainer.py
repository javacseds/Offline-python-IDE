import re
from typing import Dict, Any, Optional, List

class SmartErrorExplainer:
    """
    Parses Python execution traceback outputs and translates standard Python exceptions
    into beginner-friendly, plain English explanations with actionable recommendations.
    Designed specifically for B.Tech students & CSE lab beginners at GITAMW.
    """

    @staticmethod
    def analyze(traceback_text: str, user_code: str = "") -> Dict[str, Any]:
        if not traceback_text or not traceback_text.strip():
            return {
                "has_error": False,
                "error_type": "",
                "line_number": None,
                "explanation": "",
                "suggestion": "",
                "snippet": ""
            }

        # Extract line number from traceback if present: File "<string>", line X
        line_match = re.search(r'File ".*?", line (\d+)', traceback_text)
        line_number = int(line_match.group(1)) if line_match else None

        # Extract snippet from user code if line number found
        snippet = ""
        if line_number and user_code:
            lines = user_code.splitlines()
            if 0 < line_number <= len(lines):
                snippet = lines[line_number - 1].strip()

        # Extract the main Exception line (last non-empty line of traceback)
        tb_lines = [line.strip() for line in traceback_text.strip().splitlines() if line.strip()]
        error_header = tb_lines[-1] if tb_lines else "Unknown Error"

        error_type = "Python Exception"
        if ":" in error_header:
            error_type = error_header.split(":")[0].strip()

        # Determine explanation & suggestion based on exception type and error header message
        analysis = SmartErrorExplainer._explain_error(error_type, error_header, traceback_text, snippet)
        
        return {
            "has_error": True,
            "error_type": error_type,
            "raw_message": error_header,
            "line_number": line_number,
            "snippet": snippet,
            "explanation": analysis["explanation"],
            "suggestion": analysis["suggestion"],
            "category": analysis["category"],
            "full_traceback": traceback_text
        }

    @staticmethod
    def _explain_error(error_type: str, raw_msg: str, full_tb: str, snippet: str) -> Dict[str, str]:
        msg_lower = raw_msg.lower()

        # Syntax Error
        if "syntaxerror" in error_type.lower():
            if "expected ':'" in msg_lower or "invalid syntax" in msg_lower and snippet and not snippet.endswith(":"):
                if any(kw in snippet for kw in ["if", "elif", "else", "for", "while", "def", "class", "try", "except", "with"]):
                    return {
                        "category": "Syntax Error",
                        "explanation": "You are missing a colon (:) at the end of a block header statement (such as if, for, while, or def).",
                        "suggestion": "Add a colon ':' at the end of line " + snippet
                    }
            if "was never closed" in msg_lower or "unmatched" in msg_lower:
                return {
                    "category": "Syntax Error",
                    "explanation": "You have unbalanced parentheses '()', brackets '[]', braces '{}', or quotes in your code.",
                    "suggestion": "Check line opening and closing brackets or quotation marks to ensure they match."
                }
            return {
                "category": "Syntax Error",
                "explanation": "Python encountered code structure that violates standard Python rules.",
                "suggestion": "Carefully review the syntax on or near this line. Ensure all colons, brackets, and quotes are correctly placed."
            }

        # Indentation Error
        elif "indentationerror" in error_type.lower() or "taberror" in error_type.lower():
            if "expected an indented block" in msg_lower:
                return {
                    "category": "Indentation Error",
                    "explanation": "Python expected an indented block of code inside a block (after if, for, while, def, etc.) but found none.",
                    "suggestion": "Press TAB or insert 4 spaces under the statement header to indent the code inside the block."
                }
            return {
                "category": "Indentation Error",
                "explanation": "Your code indentation is inconsistent or incorrectly aligned.",
                "suggestion": "Use consistent 4-space indentation for code blocks. Avoid mixing spaces and tabs."
            }

        # NameError
        elif "nameerror" in error_type.lower():
            var_match = re.search(r"name '(.*?)' is not defined", raw_msg)
            var_name = var_match.group(1) if var_match else "the variable"
            return {
                "category": "Name Error (Undefined Variable)",
                "explanation": f"You are trying to use '{var_name}' before it was created or defined in your program.",
                "suggestion": f"Define '{var_name}' by assigning it a value before using it (e.g., {var_name} = ...), or check for typos in the name."
            }

        # ZeroDivisionError
        elif "zerodivisionerror" in error_type.lower():
            return {
                "category": "Zero Division Error",
                "explanation": "You are attempting to divide a number by zero or perform a modulo (%) with zero, which is mathematically undefined.",
                "suggestion": "Add a condition to check if the denominator is non-zero before performing division (e.g., if denominator != 0:)."
            }

        # TypeError
        elif "typeerror" in error_type.lower():
            if "unsupported operand type" in msg_lower:
                return {
                    "category": "Type Mismatch Error",
                    "explanation": "You are performing an operation between incompatible data types (e.g., adding a string '5' to an integer 10).",
                    "suggestion": "Convert variables to compatible types using int(), float(), or str() before performing operations."
                }
            return {
                "category": "Type Error",
                "explanation": "An operation or function was applied to an object of inappropriate type, or incorrect function arguments were passed.",
                "suggestion": "Verify variable data types using print(type(var)) and check function parameters."
            }

        # AttributeError
        elif "attributeerror" in error_type.lower():
            return {
                "category": "Attribute Error",
                "explanation": "You are calling a method or property that does not exist on that specific data type or object.",
                "suggestion": "Double check the variable type and verify the method name spelling. (e.g., strings have .lower(), lists have .append())."
            }

        # ModuleNotFoundError / ImportError
        elif "modulenotfounderror" in error_type.lower() or "importerror" in error_type.lower():
            mod_match = re.search(r"no module named '(.*?)'", raw_msg, re.IGNORECASE)
            mod_name = mod_match.group(1) if mod_match else "the package"
            return {
                "category": "Missing Package / Import Error",
                "explanation": f"The Python library or module '{mod_name}' is not installed or cannot be found in your local Python environment.",
                "suggestion": f"Use the Package Manager tab in the top navigation or type '!pip install {mod_name}' to install it locally."
            }

        # IndexError
        elif "indexerror" in error_type.lower():
            return {
                "category": "Index Out of Range Error",
                "explanation": "You tried to access an item in a list or tuple using an index position that does not exist.",
                "suggestion": "Remember Python lists use 0-based indexing (0 to len(my_list) - 1). Check list bounds using len()."
            }

        # KeyError
        elif "keyerror" in error_type.lower():
            key_match = re.search(r"KeyError: (.*)", raw_msg)
            key_val = key_match.group(1) if key_match else "the specified key"
            return {
                "category": "Key Not Found Error",
                "explanation": f"You tried to access dictionary key {key_val}, but it does not exist in the dictionary.",
                "suggestion": "Use dict.get(key) to safely access dictionary keys, or check available keys using dict.keys()."
            }

        # FileNotFoundError
        elif "filenotfounderror" in error_type.lower():
            return {
                "category": "File Not Found Error",
                "explanation": "Python could not find the file or folder directory path specified in your code.",
                "suggestion": "Check the file path spelling and ensure the file exists in your workspace directory."
            }

        # Value Error
        elif "valueerror" in error_type.lower():
            return {
                "category": "Value Error",
                "explanation": "A function received an argument with the right data type, but an inappropriate value (e.g., int('hello')).",
                "suggestion": "Inspect the input value passed into the function to ensure it can be processed validly."
            }

        # Fallback for other errors
        return {
            "category": error_type,
            "explanation": f"Python encountered a runtime error: {raw_msg}",
            "suggestion": "Review the highlighted line and trace values printed before this error step."
        }
