"""
FinWise one-click launcher
==========================

Started by run.bat (Windows), run.command (macOS) or run.sh (Linux).
It uses only the Python standard library, so it works on a fresh Python
install. Steps:

    1. Check the Python version (3.9 or newer).
    2. Create a private virtual environment in the ".venv" folder
       (only the first time).
    3. Install the packages from requirements.txt (only the first time,
       or again when requirements.txt changes).
    4. Find a free port, start the Streamlit app and open the browser.

You can also run it directly:  python launcher.py
"""

import hashlib
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import venv
import webbrowser

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_DIR, ".venv")
REQUIREMENTS = os.path.join(PROJECT_DIR, "requirements.txt")
APP_FILE = os.path.join(PROJECT_DIR, "app.py")
STAMP_FILE = os.path.join(VENV_DIR, ".finwise-installed")
MIN_PYTHON = (3, 9)


def say(message):
    print(f"[FinWise] {message}", flush=True)


def fail(message):
    print("\n" + "=" * 64)
    print(" FinWise could not start")
    print("=" * 64)
    print(message)
    print("=" * 64 + "\n")
    sys.exit(1)


def venv_python():
    """Path of the Python interpreter inside the virtual environment."""
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def venv_works():
    """True if the virtual environment exists and its Python can run."""
    python = venv_python()
    if not os.path.exists(python):
        return False
    try:
        subprocess.run([python, "-c", "import sys"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def create_venv():
    if venv_works():
        return
    if os.path.exists(VENV_DIR):
        say("Existing .venv is broken (was the folder moved?). Recreating it...")
        shutil.rmtree(VENV_DIR, ignore_errors=True)
    say("First run: creating a private Python environment (.venv)...")
    try:
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    except Exception as error:  # noqa: BLE001 - show any failure clearly
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        hint = ""
        if sys.platform.startswith("linux"):
            hint = ("\nOn Ubuntu/Debian install the venv module first:\n"
                    "    sudo apt install python3-venv python3-pip\n"
                    "then run this launcher again.")
        fail(f"Could not create the virtual environment:\n    {error}{hint}")
    if not venv_works():
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        fail("The virtual environment was created but its Python does not run.\n"
             "Try reinstalling Python from https://www.python.org/downloads/")


def requirements_hash():
    with open(REQUIREMENTS, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def install_requirements():
    """Install packages only when needed (first run or requirements changed)."""
    wanted = requirements_hash()
    if os.path.exists(STAMP_FILE):
        with open(STAMP_FILE, encoding="utf-8") as file:
            if file.read().strip() == wanted:
                say("Packages already installed.")
                return

    say("Installing packages (one time only, needs internet, about 1-3 minutes)...")
    python = venv_python()
    subprocess.run([python, "-m", "pip", "install", "--upgrade", "pip", "--quiet",
                    "--disable-pip-version-check"], check=False)
    result = subprocess.run([python, "-m", "pip", "install", "-r", REQUIREMENTS,
                             "--disable-pip-version-check"])
    if result.returncode != 0:
        fail("Package installation failed.\n"
             "  * Check your internet connection and run the launcher again.\n"
             "  * Behind a college/office proxy? Set HTTPS_PROXY first.\n"
             "  * Still failing? Delete the .venv folder and try again.")
    with open(STAMP_FILE, "w", encoding="utf-8") as file:
        file.write(wanted)
    say("Packages installed.")


def free_port(start=8501, end=8599):
    """Return the first port that nothing else is using."""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    fail(f"No free port found between {start} and {end}. Close other apps and retry.")


def wait_until_ready(url, process, timeout=90):
    """Poll Streamlit's health endpoint until the server answers."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=2) as response:
                if response.status == 200:
                    return True
        except OSError:
            pass
        time.sleep(0.5)
    return False


def run_app():
    port = free_port()
    url = f"http://localhost:{port}"
    command = [
        venv_python(), "-m", "streamlit", "run", APP_FILE,
        "--server.port", str(port),
        "--server.headless", "true",            # skips Streamlit's first-run email prompt
        "--browser.gatherUsageStats", "false",
    ]
    say("Starting FinWise...")
    process = subprocess.Popen(command, cwd=PROJECT_DIR)

    try:
        if wait_until_ready(url, process):
            say(f"FinWise is running at {url}")
            webbrowser.open(url)
            print("\n   Keep this window open while you use the app.")
            print("   To stop FinWise: close this window or press Ctrl + C.\n", flush=True)
        elif process.poll() is not None:
            fail("The app stopped while starting. Scroll up to see the error.\n"
                 "Deleting the .venv folder and running again often fixes it.")
        else:
            say(f"The app is taking long to start. Open {url} in your browser manually.")
        process.wait()
    except KeyboardInterrupt:
        say("Stopping FinWise...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    print("\n  FinWise – Smart Financial Calculator\n  ------------------------------------")
    if sys.version_info < MIN_PYTHON:
        fail(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer is needed; "
             f"this is Python {sys.version.split()[0]}.\n"
             "Install the latest Python from https://www.python.org/downloads/")
    for needed in (APP_FILE, REQUIREMENTS):
        if not os.path.exists(needed):
            fail(f"Missing file: {os.path.basename(needed)}\n"
                 "Download the complete project folder and try again.")
    create_venv()
    install_requirements()
    run_app()


if __name__ == "__main__":
    main()
