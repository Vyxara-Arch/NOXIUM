import os
import json
import struct
from typing import Optional

VAULT_EXT = ".vault"


class VaultStorage:
    MAGIC = b"NVLT"
    VERSION_V1 = 1
    VERSION_V2 = 2

    @staticmethod
    def resolve_vault_path(vaults_dir: str, name: str) -> str:
        preferred = os.path.join(vaults_dir, f"{name}{VAULT_EXT}")
        if os.path.exists(preferred):
            return preferred
        legacy = os.path.join(vaults_dir, f"{name}.json")
        if os.path.exists(legacy):
            return legacy
        return preferred

    @staticmethod
    def list_vault_names(vaults_dir: str) -> list[str]:
        if not os.path.exists(vaults_dir):
            return []
        names = set()
        for entry in os.listdir(vaults_dir):
            if entry.endswith(VAULT_EXT):
                names.add(entry[: -len(VAULT_EXT)])
            elif entry.endswith(".json"):
                names.add(entry[:-5])
        return sorted(names)

    @staticmethod
    def write_vault(
        path: str,
        username: str,
        password_hash: str,
        duress_hash: str,
        vault_blob: bytes,
        wrapped_key: Optional[bytes] = None,
    ) -> None:
        user_bytes = username.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        duress_bytes = duress_hash.encode("utf-8")
        blob_len = len(vault_blob)
        wrapped_len = len(wrapped_key) if wrapped_key else 0

        if (
            len(user_bytes) > 65535
            or len(hash_bytes) > 65535
            or len(duress_bytes) > 65535
        ):
            raise ValueError("Vault header fields too large")

        if wrapped_key:
            header = struct.pack(
                ">4sBHHHII",
                VaultStorage.MAGIC,
                VaultStorage.VERSION_V2,
                len(user_bytes),
                len(hash_bytes),
                len(duress_bytes),
                wrapped_len,
                blob_len,
            )
        else:
            header = struct.pack(
                ">4sBHHHI",
                VaultStorage.MAGIC,
                VaultStorage.VERSION_V1,
                len(user_bytes),
                len(hash_bytes),
                len(duress_bytes),
                blob_len,
            )

        with open(path, "wb") as f:
            f.write(header)
            f.write(user_bytes)
            f.write(hash_bytes)
            f.write(duress_bytes)
            if wrapped_key:
                f.write(wrapped_key)
            f.write(vault_blob)

    @staticmethod
    def read_vault(path: str) -> dict:
        if path.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["format"] = "legacy_json"
            return data

        with open(path, "rb") as f:
            raw = f.read()

        if len(raw) < 4 + 1 + 2 + 2 + 2 + 4:
            raise ValueError("Vault file too small")

        magic, version = struct.unpack(">4sB", raw[:5])
        if magic != VaultStorage.MAGIC:
            raise ValueError("Invalid vault format")
        if version == VaultStorage.VERSION_V1:
            magic, version, u_len, h_len, d_len, blob_len = struct.unpack(
                ">4sBHHHI", raw[:15]
            )
            offset = 15
            wrapped_len = 0
        elif version == VaultStorage.VERSION_V2:
            magic, version, u_len, h_len, d_len, wrapped_len, blob_len = struct.unpack(
                ">4sBHHHII", raw[:19]
            )
            offset = 19
        else:
            raise ValueError("Unsupported vault version")

        end_user = offset + u_len
        end_hash = end_user + h_len
        end_duress = end_hash + d_len
        end_wrapped = end_duress + wrapped_len
        end_blob = end_wrapped + blob_len

        if end_blob != len(raw):
            raise ValueError("Vault length mismatch")

        return {
            "username": raw[offset:end_user].decode("utf-8"),
            "hash": raw[end_user:end_hash].decode("utf-8"),
            "duress_hash": raw[end_hash:end_duress].decode("utf-8"),
            "wrapped_key": raw[end_duress:end_wrapped] if wrapped_len else None,
            "vault_blob": raw[end_wrapped:end_blob],
            "format": "vault_bin",
            "version": version,
        }

    @staticmethod
    def migrate_legacy(
        legacy_path: str,
        username: str,
        password_hash: str,
        duress_hash: str,
        vault_blob: bytes,
        wrapped_key: Optional[bytes],
    ) -> str:
        new_path = legacy_path.replace(".json", VAULT_EXT)
        VaultStorage.write_vault(
            new_path,
            username,
            password_hash,
            duress_hash,
            vault_blob,
            wrapped_key=wrapped_key,
        )
        return new_path
