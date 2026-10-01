def ip_to_room_code(ip_str: str) -> str:
    try:
        octets = [int(x) for x in ip_str.split('.')]
        if len(octets) != 4:
            return "LUDO01"
        num = (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        code = ""
        while num > 0:
            num, rem = divmod(num, 36)
            code = alphabet[rem] + code
        return code.zfill(6)
    except Exception:
        return "LUDO01"

def room_code_to_ip(code_str: str) -> str:
    clean_code = code_str.strip().upper()
    if clean_code in ["LOCAL", "127.0.0.1", "LOCALHOST"]:
        return "127.0.0.1"
    try:
        num = int(clean_code, 36)
        octets = [
            str((num >> 24) & 255),
            str((num >> 16) & 255),
            str((num >> 8) & 255),
            str(num & 255)
        ]
        return ".".join(octets)
    except Exception:
        return "127.0.0.1"
