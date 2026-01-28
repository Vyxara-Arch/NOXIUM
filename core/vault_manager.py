import os
import json

from core.vault_storage import VaultStorage, VAULT_EXT

VAULT_DIR = "vaults"


class VaultManager:
    def __init__(self):
        if not os.path.exists(VAULT_DIR):
            os.makedirs(VAULT_DIR)

    def list_vaults(self):
        """Return available vault names."""
        return VaultStorage.list_vault_names(VAULT_DIR)

    def create_vault(self, name, username, password, duress_password):
        """Create a new vault with encrypted metadata."""
        path = os.path.join(VAULT_DIR, f"{name}{VAULT_EXT}")
        if os.path.exists(path):
            return False, "Vault already exists!"

        from argon2 import PasswordHasher
        import pyotp
        from core.crypto_engine import CryptoEngine
        from Crypto.Random import get_random_bytes

        ph = PasswordHasher()
        totp_secret = pyotp.random_base32()

        default_kem = "kyber512"
        pqc_keys = {}
        if CryptoEngine.pqc_available():
            try:
                pub, priv = CryptoEngine.generate_pqc_keypair(default_kem)
                pqc_keys = {"kem": default_kem, "public": pub, "private": priv}
            except Exception:
                pqc_keys = {}

        vault_content = {
            "totp_secret": totp_secret,
            "settings": {
                "file_algo": "chacha20-poly1305",
                "file_compress": False,
                "shred": 3,
                "theme_mode": "light",
                "theme_name": "Noxium Teal",
                "pqc_enabled": False,
                "pqc_kem": default_kem,
                "auto_lock_minutes": 10,
                "device_lock_enabled": False,
            },
            "pqc": pqc_keys,
        }

        vault_key = get_random_bytes(32)
        wrapped_key = CryptoEngine.data_encrypt_blob(vault_key, password)
        encrypted_blob = CryptoEngine.data_encrypt_key_blob(
            json.dumps(vault_content).encode("utf-8"), vault_key
        )

        VaultStorage.write_vault(
            path,
            username,
            ph.hash(password),
            ph.hash(duress_password),
            encrypted_blob,
            wrapped_key=wrapped_key,
        )

        return True, totp_secret

    def get_vault_path(self, name):
        return VaultStorage.resolve_vault_path(VAULT_DIR, name)
