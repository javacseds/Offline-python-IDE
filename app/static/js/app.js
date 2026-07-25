/**
 * GITAMW Python Smart IDE - Main Application Logic
 * Department of Computer Science & Engineering
 * Gouthami Institute of Technology for Women (Autonomous), Proddatur
 */

// Global Application State
window.IDE_STATE = {
    student: null,
    editor: null,
    currentFileName: "untitled.py",
    currentFilePath: null,
    isSampleFile: false,
    lastExecutionResult: null,
    theme: "vs-dark",
    fontSize: 14
};

document.addEventListener("DOMContentLoaded", () => {
    initClock();
    setupLoginForm();
    setupTabSwitching();
    setupConsoleResizer();
});

// --- Live Clock & Date Updater ---
function initClock() {
    const updateTime = () => {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const dateStr = now.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
        
        const elTime = document.getElementById("status-clock");
        const elDate = document.getElementById("header-date");
        if (elTime) elTime.textContent = timeStr;
        if (elDate) elDate.textContent = dateStr;
    };
    updateTime();
    setInterval(updateTime, 1000);
}

// --- Login & Student Validation ---
function setupLoginForm() {
    const loginForm = document.getElementById("student-login-form");
    const resetBtn = document.getElementById("btn-reset-login");

    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            loginForm.reset();
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const name = document.getElementById("login-name").value.trim();
            const roll = document.getElementById("login-roll").value.trim().toUpperCase();
            const branch = document.getElementById("login-branch").value;
            const year = document.getElementById("login-year").value;
            const semester = document.getElementById("login-semester").value;
            const section = document.getElementById("login-section").value;
            const email = document.getElementById("login-email").value.trim();
            const mobile = document.getElementById("login-mobile").value.trim();
            const agreed = document.getElementById("login-agreed").checked;

            // Student Validation Rules
            if (!name) {
                showToast("❌ Student Name cannot be empty", "danger");
                return;
            }
            if (!roll || roll.length < 5) {
                showToast("❌ Enter a valid Roll Number (e.g. 212M1A0501)", "danger");
                return;
            }
            if (!year) {
                showToast("❌ Select a valid Year", "danger");
                return;
            }
            if (!semester) {
                showToast("❌ Select a valid Semester", "danger");
                return;
            }
            if (!agreed) {
                showToast("❌ You must agree to the Academic Integrity Policy", "warning");
                return;
            }

            const payload = {
                name: name,
                roll_number: roll,
                branch: branch,
                year: year,
                semester: semester,
                section: section,
                email: email,
                mobile: mobile,
                agreed_policy: agreed
            };

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (res.ok && data.success) {
                    showToast(`Welcome, ${data.student.name}!`, "success");
                    localStorage.setItem("gitamw_student_profile", JSON.stringify(data.student));
                    
                    document.getElementById("login-screen").style.display = "none";
                    document.getElementById("main-ide-app").style.display = "flex";
                    
                    window.initializeIDEApp(data.student);
                } else {
                    showToast(data.detail || "Login failed. Check your details.", "danger");
                }
            } catch (err) {
                showToast("❌ Network or server error during login.", "danger");
            }
        });
    }
}

// --- Initialize IDE Application ---
window.initializeIDEApp = function (studentProfile) {
    window.IDE_STATE.student = studentProfile;
    updateStudentHeaderBadge(studentProfile);
    
    initMonacoEditor();
    loadWorkspaceFiles();
    loadPackageList();
    loadHistoryLog();
    setupKeyboardShortcuts();
};

function updateStudentHeaderBadge(student) {
    if (!student) return;
    const badge = document.getElementById("student-profile-badge");
    if (badge) {
        badge.innerHTML = `
            <i class="fas fa-user-graduate text-warning"></i>
            <strong>${student.name}</strong> (${student.roll_number}) | 
            <span class="badge bg-light text-dark">${student.branch} ${student.year}Yr/Sem${student.semester} (${student.section})</span>
        `;
    }
}

