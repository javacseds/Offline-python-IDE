/**
 * GITAMW Python Smart IDE - Splash Screen Controller
 * Handles 3-second animated loading screen transition to Login Screen.
 */
document.addEventListener("DOMContentLoaded", () => {
    const splashScreen = document.getElementById("splash-screen");
    const loginScreen = document.getElementById("login-screen");
    const mainIdeApp = document.getElementById("main-ide-app");

    // Check if student profile session exists in localStorage
    const storedStudent = localStorage.getItem("gitamw_student_profile");
    if (storedStudent && storedStudent !== "null") {
        try {
            const parsed = JSON.parse(storedStudent);
            if (parsed && parsed.name) {
                if (splashScreen) splashScreen.style.display = "none";
                if (loginScreen) loginScreen.style.display = "none";
                if (mainIdeApp) mainIdeApp.style.display = "flex";
                if (window.initializeIDEApp) window.initializeIDEApp(parsed);
                return;
            }
        } catch (e) {
            localStorage.removeItem("gitamw_student_profile");
        }
    }

    // Hide main IDE app initially if no active session
    if (mainIdeApp) mainIdeApp.style.display = "none";
    if (loginScreen) loginScreen.style.display = "none";

    // Timer for Splash Screen
    setTimeout(() => {
        if (splashScreen) {
            splashScreen.style.opacity = "0";
            setTimeout(() => {
                splashScreen.style.display = "none";
                if (mainIdeApp && mainIdeApp.style.display === "flex") {
                    return; // IDE already active
                }
                if (loginScreen) loginScreen.style.display = "flex";
            }, 500);
        }
    }, 1500);
});
