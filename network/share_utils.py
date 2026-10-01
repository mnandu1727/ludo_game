# network/share_utils.py
import subprocess
import platform
import webbrowser
import urllib.parse

def copy_to_clipboard(text: str) -> bool:
    """Copies text to the system clipboard across macOS, Windows, and Linux."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        elif system == "Windows":  # Windows
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            process.communicate(text.encode('utf-8'))
            return True
        elif system == "Linux":  # Linux (xclip/xsel)
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
    except Exception:
        pass
    return False

def get_from_clipboard() -> str:
    """Retrieves text from the OS clipboard."""
    system = platform.system()
    try:
        if system == "Darwin":
            return subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8').strip()
        elif system == "Windows":
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            txt = root.clipboard_get()
            root.destroy()
            return str(txt).strip()
    except Exception:
        pass
    return ""

def share_to_whatsapp(room_code: str, host_name: str = "Host"):
    """Launches WhatsApp with a pre-filled match invite text."""
    msg = (
        f"🎲 Join my Ludo match!\n"
        f"👑 Host: {host_name}\n"
        f"🔑 Room Code: {room_code}\n\n"
        f"Enter the code in the Ludo Game to join!"
    )
    encoded = urllib.parse.quote(msg)
    url = f"https://api.whatsapp.com/send?text={encoded}"
    try:
        webbrowser.open(url)
    except Exception:
        pass