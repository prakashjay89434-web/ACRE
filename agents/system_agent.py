from agents.base_agent import BaseAgent
from utils.system_control import open_application, get_system_info
from utils.browser_automation import (
    search_youtube, send_whatsapp_message,
    send_gmail, open_url, google_search
)
from typing import Any
import re


class SystemAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="SystemAgent")

    def get_name(self) -> str:
        return self.name

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        query = state.get("query", "").lower().strip()
        print(f"  [System] Processing: '{query}'")

        answer = ""

        # YouTube search
        if "youtube" in query and ("search" in query or "play" in query or "find" in query):
            search_term = re.sub(r'.*(search|play|find).*?(on|in)?\s*youtube\s*', '', query).strip()
            if not search_term:
                search_term = query.replace("youtube", "").replace("search", "").replace("open", "").strip()
            result = search_youtube(search_term)
            answer = result["message"]

        # WhatsApp message
        elif "whatsapp" in query and ("send" in query or "message" in query):
            # Extract contact and message
            parts = query.split("to")
            contact = parts[1].split("and")[0].strip() if len(parts) > 1 else ""
            msg_parts = query.split("saying") or query.split("message")
            message = msg_parts[-1].strip() if len(msg_parts) > 1 else "Hello!"
            result = send_whatsapp_message(contact, message)
            answer = result["message"]

        # Gmail
        elif ("gmail" in query or "email" in query or "mail" in query) and "send" in query:
            parts = query.split("to")
            to = parts[1].split()[0].strip() if len(parts) > 1 else ""
            result = send_gmail(to, "Message from ACRE", query)
            answer = result["message"]

        # Google search
        elif "google" in query and "search" in query:
            search_term = query.replace("google", "").replace("search", "").replace("on", "").strip()
            result = google_search(search_term)
            answer = result["message"]

        # Open URL
        elif "open" in query and ("." in query or "http" in query):
            url = re.search(r'(https?://\S+|\S+\.\S+)', query)
            if url:
                result = open_url(url.group())
                answer = result["message"]
            else:
                result = open_application(query.replace("open", "").strip())
                answer = result["message"]

        # Open app
        elif "open" in query or "launch" in query or "start" in query:
            app_name = query.replace("open", "").replace("launch", "").replace("start", "").strip()
            result = open_application(app_name)
            answer = result["message"]

        # System info
        elif "system" in query or "cpu" in query or "ram" in query:
            info = get_system_info()
            answer = f"CPU: {info['cpu_percent']}% | RAM: {info['ram_percent']}% ({info['ram_used_gb']}/{info['ram_total_gb']} GB) | Disk: {info['disk_percent']}%"

        else:
            answer = f"Command not understood: '{query}'"

        print(f"  [System] Result: {answer}")

        return {
            **state,
            "code_result": {
                "code": "",
                "stdout": answer,
                "stderr": "",
                "error": False,
                "confidence": 1.0,
            }
        }