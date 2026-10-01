import base64
import json

def encode_online_room(host_str: str, port_int: int) -> str:
    """Encodes host and port into a clean, shareable 6-8 char room code."""
    data = f"{host_str}:{port_int}".encode("utf-8")
    b64 = base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")
    return b64

def decode_online_room(code_str: str) -> tuple[str, int]:
    """Decodes a room code back into (host, port)."""
    clean = code_str.strip()
    if clean.upper() in ["LOCAL", "127.0.0.1", "LOCALHOST"]:
        return "127.0.0.1", 5555
    try:
        # Check if direct host:port entered
        if ":" in clean:
            h, p = clean.split(":", 1)
            return h.strip(), int(p.strip())
        # Base64 decode
        padding = 4 - (len(clean) % 4)
        if padding != 4:
            clean += "=" * padding
        decoded = base64.urlsafe_b64decode(clean.encode("utf-8")).decode("utf-8")
        h, p = decoded.split(":", 1)
        return h, int(p)
    except Exception:
        return clean, 5555