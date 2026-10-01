import subprocess
import platform
import webbrowser
import urllib.parse

def copy_to_clipboard(text: str) -> bool:
    system = platform.system()
    try:
        if system == "Darwin":
            p = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
            p.communicate(text.encode('utf-8'))
            return True
        elif system == "Windows":
            p = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode('utf-8'))
            return True
    except Exception:
        pass
    return False

def get_from_clipboard() -> str:
    system = platform.system()
    try:
        if system == "Darwin":
            return subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8').strip()
    except Exception:
        pass
    return ""

def share_to_whatsapp(room_code: str, host_name: str = "Host"):
    msg = f"🎲 Join my Ludo match!\n👑 Host: {host_name}\n🔑 Room Code: {room_code}"
    encoded = urllib.parse.quote(msg)
    try:
        webbrowser.open(f"https://api.whatsapp.com/send?text={encoded}")
    except Exception:
        pass
