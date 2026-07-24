import sys
import subprocess
import importlib.util
from typing import Dict, List, Any

class PackageManager:
    """
    Detects pre-installed data science and standard Python packages locally
    and handles offline/local package installation commands.
    """

    TARGET_PACKAGES = [
        {"name": "numpy", "display": "NumPy", "category": "Data Science", "desc": "Numerical Python array library"},
        {"name": "pandas", "display": "Pandas", "category": "Data Analysis", "desc": "Data Structures & Analysis"},
        {"name": "matplotlib", "display": "Matplotlib", "category": "Visualization", "desc": "2D Plotting and Graphics"},
        {"name": "seaborn", "display": "Seaborn", "category": "Visualization", "desc": "Statistical Data Visualization"},
        {"name": "sklearn", "display": "Scikit-Learn", "category": "Machine Learning", "desc": "Machine Learning Algorithms"},
        {"name": "scipy", "display": "SciPy", "category": "Scientific", "desc": "Scientific Computing Tools"},
        {"name": "cv2", "display": "OpenCV (cv2)", "category": "Computer Vision", "desc": "Image Processing & Vision"},
        {"name": "requests", "display": "Requests", "category": "Networking", "desc": "HTTP Client Library"},
        {"name": "bs4", "display": "BeautifulSoup4", "category": "Web Scraping", "desc": "HTML/XML Parser"},
        {"name": "sympy", "display": "SymPy", "category": "Mathematics", "desc": "Symbolic Mathematics"},
        {"name": "torch", "display": "PyTorch", "category": "Deep Learning", "desc": "Tensor Computation & Neural Networks"},
        {"name": "tensorflow", "display": "TensorFlow", "category": "Deep Learning", "desc": "End-to-end Machine Learning"},
        {"name": "openpyxl", "display": "OpenPyXL", "category": "Data I/O", "desc": "Excel File Reading/Writing"},
        {"name": "pillow", "display": "Pillow (PIL)", "category": "Image Processing", "desc": "Python Imaging Library"}
    ]

    @staticmethod
    def get_installed_packages() -> List[Dict[str, Any]]:
        """Scans local Python environment for preinstalled packages."""
        results = []
        for pkg in PackageManager.TARGET_PACKAGES:
            mod_name = pkg["name"]
            spec = importlib.util.find_spec(mod_name)
            is_installed = spec is not None
            version = "Not Installed"
            if is_installed:
                try:
                    mod = __import__(mod_name)
                    version = getattr(mod, "__version__", "Installed")
                except Exception:
                    version = "Installed"
            
            results.append({
                "name": pkg["display"],
                "module_name": pkg["name"],
                "category": pkg["category"],
                "description": pkg["desc"],
                "is_installed": is_installed,
                "version": version
            })
        return results

    @staticmethod
    def install_package(package_name: str) -> Dict[str, Any]:
        """Installs package locally using current Python environment's pip."""
        clean_name = package_name.strip()
        if not clean_name:
            return {"success": False, "message": "Package name cannot be empty."}

        cmd = [sys.executable, "-m", "pip", "install", clean_name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode == 0:
                return {
                    "success": True,
                    "message": f"Package '{clean_name}' installed successfully!",
                    "output": res.stdout
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install '{clean_name}'.",
                    "output": res.stderr or res.stdout
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Installation timed out after 120 seconds."}
        except Exception as e:
            return {"success": False, "message": f"Error during package installation: {str(e)}"}
