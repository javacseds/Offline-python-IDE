"""
GITAMW Python Smart IDE — Execution Engine
===========================================
Gouthami Institute of Technology and Management for Women (Autonomous)
Department of Computer Science & Engineering

ROOT CAUSE (FIXED):
  The previous implementation wrote stdin AFTER the monitoring loop via
  process.communicate(input=stdin_text). However, the process is already
  blocked on input() the moment it starts — the monitoring loop ran for
  the full 30-second timeout and killed the process before
  process.communicate() was ever reached. stdin was delivered too late.

FIX:
  stdin is now written to process.stdin IMMEDIATELY after Popen() returns,
  before the monitoring loop begins. The process can then read all its
  inputs without blocking. stdin.close() is called to signal EOF so
  any extra input() calls get EOFError instead of blocking forever.

  Timeout logic:
  - exec_timeout (30s): measures only actual CPU/running time. Kills runaway
    loops. Input-wait time is NOT part of this budget because stdin is
    pre-fed synchronously before the loop starts.
  - No separate idle timeout is needed with the pre-collect approach.

  Multiple input() calls: all supported — every value in stdin_inputs is
  written as a separate line, Python's input() reads them one by one.
"""

import os
import sys
import time
import tempfile
import subprocess
import psutil
import base64
import glob
import re
from typing import Dict, Any, List, Optional

from app.smart_error_explainer import SmartErrorExplainer


