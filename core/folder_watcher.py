import os
import time
import threading
from PyQt6.QtCore import QObject, pyqtSignal

from core.crypto_engine import CryptoEngine


class FolderWatcher(QObject):
    """Background service to monitor folders and auto-encrypt new files."""

    file_processed = pyqtSignal(str, str)

    def __init__(
        self,
        crypto_engine,
        password,
        mode="chacha20-poly1305",
        compress=False,
        pqc_public_key=None,
        pqc_kem="kyber512",
        device_lock=False,
    ):
        super().__init__()
        self.crypto_engine = crypto_engine
        self.password = password
        self.mode = mode
        self.compress = compress
        self.pqc_public_key = pqc_public_key
        self.pqc_kem = pqc_kem
        self.device_lock = device_lock
        self.folders = set()
        self.running = False
        self.thread = None
        self._lock = threading.Lock()
        self._seen = {}

    def add_folder(self, path):
        with self._lock:
            if os.path.exists(path) and os.path.isdir(path):
                self.folders.add(path)
                return True
        return False

    def remove_folder(self, path):
        with self._lock:
            if path in self.folders:
                self.folders.remove(path)

    def get_folders(self):
        return list(self.folders)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self):
        while self.running:
            with self._lock:
                current_folders = list(self.folders)

            for folder in current_folders:
                if not os.path.exists(folder):
                    continue

                try:
                    with os.scandir(folder) as entries:
                        for entry in entries:
                            if not self.running:
                                break
                            if not entry.is_file():
                                continue

                            if entry.name.endswith(CryptoEngine.ENCRYPTED_EXT):
                                continue

                            if os.path.exists(entry.path + CryptoEngine.ENCRYPTED_EXT):
                                continue

                            if entry.is_symlink():
                                continue

                            stat = entry.stat()
                            if hasattr(stat, "st_nlink") and stat.st_nlink > 1:
                                continue

                            now = time.time()
                            if now - stat.st_mtime < 2:
                                self._seen[entry.path] = {
                                    "mtime": stat.st_mtime,
                                    "size": stat.st_size,
                                    "stable": 0,
                                }
                                continue

                            last_seen = self._seen.get(entry.path)
                            if last_seen and last_seen["mtime"] == stat.st_mtime and last_seen["size"] == stat.st_size:
                                last_seen["stable"] += 1
                            else:
                                self._seen[entry.path] = {
                                    "mtime": stat.st_mtime,
                                    "size": stat.st_size,
                                    "stable": 0,
                                }
                                continue

                            if last_seen["stable"] < 1:
                                continue

                            self.process_file(entry.path)
                            self._seen.pop(entry.path, None)
                except Exception as e:
                    print(f"Watcher error: {e}")

            time.sleep(2)

    def process_file(self, path):
        try:
            ok, msg = self.crypto_engine.encrypt_file(
                path,
                self.password,
                self.mode,
                pqc_public_key=self.pqc_public_key,
                pqc_kem=self.pqc_kem,
                compress=self.compress,
                device_lock=self.device_lock,
            )
            if ok:
                from core.shredder import Shredder

                Shredder.wipe_file(path)
                self.file_processed.emit(os.path.basename(path), "Encrypted & Shredded")
            else:
                self.file_processed.emit(os.path.basename(path), f"Failed: {msg}")
        except Exception as e:
            self.file_processed.emit(os.path.basename(path), f"Error: {str(e)}")