// --- Monaco Editor Initialization ---
function initMonacoEditor() {
    if (window.IDE_STATE.editor) return;

    const container = document.getElementById('monaco-editor-wrapper');
    if (!container) return;

    const initialCode = `# GITAMW Python Smart IDE
# Gouthami Institute of Technology for Women (Autonomous), Proddatur
# Write your Python program below and press F5 or Ctrl+Enter to execute!

def welcome_student(name, roll_no):
    print(f"Welcome {name} ({roll_no}) to Department of CSE!")
    print("Python Smart IDE is ready for execution.")

welcome_student("${window.IDE_STATE.student ? window.IDE_STATE.student.name : 'Student'}", "${window.IDE_STATE.student ? window.IDE_STATE.student.roll_number : '212M1A0501'}")
`;

    try {
        if (typeof require !== 'undefined' && require.config) {
            require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });

            require(['vs/editor/editor.main'], function () {
                if (window.IDE_STATE.editor) return;
                window.IDE_STATE.editor = monaco.editor.create(container, {
                    value: initialCode,
                    language: 'python',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    fontSize: 14,
                    minimap: { enabled: false },
                    lineNumbers: 'on',
                    roundedSelection: true,
                    scrollBeyondLastLine: false,
                    tabSize: 4
                });

                window.IDE_STATE.editor.onDidChangeCursorPosition((e) => {
                    const pos = e.position;
                    const elPos = document.getElementById("status-cursor-pos");
                    if (elPos) elPos.textContent = `Ln ${pos.lineNumber}, Col ${pos.column}`;
                });
            }, function (err) {
                console.warn("CDN Monaco load failed, falling back to textarea:", err);
                createFallbackTextarea(container, initialCode);
            });
        } else {
            createFallbackTextarea(container, initialCode);
        }
    } catch (err) {
        console.warn("Monaco initialization failed, using textarea fallback:", err);
        createFallbackTextarea(container, initialCode);
    }
}

function createFallbackTextarea(container, initialCode) {
    if (window.IDE_STATE.editor) return;
    container.innerHTML = `<textarea id="fallback-code-editor" class="form-control font-monospace text-light bg-dark h-100 p-3" style="resize:none; border:none; outline:none; font-family: monospace; font-size: 14px; line-height: 1.5;"></textarea>`;
    const textarea = document.getElementById("fallback-code-editor");
    textarea.value = initialCode;

    window.IDE_STATE.editor = {
        getValue: () => textarea.value,
        setValue: (val) => { textarea.value = val; },
        focus: () => textarea.focus()
    };
}

