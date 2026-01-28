import hashlib
import os
import platform
import uuid


def _read_windows_machine_guid():
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        return value
    except Exception:
        return None


def _read_machine_id():
    if os.name == "nt":
        return _read_windows_machine_guid()
    for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception:
            continue
    return None


def get_device_fingerprint() -> bytes:
    parts = []
    machine_id = _read_machine_id()
    if machine_id:
        parts.append(machine_id)

    try:
        parts.append(platform.node())
    except Exception:
        pass

    try:
        parts.append(platform.system())
        parts.append(platform.release())
    except Exception:
        pass

    try:
        parts.append(str(uuid.getnode()))
    except Exception:
        pass

    if not parts:
        raise RuntimeError("No device identifiers available")

    data = "|".join(parts).encode("utf-8")
    return hashlib.sha256(data).digest()


def get_device_fingerprint_hex() -> str:
    return get_device_fingerprint().hex()