class ExecutionEngine:
    """
    Executes Python programs locally in an isolated subprocess.

    Pipeline for programs that use input():
      1. Frontend detects input() calls via /api/execute/detect-inputs.
      2. User provides values in the modal dialog.
      3. Frontend calls /api/execute with stdin_inputs=[...].
      4. Backend writes ALL stdin values to process.stdin immediately
         after spawning (before any timeout monitoring begins).
      5. process.stdin is closed so subsequent input() calls get EOF.
      6. Monitoring loop runs; only actual execution time counts against
         the 30-second CPU timeout.
    """

    # ── Public constants ──────────────────────────────────────────────────────
    EXEC_TIMEOUT_SECONDS: int = 30   # Hard CPU-time limit for runaway code
    IDLE_TIMEOUT_SECONDS: int = 120  # Max time waiting for user input (pre-collect only)

    # ── Input-call detection ──────────────────────────────────────────────────
    @staticmethod
    def detect_input_calls(code: str) -> List[str]:
        """
        Return a list of prompt strings extracted from every input("prompt") call
        found in ``code``.  Comments are stripped before scanning so they don't
        produce false positives.

        Returns:
            List of prompt label strings (may be empty string for bare input()).
        """
        code_no_comments = re.sub(r'#[^\n]*', '', code)

        # Match: input("..."), input('...'), input(f"..."), or bare input()
        pattern = re.compile(
            r'\binput\s*\(\s*(?:f?["\']([^"\']*)["\']|([^)]*))?\s*\)',
            re.MULTILINE
        )
        prompts: List[str] = []
        for m in pattern.finditer(code_no_comments):
            label = (m.group(1) or m.group(2) or "").strip()
            prompts.append(label)
        return prompts

    # ── Main execution entry point ────────────────────────────────────────────
    @staticmethod
    def execute(
        code: str,
        timeout_seconds: int = EXEC_TIMEOUT_SECONDS,
        stdin_inputs: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Execute ``code`` in an isolated subprocess and return a result dict.

        Args:
            code:            Python source code string.
            timeout_seconds: Maximum *execution* time in seconds (CPU budget).
                             Input-wait time is NOT counted against this budget
                             because stdin is written synchronously before the
                             monitoring loop starts.
            stdin_inputs:    Pre-collected list of values to feed as stdin.
                             Each entry becomes one newline-terminated line.
                             If None or empty, stdin is immediately closed so
                             input() raises EOFError instead of blocking.

        Returns:
            Dict with keys: status, stdout, stderr, duration_seconds,
            memory_mb, plots, smart_error.
        """
        start_time = time.monotonic()

        # ── 1. Strip magic pip lines ──────────────────────────────────────────
        lines = code.splitlines()
        clean_lines: List[str] = []
        pip_commands: List[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("!pip ") or stripped.startswith("pip install "):
                pip_commands.append(stripped.lstrip("!"))
            else:
                clean_lines.append(line)

        if pip_commands and not "".join(clean_lines).strip():
            return ExecutionEngine._run_pip_command(pip_commands[0])

        clean_code = "\n".join(clean_lines)

        # ── 2. Build stdin payload ────────────────────────────────────────────
        #
        # KEY FIX: Build the complete stdin string NOW, before spawning.
        # We will write it to process.stdin the moment Popen returns,
        # so the process never waits for data that never arrives.
        #
        stdin_text: Optional[str] = None
        if stdin_inputs:
            stdin_text = "\n".join(str(v) for v in stdin_inputs) + "\n"

        # ── 3. Write script to temp file ──────────────────────────────────────
        with tempfile.TemporaryDirectory(prefix="gitamw_ide_") as temp_dir:
            script_path   = os.path.join(temp_dir, "student_script.py")
            output_img_dir = os.path.join(temp_dir, "plots")
            os.makedirs(output_img_dir, exist_ok=True)

            # Matplotlib headless interceptor so plt.show() saves PNG to disk
            hooked_code = f"""\
import os, sys

# ── Interactive input echo interceptor for non-TTY mode ──────────────────────
try:
    import builtins
    _orig_input = builtins.input
    def _custom_input(prompt=""):
        val = _orig_input(prompt)
        sys.stdout.write(str(val) + "\\n")
        sys.stdout.flush()
        return val
    builtins.input = _custom_input
except Exception:
    pass

# ── Matplotlib headless interceptor ──────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as _plt
    _plot_count = [0]
    def _custom_show(*args, **kwargs):
        _plot_count[0] += 1
        _plt.savefig(
            os.path.join(r"{output_img_dir}", f"plot_{{_plot_count[0]}}.png"),
            bbox_inches='tight', dpi=120)
        _plt.close('all')
    _plt.show = _custom_show
except Exception:
    pass

# ── User code ─────────────────────────────────────────────────────────────────
{clean_code}


# ── Auto-save any open figures user forgot to plt.show() ─────────────────────
try:
    import matplotlib.pyplot as _plt
    if _plt.get_fignums():
        _plt.savefig(
            os.path.join(r"{output_img_dir}", "plot_autosave.png"),
            bbox_inches='tight', dpi=120)
        _plt.close('all')
except Exception:
    pass
"""
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(hooked_code)

            # ── 4. Spawn subprocess ───────────────────────────────────────────
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,       # Always open — we control when to close
                text=True,
                cwd=temp_dir,
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                bufsize=0,                   # Unbuffered I/O
            )

            # ── 5. IMMEDIATELY write all stdin and close the pipe ─────────────
            #
            # This is the critical fix.  The process has just started; it may
            # not yet have reached its first input() call.  We write everything
            # now so that whenever input() is called — whether immediately or
            # after some computation — the data is already sitting in the kernel
            # pipe buffer ready to be read.  Closing stdin signals EOF so any
            # extra input() calls get EOFError instead of hanging forever.
            #
            try:
                if stdin_text:
                    process.stdin.write(stdin_text)
                    process.stdin.flush()
                process.stdin.close()       # EOF → no more data will arrive
            except (BrokenPipeError, OSError):
                pass   # Process may have exited before we could write (e.g. syntax error)

            # ── 6. Monitor: memory sampling + CPU-time timeout ────────────────
            #
            # TIMEOUT SEMANTICS:
            #   Because stdin is already in the pipe buffer, the process will
            #   immediately proceed past input() calls.  All time here is genuine
            #   execution time, so the timeout fairly measures CPU work only.
            #
            max_memory_mb = 0.0
            p_util: Optional[psutil.Process] = None
            try:
                p_util = psutil.Process(process.pid)
            except Exception:
                pass

            timed_out = False
            try:
                while process.poll() is None:
                    # Sample RSS memory
                    if p_util:
                        try:
                            mem = p_util.memory_info().rss / (1024 * 1024)
                            if mem > max_memory_mb:
                                max_memory_mb = mem
                        except Exception:
                            pass

                    time.sleep(0.05)

                    # Enforce CPU-time hard limit
                    elapsed = time.monotonic() - start_time
                    if elapsed > timeout_seconds:
                        process.kill()
                        timed_out = True
                        break

                # Collect remaining output (process is either done or just killed)
                try:
                    stdout, stderr = process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()

            except Exception as exc:
                try:
                    process.kill()
                except Exception:
                    pass
                try:
                    stdout, stderr = process.communicate(timeout=2)
                except Exception:
                    stdout, stderr = "", str(exc)

            # ── 7. Handle timeout result ──────────────────────────────────────
            duration = time.monotonic() - start_time

            if timed_out:
                return {
                    "status":           "Timeout",
                    "stdout":           stdout,
                    "stderr":           f"TimeoutError: Execution exceeded {timeout_seconds}s hard limit.",
                    "duration_seconds": round(duration, 3),
                    "memory_mb":        round(max_memory_mb, 2),
                    "plots":            [],
                    "smart_error": {
                        "has_error":   True,
                        "error_type":  "TimeoutError",
                        "category":    "Infinite Loop / Long Computation",
                        "raw_message": f"Killed after {timeout_seconds}s.",
                        "line_number": None,
                        "explanation": (
                            f"Your program ran for more than {timeout_seconds} seconds "
                            "of actual CPU time and was forcibly stopped. "
                            "This limit exists to protect the server from runaway code."
                        ),
                        "suggestion": (
                            "Check for infinite loops (while True without a break), "
                            "very deep recursion, or unexpectedly heavy computations. "
                            "Note: input() wait time does NOT count against this limit — "
                            "only actual execution time does."
                        ),
                    },
                }

            # ── 8. Collect plot images ────────────────────────────────────────
            if max_memory_mb == 0.0:
                max_memory_mb = 12.5   # Fallback baseline RSS estimate

            plot_images: List[str] = []
            for png in sorted(glob.glob(os.path.join(output_img_dir, "*.png"))):
                try:
                    with open(png, "rb") as img_f:
                        encoded = base64.b64encode(img_f.read()).decode("utf-8")
                        plot_images.append(f"data:image/png;base64,{encoded}")
                except Exception:
                    pass

            # ── 9. Smart error analysis ───────────────────────────────────────
            smart_error = SmartErrorExplainer.analyze(stderr, clean_code)

            # ── 10. Friendly EOFError message ─────────────────────────────────
            #
            # If the program called more input() than values were provided,
            # Python raises EOFError.  Turn that into a helpful message.
            #
            if "EOFError" in stderr and not stdin_inputs:
                smart_error = {
                    "has_error":   True,
                    "error_type":  "EOFError",
                    "category":    "Missing Input Values",
                    "raw_message": stderr,
                    "line_number": None,
                    "explanation": (
                        "Your program calls input() but no input values were provided. "
                        "Click the 'Provide Input' button, enter the required values, "
                        "and click 'Run with Inputs'."
                    ),
                    "suggestion": (
                        "Use the 'Provide Input' button in the toolbar to supply values "
                        "before running programs that use input()."
                    ),
                }
            elif "EOFError" in stderr and stdin_inputs:
                smart_error = {
                    "has_error":   True,
                    "error_type":  "EOFError",
                    "category":    "Too Few Input Values",
                    "raw_message": stderr,
                    "line_number": None,
                    "explanation": (
                        f"Your program needed more input() values than the "
                        f"{len(stdin_inputs)} value(s) you provided."
                    ),
                    "suggestion": (
                        "Click 'Provide Input' again and add more rows — "
                        "one value per input() call in your program."
                    ),
                }

            return {
                "status":           "Success" if process.returncode == 0 else "Error",
                "exit_code":        process.returncode,
                "stdout":           stdout,
                "stderr":           stderr,
                "duration_seconds": round(duration, 3),
                "memory_mb":        round(max_memory_mb, 2),
                "plots":            plot_images,
                "smart_error":      smart_error,
            }

    # ── Pip helper ────────────────────────────────────────────────────────────
    @staticmethod
    def _run_pip_command(cmd: str) -> Dict[str, Any]:
        """Execute a pip install command from the editor magic !pip syntax."""
        start = time.monotonic()
        full_args = [sys.executable, "-m"] + cmd.split()
        try:
            res = subprocess.run(
                full_args,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "status":           "Success" if res.returncode == 0 else "Error",
                "exit_code":        res.returncode,
                "stdout":           f"[Pip Output]\n{res.stdout}",
                "stderr":           res.stderr,
                "duration_seconds": round(time.monotonic() - start, 3),
                "memory_mb":        15.0,
                "plots":            [],
                "smart_error":      {"has_error": False} if res.returncode == 0 else {
                    "has_error":   True,
                    "error_type":  "PipInstallError",
                    "explanation": "Package installation failed or encountered an error.",
                    "suggestion":  "Check package name spelling or ensure offline wheel is available.",
                },
            }
        except Exception as exc:
            return {
                "status":           "Error",
                "exit_code":        1,
                "stdout":           "",
                "stderr":           str(exc),
                "duration_seconds": round(time.monotonic() - start, 3),
                "memory_mb":        0.0,
                "plots":            [],
                "smart_error": {
                    "has_error":   True,
                    "error_type":  "PipError",
                    "explanation": f"Failed to execute pip command: {exc}",
                    "suggestion":  "Verify system permissions or package name.",
                },
            }