// --- Program Execution Handler ---
async function runProgram(stdinInputs = null) {
    if (!window.IDE_STATE.editor) return;
    const code = window.IDE_STATE.editor.getValue();
    const fileName = window.IDE_STATE.currentFileName;

    // Auto-detect input() calls if no stdin provided
    if (stdinInputs === null) {
        try {
            const detectRes = await fetch("/api/execute/detect-inputs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code, program_name: fileName })
            });
            const detectData = await detectRes.json();
            if (detectData.needs_input) {
                openInputDialog(detectData.prompts);
                return; // Stop — wait for user to provide inputs in the dialog
            }
        } catch (e) {
            // Detection failed; run anyway without stdin
        }
    }

    const btnRun = document.getElementById("btn-run-code");
    if (btnRun) {
        btnRun.disabled = true;
        btnRun.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Running...`;
    }

    const outputConsole = document.getElementById("output-console-body");
    const telemetryStatus = document.getElementById("status-execution-telemetry");
    if (outputConsole) outputConsole.textContent = "⏳ Executing program locally...\n";

    try {
        const res = await fetch("/api/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                code: code,
                program_name: fileName,
                stdin_inputs: stdinInputs
            })
        });
        const result = await res.json();
        window.IDE_STATE.lastExecutionResult = result;

        // Render Console Output
        let consoleText = "";
        if (result.stdout) consoleText += result.stdout;
        if (result.stderr) consoleText += `\n[STDERR / TRACEBACK]\n${result.stderr}`;
        if (!result.stdout && !result.stderr) consoleText = "[Program completed with no output]";

        if (outputConsole) outputConsole.textContent = consoleText;

        // Telemetry Update
        if (telemetryStatus) {
            telemetryStatus.innerHTML = `
                <span class="badge ${result.status === 'Success' ? 'bg-success' : 'bg-danger'}">${result.status}</span>
                <span><i class="fas fa-clock text-warning"></i> ${result.duration_seconds}s</span>
                <span><i class="fas fa-memory text-info"></i> ${result.memory_mb} MB</span>
            `;
        }

        // Render Matplotlib Plots if generated
        renderPlots(result.plots);

        // Render Smart Error Explainer if error occurred
        renderSmartError(result.smart_error);

        // Reload History
        loadHistoryLog();

        showToast(result.status === "Success" ? "Program executed successfully!" : "Execution encountered an error.", result.status === "Success" ? "success" : "danger");

    } catch (err) {
        if (outputConsole) outputConsole.textContent = `❌ Execution Error: ${err.message}`;
    } finally {
        if (btnRun) {
            btnRun.disabled = false;
            btnRun.innerHTML = `<i class="fas fa-play text-success"></i> Run (F5)`;
        }
    }
}

// --- Render Matplotlib Plots ---
function renderPlots(plots) {
    const container = document.getElementById("plots-container");
    if (!container) return;
    container.innerHTML = "";

    if (!plots || plots.length === 0) {
        container.innerHTML = `<div class="text-muted p-3 text-center">No graphical plots generated in this execution. Use <code>matplotlib.pyplot.show()</code> to view charts here.</div>`;
        return;
    }

    plots.forEach((base64Img, idx) => {
        const card = document.createElement("div");
        card.className = "card mb-3 p-2 bg-dark border-secondary text-center";
        card.innerHTML = `
            <div class="card-header py-1 text-light fs-6">Figure ${idx + 1}</div>
            <div class="card-body p-1">
                <img src="${base64Img}" class="img-fluid rounded" alt="Matplotlib Plot ${idx + 1}" style="max-height: 400px;"/>
            </div>
        `;
        container.appendChild(card);
    });

    // Switch tab to plots
    switchOutputTab('plots');
}

// --- Smart Error Explainer Rendering ---
function renderSmartError(smartErr) {
    const box = document.getElementById("smart-error-explainer-box");
    if (!box) return;

    if (!smartErr || !smartErr.has_error) {
        box.innerHTML = `<div class="text-success p-3"><i class="fas fa-check-circle me-2"></i> No syntax or runtime errors detected in your code. Good job!</div>`;
        return;
    }

    box.innerHTML = `
        <div class="smart-error-box">
            <div class="smart-error-title">
                <i class="fas fa-exclamation-triangle"></i> ${smartErr.category || smartErr.error_type || 'Python Error'}
            </div>
            <div class="mt-2"><strong>Error Message:</strong> <code>${smartErr.raw_message || 'Exception raised'}</code></div>
            ${smartErr.line_number ? `<div class="mt-1 text-warning"><strong>Line Number:</strong> Line ${smartErr.line_number} ${smartErr.snippet ? `<code>${smartErr.snippet}</code>` : ''}</div>` : ''}
            <div class="mt-3 fs-6"><strong>Explanation for Beginner Students:</strong></div>
            <div class="text-light">${smartErr.explanation}</div>
            <div class="smart-suggestion-box">
                <strong>💡 Actionable Recommendation / Suggestion:</strong>
                <div>${smartErr.suggestion}</div>
            </div>
        </div>
    `;

    // Switch tab to Smart Error
    switchOutputTab('smart-error');
}

// --- Workspace File Explorer ---
async function loadWorkspaceFiles() {
    try {
        const res = await fetch("/api/files/list");
        const data = await res.json();

        // Render Saved Files
        const savedContainer = document.getElementById("saved-files-list");
        if (savedContainer) {
            savedContainer.innerHTML = "";
            if (data.saved.length === 0) {
                savedContainer.innerHTML = `<div class="text-muted small p-2">No saved programs yet. Click Save to store code.</div>`;
            } else {
                data.saved.forEach(file => {
                    const item = document.createElement("div");
                    item.className = `file-item ${window.IDE_STATE.currentFileName === file.name && !window.IDE_STATE.isSampleFile ? 'active' : ''}`;
                    item.innerHTML = `
                        <span><i class="fab fa-python text-warning me-2"></i>${file.name}</span>
                        <button class="btn btn-sm text-danger py-0 px-1" onclick="deleteFile('${file.name}', event)"><i class="fas fa-trash"></i></button>
                    `;
                    item.onclick = () => openFile(file.name, false);
                    savedContainer.appendChild(item);
                });
            }
        }

        // Render GITAMW Sample Programs
        const sampleContainer = document.getElementById("sample-files-list");
        if (sampleContainer) {
            sampleContainer.innerHTML = "";
            data.samples.forEach(file => {
                const item = document.createElement("div");
                item.className = `file-item ${window.IDE_STATE.currentFileName === file.name && window.IDE_STATE.isSampleFile ? 'active' : ''}`;
                item.innerHTML = `<span><i class="fas fa-book-open text-info me-2"></i>${file.name}</span>`;
                item.onclick = () => openFile(file.name, true);
                sampleContainer.appendChild(item);
            });
        }
    } catch (err) {
        console.error("Failed to load workspace files:", err);
    }
}

function updateFileNameBadge(filename, isSample = false) {
    const textEl = document.getElementById("current-filename-text");
    if (textEl) {
        textEl.textContent = `${filename}${isSample ? ' (Sample Read-Only)' : ''}`;
    }
}

function createNewFile() {
    let name = prompt("Enter new Python filename:", "my_program.py");
    if (name === null) return;
    name = name.trim();
    if (!name) name = "new_program.py";
    if (!name.endsWith(".py")) name += ".py";

    window.IDE_STATE.currentFileName = name;
    window.IDE_STATE.isSampleFile = false;

    const initialTemplate = `# Python File: ${name}
# Gowthami Institute of Technology and Management for Women (Autonomous)

def main():
    print("Hello from ${name}!")

if __name__ == "__main__":
    main()
`;

    if (window.IDE_STATE.editor) {
        window.IDE_STATE.editor.setValue(initialTemplate);
    }

    updateFileNameBadge(name, false);
    loadWorkspaceFiles();
    showToast(`Created new file '${name}'. Press Ctrl+S or click Save to store.`, "success");
}

function renameCurrentFile() {
    if (window.IDE_STATE.isSampleFile) {
        showToast("Sample lab experiments are read-only and cannot be renamed directly.", "warning");
        return;
    }

    let newName = prompt("Enter new filename:", window.IDE_STATE.currentFileName || "my_program.py");
    if (newName === null) return;
    newName = newName.trim();
    if (!newName) return;
    if (!newName.endsWith(".py")) newName += ".py";

    window.IDE_STATE.currentFileName = newName;
    updateFileNameBadge(newName, false);
    loadWorkspaceFiles();
    showToast(`Renamed file to '${newName}'. Click Save to confirm storage.`, "info");
}

async function openFile(filename, isSample) {
    try {
        const res = await fetch(`/api/files/read?name=${encodeURIComponent(filename)}&sample=${isSample}`);
        if (!res.ok) {
            const errData = await res.json();
            showToast(errData.detail || `Failed to open file ${filename}`, "danger");
            return;
        }
        const data = await res.json();
        if (window.IDE_STATE.editor) {
            window.IDE_STATE.editor.setValue(data.content);
            window.IDE_STATE.currentFileName = data.filename;
            window.IDE_STATE.isSampleFile = isSample;

            updateFileNameBadge(data.filename, isSample);
            loadWorkspaceFiles();
            showToast(`Opened ${data.filename}`, "info");
        }
    } catch (err) {
        showToast(`Failed to open file ${filename}`, "danger");
    }
}

async function saveCurrentFile() {
    if (!window.IDE_STATE.editor) return;
    let filename = window.IDE_STATE.currentFileName;
    
    if (window.IDE_STATE.isSampleFile || filename === "untitled.py") {
        const inputName = prompt("Enter file name to save:", "my_program.py");
        if (!inputName) return;
        filename = inputName.trim();
        if (!filename.endsWith(".py")) filename += ".py";
    }

    const content = window.IDE_STATE.editor.getValue();
    try {
        const res = await fetch("/api/files/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: filename, content: content })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            window.IDE_STATE.currentFileName = data.file.filename;
            window.IDE_STATE.isSampleFile = false;
            
            updateFileNameBadge(data.file.filename, false);
            loadWorkspaceFiles();
            showToast(`Saved file '${data.file.filename}' to local disk!`, "success");
        }
    } catch (err) {
        showToast("Error saving file", "danger");
    }
}

async function deleteFile(filename, event) {
    if (event) event.stopPropagation();
    if (!confirm(`Are you sure you want to delete '${filename}'?`)) return;

    try {
        const res = await fetch(`/api/files/delete?filename=${encodeURIComponent(filename)}`, { method: "DELETE" });
        if (res.ok) {
            showToast(`Deleted file '${filename}'`, "info");
            if (window.IDE_STATE.currentFileName === filename) {
                window.IDE_STATE.currentFileName = "untitled.py";
                window.IDE_STATE.editor.setValue("# New Python File\n");
            }
            loadWorkspaceFiles();
        }
    } catch (err) {
        showToast("Failed to delete file", "danger");
    }
}

// --- Package Manager UI ---
async function loadPackageList() {
    const container = document.getElementById("packages-card-list");
    if (!container) return;

    try {
        const res = await fetch("/api/packages/list");
        const data = await res.json();
        
        container.innerHTML = "";
        data.packages.forEach(pkg => {
            const card = document.createElement("div");
            card.className = "card mb-2 bg-dark border-secondary text-light p-2 fs-6";
            card.innerHTML = `
                <div class="d-flex align-items-center justify-content-between">
                    <div>
                        <strong>${pkg.name}</strong> 
                        <span class="badge ${pkg.is_installed ? 'bg-success' : 'bg-secondary'} ms-2">${pkg.version}</span>
                        <div class="small text-muted">${pkg.description}</div>
                    </div>
                    <button class="btn btn-sm ${pkg.is_installed ? 'btn-outline-success' : 'btn-warning'}" 
                            onclick="installPackage('${pkg.module_name}')" ${pkg.is_installed ? 'disabled' : ''}>
                        ${pkg.is_installed ? '<i class="fas fa-check"></i> Installed' : '<i class="fas fa-download"></i> Install'}
                    </button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load packages:", err);
    }
}

