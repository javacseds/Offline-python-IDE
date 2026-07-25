import os
import sys
import time
import tempfile
import subprocess
import psutil
import base64
import glob
from typing import Dict, Any
from app.smart_error_explainer import SmartErrorExplainer

class ExecutionEngine:
    """
    Executes Python programs locally in an isolated subprocess.
    Measures runtime performance (ms), RSS memory consumption (MB),
    captures stdout/stderr, intercepts Matplotlib figures, and triggers
    Smart Error Explanation on exceptions.
    """

    @staticmethod
    def detect_input_calls(code: str) -> int:
        """Count how many input() calls exist in the code (rough scan, ignores comments)."""
        import re
        # Strip single-line comments
        code_no_comments = re.sub(r'#[^\n]*', '', code)
        # Count input( occurrences outside strings (approximate)
        count = len(re.findall(r'\binput\s*\(', code_no_comments))
        return count

    @staticmethod
    def execute(code: str, timeout_seconds: int = 30, stdin_inputs: list = None) -> Dict[str, Any]:

        start_time = time.time()
        
        # Check for pip magic commands inside code editor
        lines = code.splitlines()
        clean_lines = []
        pip_commands = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("!pip ") or stripped.startswith("pip install "):
                pip_commands.append(stripped.lstrip("!"))
            else:
                clean_lines.append(line)

        # If magic pip command found, execute pip install
        if pip_commands and not "".join(clean_lines).strip():
            pip_cmd = pip_commands[0]
            return ExecutionEngine._run_pip_command(pip_cmd)

        clean_code = "\n".join(clean_lines)

        # Create temporary working directory for script execution
        with tempfile.TemporaryDirectory(prefix="gitamw_ide_") as temp_dir:
            script_path = os.path.join(temp_dir, "student_script.py")
            output_img_dir = os.path.join(temp_dir, "plots")
            os.makedirs(output_img_dir, exist_ok=True)

            # Prepend Matplotlib figure hook so plt.show() saves images to temp_dir automatically
            hooked_code = f"""
import os
import sys

# Matplotlib headless plot interceptor for IDE display
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as _plt
    _orig_show = _plt.show
    _plot_count = [0]
    def _custom_show(*args, **kwargs):
        _plot_count[0] += 1
        img_path = os.path.join(r"{output_img_dir}", f"plot_{{_plot_count[0]}}.png")
        _plt.savefig(img_path, bbox_inches='tight', dpi=120)
        _plt.close('all')
    _plt.show = _custom_show
except Exception:
    pass

# --- User Code Execution ---
{clean_code}

# Auto-save active figures if user forgot plt.show()
try:
    import matplotlib.pyplot as _plt
    if _plt.get_fignums():
        img_path = os.path.join(r"{output_img_dir}", "plot_autosave.png")
        _plt.savefig(img_path, bbox_inches='tight', dpi=120)
        _plt.close('all')
except Exception:
    pass
"""
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(hooked_code)

            # Prepare stdin: join user-supplied inputs with newlines
            stdin_text = None
            if stdin_inputs:
                stdin_text = "\n".join(str(v) for v in stdin_inputs) + "\n"

            # Spawn Python subprocess
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                cwd=temp_dir,
                env=dict(os.environ, PYTHONIOENCODING="utf-8")
            )

            # Monitor memory and process completion
            max_memory_mb = 0.0
            p_util = None
            try:
                p_util = psutil.Process(process.pid)
            except Exception:
                pass

            try:
                while process.poll() is None:
                    if p_util:
                        try:
                            mem = p_util.memory_info().rss / (1024 * 1024)
                            if mem > max_memory_mb:
                                max_memory_mb = mem
                        except Exception:
                            pass
                    time.sleep(0.05)
                    if time.time() - start_time > timeout_seconds:
                        process.kill()
                        stdout, stderr = process.communicate()
                        duration = time.time() - start_time
                        has_input = bool(stdin_inputs is None and ExecutionEngine.detect_input_calls("".join(clean_lines)) > 0)
                        return {
                            "status": "Timeout",
                            "stdout": stdout,
                            "stderr": f"TimeoutError: Execution exceeded {timeout_seconds}s.",
                            "duration_seconds": round(duration, 3),
                            "memory_mb": round(max_memory_mb, 2),
                            "plots": [],
                            "smart_error": {
                                "has_error": True,
                                "error_type": "TimeoutError",
                                "category": "Timeout / Waiting for Input",
                                "raw_message": f"Execution exceeded maximum limit of {timeout_seconds}s.",
                                "line_number": None,
                                "explanation": (
                                    "Your program uses input() to read user values. "
                                    "Please provide the input values in the 'Provide Input' box above the Run button, "
                                    "then click Run again."
                                ) if has_input else "Your code ran for too long and was automatically stopped.",
                                "suggestion": (
                                    "Click the 'Provide Input' button, enter each value on a separate line, then click Run."
                                ) if has_input else "Check for infinite loops (while True without break) or very heavy computations."
                            }
                        }

                # Feed stdin and collect output
                try:
                    stdout, stderr = process.communicate(input=stdin_text, timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
            except Exception as e:
                process.kill()
                stdout, stderr = "", str(e)

            duration = time.time() - start_time
            if max_memory_mb == 0.0:
                max_memory_mb = 12.5 # Default fallback baseline RSS

            # Collect generated Matplotlib plot images as Base64 strings
            plot_images = []
            png_files = sorted(glob.glob(os.path.join(output_img_dir, "*.png")))
            for png in png_files:
                try:
                    with open(png, "rb") as img_f:
                        encoded = base64.b64encode(img_f.read()).decode("utf-8")
                        plot_images.append(f"data:image/png;base64,{encoded}")
                except Exception:
                    pass

            # Perform Smart Error Analysis if stderr exists
            smart_error = SmartErrorExplainer.analyze(stderr, clean_code)

            return {
                "status": "Success" if process.returncode == 0 else "Error",
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "duration_seconds": round(duration, 3),
                "memory_mb": round(max_memory_mb, 2),
                "plots": plot_images,
                "smart_error": smart_error
            }

    @staticmethod
    def _run_pip_command(cmd: str) -> Dict[str, Any]:
        """Runs pip command directly from editor."""
        start = time.time()
        full_args = [sys.executable, "-m"] + cmd.split()
        try:
            res = subprocess.run(
                full_args,
                capture_output=True,
                text=True,
                timeout=120
            )
            return {
                "status": "Success" if res.returncode == 0 else "Error",
                "exit_code": res.returncode,
                "stdout": f"[Pip Output]\n{res.stdout}",
                "stderr": res.stderr,
                "duration_seconds": round(time.time() - start, 3),
                "memory_mb": 15.0,
                "plots": [],
                "smart_error": {"has_error": False} if res.returncode == 0 else {
                    "has_error": True,
                    "error_type": "PipInstallError",
                    "explanation": "Package installation failed or encountered an error.",
                    "suggestion": "Check package name spelling or ensure offline wheel package is available."
                }
            }
        except Exception as e:
            return {
                "status": "Error",
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "duration_seconds": round(time.time() - start, 3),
                "memory_mb": 0.0,
                "plots": [],
                "smart_error": {
                    "has_error": True,
                    "error_type": "PipError",
                    "explanation": f"Failed to execute pip command: {str(e)}",
                    "suggestion": "Verify system permissions or package name."
                }
            }
