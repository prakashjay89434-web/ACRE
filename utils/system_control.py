import psutil
import subprocess
import os
import pyautogui
import platform


def get_system_info() -> dict:
    """Get current system information."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "platform": platform.system(),
    }


def get_running_apps() -> list:
    """Get list of running applications."""
    apps = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            if proc.info['status'] == 'running':
                apps.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name']
                })
        except Exception:
            pass
    return apps[:20]  # Return top 20


def open_application(app_name: str) -> dict:
    """Open an application. Requires user confirmation first."""
    app_map = {
        "chrome": "start chrome",
        "notepad": "start notepad",
        "calculator": "start calc",
        "explorer": "start explorer",
        "vs code": "code .",
        "vscode": "code .",
        "terminal": "start cmd",
        "cmd": "start cmd",
    }

    app_lower = app_name.lower()
    command = None

    for key, cmd in app_map.items():
        if key in app_lower:
            command = cmd
            break

    if not command:
        return {"success": False, "message": f"App '{app_name}' not found in list"}

    try:
        subprocess.Popen(command, shell=True)
        return {"success": True, "message": f"Opening {app_name}..."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def take_screenshot() -> str:
    """Take a screenshot and save it."""
    path = "data/screenshot.png"
    os.makedirs("data", exist_ok=True)
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path


def type_text(text: str) -> dict:
    """Type text using keyboard."""
    try:
        pyautogui.typewrite(text, interval=0.05)
        return {"success": True, "message": f"Typed: {text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    print("System Info:")
    info = get_system_info()
    for k, v in info.items():
        print(f"  {k}: {v}")

    print("\nRunning Apps (top 5):")
    apps = get_running_apps()
    for app in apps[:5]:
        print(f"  {app['name']} (PID: {app['pid']})")