async function installPackage(pkgName) {
    if (!pkgName) {
        pkgName = document.getElementById("custom-package-input").value.trim();
    }
    if (!pkgName) {
        showToast("Enter a package name to install", "warning");
        return;
    }

    showToast(`Installing package '${pkgName}' locally...`, "info");
    try {
        const res = await fetch("/api/packages/install", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ package_name: pkgName })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, "success");
            loadPackageList();
        } else {
            showToast(data.message || "Installation failed.", "danger");
        }
    } catch (err) {
        showToast("Error installing package.", "danger");
    }
}

// --- History Log Handler ---
async function loadHistoryLog() {
    const container = document.getElementById("history-log-list");
    if (!container) return;

    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        
        container.innerHTML = "";
        if (data.history.length === 0) {
            container.innerHTML = `<div class="text-muted p-2">No execution history recorded yet.</div>`;
            return;
        }

        data.history.forEach(item => {
            const card = document.createElement("div");
            card.className = `card mb-2 p-2 bg-dark text-light border-${item.status === 'Success' ? 'success' : 'danger'}`;
            card.innerHTML = `
                <div class="d-flex justify-content-between small">
                    <strong>${item.program_name}</strong>
                    <span class="badge ${item.status === 'Success' ? 'bg-success' : 'bg-danger'}">${item.status}</span>
                </div>
                <div class="small text-muted mt-1">${item.timestamp} | ${item.duration_seconds}s | ${item.memory_mb} MB</div>
                <code class="d-block mt-1 text-info small">${item.code_snippet}</code>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}

// --- PDF Report Export Options & Download ---
function openExportModal() {
    const overlay = document.getElementById("export-modal-overlay");
    if (overlay) overlay.style.display = "flex";
}

function closeExportModal() {
    const overlay = document.getElementById("export-modal-overlay");
    if (overlay) overlay.style.display = "none";
}

function closeExportModalOnOverlay(event) {
    if (event.target && event.target.id === "export-modal-overlay") {
        closeExportModal();
    }
}

function selectExportOption(filter) {
    const radio = document.getElementById(filter === 'today' ? 'export-today' : 'export-all');
    if (radio) radio.checked = true;
}

async function confirmDownloadReport() {
    const selectedRadio = document.querySelector('input[name="exportFilter"]:checked');
    const filter = selectedRadio ? selectedRadio.value : 'today';
    closeExportModal();
    await downloadExecutionReport(filter);
}

async function downloadExecutionReport(filter = 'today') {
    const filterName = filter === 'today' ? "Today's Programs" : "All Programs";
    showToast(`Generating PDF lab report (${filterName})...`, "info");

    const payload = {
        code: window.IDE_STATE.editor ? window.IDE_STATE.editor.getValue() : "",
        program_name: window.IDE_STATE.currentFileName || "untitled.py",
        filter: filter
    };

    try {
        const res = await fetch("/api/export/report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            let errorMsg = "No programs found to export.";
            try {
                const errData = await res.json();
                if (errData && errData.detail) errorMsg = errData.detail;
            } catch (e) {}
            showToast(`⚠️ ${errorMsg}`, "warning");
            return;
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const roll = window.IDE_STATE.student ? window.IDE_STATE.student.roll_number : "Session";
        const scopeTag = filter === 'today' ? 'Today' : 'All';
        a.download = `GITAMW_${roll}_Report_${scopeTag}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast("✅ PDF Lab Report downloaded successfully!", "success");
    } catch (err) {
        showToast("❌ Failed to export PDF report: " + err.message, "danger");
    }
}

// --- Console Resizer Drag Handle ---
function setupConsoleResizer() {
    const resizer = document.getElementById("console-resizer");
    const outputPanel = document.getElementById("bottom-output-panel");
    if (!resizer || !outputPanel) return;

    let isResizing = false;
    let startY = 0;
    let startHeight = 0;

    resizer.addEventListener("mousedown", (e) => {
        isResizing = true;
        startY = e.clientY;
        startHeight = outputPanel.offsetHeight;
        resizer.classList.add("resizing");
        document.body.style.cursor = "ns-resize";
        document.body.style.userSelect = "none";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isResizing) return;
        const dy = startY - e.clientY;
        const newHeight = Math.max(80, Math.min(window.innerHeight * 0.75, startHeight + dy));
        outputPanel.style.height = `${newHeight}px`;

        if (window.IDE_STATE.editor && typeof window.IDE_STATE.editor.layout === "function") {
            window.IDE_STATE.editor.layout();
        }
    });

    document.addEventListener("mouseup", () => {
        if (isResizing) {
            isResizing = false;
            resizer.classList.remove("resizing");
            document.body.style.cursor = "";
            document.body.style.userSelect = "";
            if (window.IDE_STATE.editor && typeof window.IDE_STATE.editor.layout === "function") {
                window.IDE_STATE.editor.layout();
            }
        }
    });
}

