import ctypes
import os
import threading
from typing import Optional


class SecureSession:
    """RAM-only session storage with best-effort memory locking and wiping."""

    _instance = None
    _instance_lock = threading.Lock()
    __slots__ = (
        "_lock",
        "_key_buf",
        "_key_len",
        "_locked",
        "current_vault",
        "is_active",
    )

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    inst = super(SecureSession, cls).__new__(cls)
                    inst._lock = threading.RLock()
                    inst._key_buf = None
                    inst._key_len = 0
                    inst._locked = False
                    inst.current_vault = None
                    inst.is_active = False
                    cls._instance = inst
        return cls._instance

    @property
    def master_key(self) -> Optional[memoryview]:
        if not self._key_buf or self._key_len == 0:
            return None
        return memoryview(self._key_buf)[: self._key_len]

    def start_session(self, key: bytes, vault_name: str):
        with self._lock:
            self._set_key(key)
            self.current_vault = vault_name
            self.is_active = True

    def destroy_session(self):
        """Wipes keys from RAM securely and releases references."""
        with self._lock:
            self._wipe_key()
            self.current_vault = None
            self.is_active = False

        import gc

        gc.collect()

    def _set_key(self, key) -> None:
        if key is None:
            self._wipe_key()
            return
        if not isinstance(key, (bytes, bytearray, memoryview)):
            raise ValueError("Session key must be bytes-like")

        view = memoryview(key)
        key_len = len(view)
        if key_len == 0:
            self._wipe_key()
            return

        if self._key_buf is None or len(self._key_buf) != key_len:
            self._wipe_key()
            self._key_buf = bytearray(key_len)
        else:
            self._zero_buffer()

        self._key_buf[:key_len] = view[:key_len]
        self._key_len = key_len
        self._lock_key()

    def _lock_key(self) -> None:
        if not self._key_buf or os.name != "nt":
            self._locked = False
            return
        try:
            buf = (ctypes.c_char * len(self._key_buf)).from_buffer(self._key_buf)
            res = ctypes.windll.kernel32.VirtualLock(
                ctypes.c_void_p(ctypes.addressof(buf)), ctypes.c_size_t(len(self._key_buf))
            )
            self._locked = bool(res)
        except Exception:
            self._locked = False

    def _unlock_key(self) -> None:
        if not self._key_buf or not self._locked or os.name != "nt":
            self._locked = False
            return
        try:
            buf = (ctypes.c_char * len(self._key_buf)).from_buffer(self._key_buf)
            ctypes.windll.kernel32.VirtualUnlock(
                ctypes.c_void_p(ctypes.addressof(buf)), ctypes.c_size_t(len(self._key_buf))
            )
        except Exception:
            pass
        self._locked = False

    def _zero_buffer(self) -> None:
        if not self._key_buf:
            self._key_len = 0
            return
        try:
            buf = (ctypes.c_char * len(self._key_buf)).from_buffer(self._key_buf)
            ctypes.memset(ctypes.c_void_p(ctypes.addressof(buf)), 0, len(self._key_buf))
        except Exception:
            for i in range(len(self._key_buf)):
                self._key_buf[i] = 0

    def _wipe_key(self, lock_after: bool = False) -> None:
        if not self._key_buf:
            self._key_len = 0
            return
        self._unlock_key()
        self._zero_buffer()
        if not lock_after:
            self._key_buf = None
            self._key_len = 0
        else:
            self._key_len = 0
            self._lock_key()

    def __del__(self):
        try:
            self._wipe_key()
        except Exception:
            pass
