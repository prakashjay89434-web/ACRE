import psutil
import subprocess
import os
import platform


def get_system_info() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "platform": platform.system(),
    }


def get_running_apps() -> list:
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
    return apps[:20]


def open_application(app_name: str) -> dict:
    app_lower = app_name.lower().strip()

    app_map = {
        "chrome": "start chrome",
        "notepad": "start notepad",
        "calculator": "start calc",
        "explorer": "start explorer",
        "file explorer": "start explorer",
        "vs code": "code .",
        "vscode": "code .",
        "terminal": "start cmd",
        "cmd": "start cmd",
        "whatsapp": "start whatsapp:",
        "spotify": "start spotify:",
        "word": "start winword",
        "excel": "start excel",
        "paint": "start mspaint",
        "settings": "start ms-settings:",
        "task manager": "start taskmgr",
        "youtube": "start https://youtube.com",
        "google": "start https://google.com",
        "gmail": "start https://gmail.com",
        "github": "start https://github.com",
    }

    for key, cmd in app_map.items():
        if key in app_lower:
            try:
                subprocess.Popen(cmd, shell=True)
                return {"success": True, "message": f"Opening {key}..."}
            except Exception as e:
                return {"success": False, "message": str(e)}

    try:
        subprocess.Popen(f"start {app_lower}", shell=True)
        return {"success": True, "message": f"Trying to open '{app_name}'..."}
    except Exception as e:
        return {"success": False, "message": f"Could not open '{app_name}': {str(e)}"}


def take_screenshot() -> str:
    path = "data/screenshot.png"
    os.makedirs("data", exist_ok=True)
    try:
        import mss
        with mss.mss() as sct:
            sct.shot(output=path)
        return path
    except Exception:
        return "Screenshot failed - mss not available"


def type_text(text: str) -> dict:
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=0.05)
        return {"success": True, "message": f"Typed: {text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}