// --- Keyboard Shortcuts & Utilities ---
function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        // F5 or Ctrl+Enter -> Run Code
        if (e.key === "F5" || (e.ctrlKey && e.key === "Enter")) {
            e.preventDefault();
            runProgram();
        }
        // Ctrl+S -> Save File
        if (e.ctrlKey && e.key.toLowerCase() === "s") {
            e.preventDefault();
            saveCurrentFile();
        }
        // Ctrl+L -> Clear Output
        if (e.ctrlKey && e.key.toLowerCase() === "l") {
            e.preventDefault();
            clearOutputConsole();
        }
    });
}

function clearOutputConsole() {
    const consoleBody = document.getElementById("output-console-body");
    const plotsBox = document.getElementById("plots-container");
    const smartBox = document.getElementById("smart-error-explainer-box");

    if (consoleBody) consoleBody.textContent = "[Console Output Cleared]";
    if (plotsBox) plotsBox.innerHTML = "";
    if (smartBox) smartBox.innerHTML = "";
    showToast("Console cleared.", "info");
}

function setupTabSwitching() {
    // Sidebar Tabs
    const sideBtns = document.querySelectorAll(".sidebar-tab-btn");
    sideBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            sideBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const targetTab = btn.getAttribute("data-tab");
            document.querySelectorAll(".sidebar-tab-pane").forEach(pane => {
                pane.style.display = pane.id === `tab-pane-${targetTab}` ? "block" : "none";
            });
        });
    });
}

