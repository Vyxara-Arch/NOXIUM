import os
import shutil
import zipfile
import datetime
import tempfile
import stat

from core.crypto_engine import CryptoEngine
from core.vault_storage import VAULT_EXT


class BackupManager:
    """Manages secure vault export and import (backup/restore)."""

    def __init__(self, vaults_dir="vaults"):
        self.vaults_dir = vaults_dir
        os.makedirs(self.vaults_dir, exist_ok=True)

    def export_vault(self, vault_name, output_dir, password):
        vault_path = os.path.join(self.vaults_dir, f"{vault_name}{VAULT_EXT}")
        legacy_path = os.path.join(self.vaults_dir, f"{vault_name}.json")
        vault_data_dir = os.path.join(self.vaults_dir, vault_name)

        if not os.path.exists(vault_path):
            if os.path.exists(legacy_path):
                vault_path = legacy_path
            else:
                return False, "Vault not found"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_zip = None

        try:
            fd, temp_zip = tempfile.mkstemp(prefix="noxium_backup_", suffix=".zip")
            os.close(fd)
            with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                ext = os.path.splitext(vault_path)[1]
                zf.write(vault_path, arcname=f"{vault_name}{ext}")

                if os.path.exists(vault_data_dir):
                    for root, dirs, files in os.walk(vault_data_dir):
                        for file in files:
                            abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(abs_path, self.vaults_dir)
                            zf.write(abs_path, arcname=rel_path)

            ok, enc_path = CryptoEngine.encrypt_file(
                temp_zip, password, "chacha20-poly1305"
            )
            if ok:
                final_name = f"{vault_name}_backup_{timestamp}.vib"
                final_path = os.path.join(output_dir, final_name)

                if os.path.exists(final_path):
                    os.remove(final_path)

                shutil.move(enc_path, final_path)
                return True, final_path
            return False, enc_path

        except Exception as e:
            return False, str(e)
        finally:
            if temp_zip and os.path.exists(temp_zip):
                os.remove(temp_zip)
            if temp_zip and os.path.exists(temp_zip + CryptoEngine.ENCRYPTED_EXT):
                os.remove(temp_zip + CryptoEngine.ENCRYPTED_EXT)

    def import_vault(self, backup_path, password):
        if not os.path.exists(backup_path):
            return False, "Backup file not found"

        temp_enc = None
        temp_zip = None

        fd, temp_enc = tempfile.mkstemp(prefix="noxium_restore_", suffix=CryptoEngine.ENCRYPTED_EXT)
        os.close(fd)
        temp_zip = temp_enc[: -len(CryptoEngine.ENCRYPTED_EXT)]
        shutil.copy(backup_path, temp_enc)

        try:
            ok, dec_path = CryptoEngine.decrypt_file(temp_enc, password)
            if not ok:
                return False, dec_path

            if not zipfile.is_zipfile(dec_path):
                return False, "Decrypted file is not a valid archive. Wrong password?"

            with zipfile.ZipFile(dec_path, "r") as zf:
                self._safe_extract(zf, self.vaults_dir)

            return True, "Vault restored successfully"

        except Exception as e:
            return False, f"Restore failed: {str(e)}"
        finally:
            if temp_enc and os.path.exists(temp_enc):
                os.remove(temp_enc)
            if temp_zip and os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except Exception:
                    pass

    def _safe_extract(self, zf: zipfile.ZipFile, dest_dir: str) -> None:
        base_dir = os.path.abspath(dest_dir)
        for member in zf.infolist():
            name = member.filename
            if not name or name.endswith("/"):
                continue

            # Block absolute paths and traversal
            target_path = os.path.abspath(os.path.join(base_dir, name))
            if os.path.commonpath([base_dir, target_path]) != base_dir:
                raise ValueError(f"Unsafe archive path: {name}")

            # Best-effort symlink detection (Unix zips)
            mode = (member.external_attr >> 16) & 0xFFFF
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise ValueError(f"Symlink entries not allowed: {name}")

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member, "r") as src, open(target_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