function switchOutputTab(tabName) {
    const btns = document.querySelectorAll(".output-tab-btn");
    btns.forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-output-tab") === tabName);
    });
    
    document.querySelectorAll(".output-tab-pane").forEach(pane => {
        pane.style.display = pane.id === `output-tab-${tabName}` ? "block" : "none";
    });
}

function toggleAppTheme() {
    document.body.classList.toggle("dark-mode");
    const isDark = document.body.classList.contains("dark-mode");
    if (window.IDE_STATE.editor) {
        monaco.editor.setTheme(isDark ? "vs-dark" : "vs");
    }
}

// --- Logout Student Session ---
function logoutStudent() {
    localStorage.removeItem("gitamw_student_profile");
    location.reload();
}

// --- Toast Notification Helper ---
function showToast(message, type = "info") {
    const toastContainer = document.getElementById("toast-container");
    if (!toastContainer) return;

    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-white bg-${type} border-0 show mb-2`;
    toast.role = "alert";
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body font-weight-bold">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// --- Syllabus PDF Upload & Viewer ---
function uploadSyllabus(input) {
    const file = input.files[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
        showToast("❌ Only PDF files are supported for syllabus upload.", "danger");
        input.value = "";
        return;
    }

    const url = URL.createObjectURL(file);
    const container = document.getElementById("syllabus-viewer-container");
    if (!container) return;

    container.innerHTML = `
        <div class="d-flex align-items-center justify-content-between px-2 py-1" style="background:#1e293b; font-size:0.78rem;">
            <span class="text-info"><i class="fas fa-file-pdf text-danger me-1"></i>${file.name}</span>
            <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="clearSyllabus()" title="Remove Syllabus"><i class="fas fa-times"></i></button>
        </div>
        <iframe src="${url}" title="Syllabus PDF Viewer"></iframe>
    `;
    showToast("✅ Syllabus uploaded successfully!", "success");
}

function clearSyllabus() {
    const container = document.getElementById("syllabus-viewer-container");
    const input = document.getElementById("syllabus-file-input");
    if (container) {
        container.innerHTML = `
            <div class="text-muted small text-center p-3">
                <i class="fas fa-file-pdf fa-2x mb-2 d-block text-danger"></i>
                No syllabus uploaded yet.<br>Upload a PDF to view it here.
            </div>
        `;
    }
    if (input) input.value = "";
}

// --- Editor Settings ---
function applyEditorSetting(setting, value) {
    if (setting === 'fontSize') {
        const size = parseInt(value);
        const label = document.getElementById("editor-font-size-val");
        if (label) label.textContent = `${size}px`;
        if (window.IDE_STATE.editor && window.IDE_STATE.editor.updateOptions) {
            window.IDE_STATE.editor.updateOptions({ fontSize: size });
        } else {
            // fallback textarea
            const ta = document.getElementById("fallback-code-editor");
            if (ta) ta.style.fontSize = `${size}px`;
        }
    } else if (setting === 'fontFamily') {
        if (window.IDE_STATE.editor && window.IDE_STATE.editor.updateOptions) {
            window.IDE_STATE.editor.updateOptions({ fontFamily: value });
        } else {
            const ta = document.getElementById("fallback-code-editor");
            if (ta) ta.style.fontFamily = value;
        }
    } else if (setting === 'theme') {
        if (typeof monaco !== 'undefined') {
            monaco.editor.setTheme(value);
            window.IDE_STATE.theme = value;
        }
    }
}

// --- Console Settings ---
function applyConsoleSetting(setting, value) {
    const outputBody = document.querySelector(".output-body");
    if (!outputBody) return;

    if (setting === 'fontSize') {
        const size = parseInt(value);
        const label = document.getElementById("console-font-size-val");
        if (label) label.textContent = `${size}px`;
        outputBody.style.fontSize = `${size}px`;
    } else if (setting === 'fontFamily') {
        outputBody.style.fontFamily = value;
    } else if (setting === 'color') {
        outputBody.style.color = value;
    } else if (setting === 'background') {
        outputBody.style.background = value;
        const panel = document.getElementById("bottom-output-panel");
        if (panel) panel.style.background = value;
    }
}

// --- Reset IDE Settings to Defaults ---
function resetIDESettings() {
    // Reset editor settings controls
    const editorFontSizeEl = document.getElementById("setting-editor-font-size");
    const editorFontEl = document.getElementById("setting-editor-font");
    const editorThemeEl = document.getElementById("setting-editor-theme");
    if (editorFontSizeEl) { editorFontSizeEl.value = 14; applyEditorSetting('fontSize', 14); }
    if (editorFontEl) { editorFontEl.value = "Consolas, monospace"; applyEditorSetting('fontFamily', "Consolas, monospace"); }
    if (editorThemeEl) { editorThemeEl.value = "vs-dark"; applyEditorSetting('theme', "vs-dark"); }

    // Reset console settings controls
    const consoleFontSizeEl = document.getElementById("setting-console-font-size");
    const consoleFontEl = document.getElementById("setting-console-font");
    const consoleColorEl = document.getElementById("setting-console-text-color");
    const consoleBgEl = document.getElementById("setting-console-bg-color");
    if (consoleFontSizeEl) { consoleFontSizeEl.value = 14; applyConsoleSetting('fontSize', 14); }
    if (consoleFontEl) { consoleFontEl.value = "Consolas, monospace"; applyConsoleSetting('fontFamily', "Consolas, monospace"); }
    if (consoleColorEl) { consoleColorEl.value = "#f8fafc"; applyConsoleSetting('color', "#f8fafc"); }
    if (consoleBgEl) { consoleBgEl.value = "#090d16"; applyConsoleSetting('background', "#090d16"); }

    showToast("✅ IDE settings reset to defaults.", "success");
}

// =============================================================================
// INPUT VALUES MODAL — for programs that use input()
// =============================================================================

/**
 * Opens the Input Dialog.
 * @param {string[]} prompts - Array of prompt labels extracted from input("...") calls.
 *                             If empty/null, shows a single generic field.
 */
function openInputDialog(prompts) {
    const overlay   = document.getElementById("input-modal-overlay");
    const container = document.getElementById("input-fields-container");
    if (!overlay || !container) return;

    // Build labeled input fields
    container.innerHTML = "";
    const labels = (prompts && prompts.length > 0) ? prompts : ["Input 1"];
    labels.forEach((label, i) => {
        const div = document.createElement("div");
        div.className = "mb-2";
        div.innerHTML = `
            <label class="settings-label">${label || "Input " + (i + 1)}</label>
            <input type="text" class="form-control form-control-sm input-value-field"
                   placeholder="Enter value..." data-index="${i}"
                   onkeydown="if(event.key==='Enter'){ document.querySelectorAll('.input-value-field')[${i+1}]?.focus() || runWithInputs(); }">
        `;
        container.appendChild(div);
    });

    overlay.style.display = "flex";
    // Focus first field
    setTimeout(() => {
        const first = container.querySelector(".input-value-field");
        if (first) first.focus();
    }, 100);

    // Escape key closes modal
    document._inputEscHandler = (e) => { if (e.key === "Escape") closeInputModal(); };
    document.addEventListener("keydown", document._inputEscHandler);
}

/** Close the input modal without running */
function closeInputModal() {
    const overlay = document.getElementById("input-modal-overlay");
    if (overlay) overlay.style.display = "none";
    if (document._inputEscHandler) {
        document.removeEventListener("keydown", document._inputEscHandler);
        document._inputEscHandler = null;
    }
}

/** Close when clicking outside the modal box */
function closeInputModalOnOverlay(event) {
    if (event.target && event.target.id === "input-modal-overlay") {
        closeInputModal();
    }
}

/** Add an extra input field row */
function addInputField() {
    const container = document.getElementById("input-fields-container");
    if (!container) return;
    const count = container.querySelectorAll(".input-value-field").length + 1;
    const div = document.createElement("div");
    div.className = "mb-2";
    div.innerHTML = `
        <label class="settings-label">Input ${count}</label>
        <input type="text" class="form-control form-control-sm input-value-field"
               placeholder="Enter value...">
    `;
    container.appendChild(div);
    div.querySelector("input").focus();
}

/** Clear all input field values */
function clearInputFields() {
    document.querySelectorAll(".input-value-field").forEach(f => f.value = "");
    const first = document.querySelector(".input-value-field");
    if (first) first.focus();
}

/** Collect all input values and run the program */
async function runWithInputs() {
    const fields = document.querySelectorAll(".input-value-field");
    const inputs = Array.from(fields).map(f => f.value);

    // Validate at least one non-empty value
    if (inputs.every(v => v.trim() === "")) {
        showToast("⚠️ Please enter at least one input value.", "warning");
        return;
    }

    closeInputModal();
    // Pass collected stdin values to runProgram
    await runProgram(inputs);
}
