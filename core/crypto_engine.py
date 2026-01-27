import os
import struct
import hashlib
import hmac
import zlib
import base64
from typing import Optional

from Crypto.Cipher import ChaCha20_Poly1305, AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
from argon2.low_level import hash_secret_raw, Type


try:
    from pqcrypto.kem import kyber512, kyber768, kyber1024

    _PQC_KEMS = {
        "kyber512": kyber512,
        "kyber768": kyber768,
        "kyber1024": kyber1024,
    }
    _PQC_ORDER = ["kyber512", "kyber768", "kyber1024"]
    HAS_PQC = True
except Exception:
    _PQC_KEMS = {}
    _PQC_ORDER = []
    HAS_PQC = False


class CryptoEngine:
    FILE_MAGIC = b"NFX1"
    FILE_VERSION = 1

    DATA_MAGIC = b"NDSB"
    DATA_VERSION = 1

    KEY_MAGIC = b"NDSK"
    KEY_VERSION = 1

    MAGIC_STD = b"NDS1"
    MAGIC_PQC = b"NDSQ"
    MAGIC_SIV = b"NDS3"
    MAGIC_BLF = b"NDS4"
    MAGIC_CST = b"NDS5"

    ALG_CHACHA20 = 1
    ALG_AESGCM = 2
    ALG_PQC_HYBRID = 3

    KDF_ARGON2ID = 1

    FLAG_COMPRESS = 1
    FLAG_PQC = 2

    DEFAULT_MEM_KIB = 65536
    DEFAULT_TIME_COST = 3
    DEFAULT_PARALLELISM = 2

    ENCRYPTED_EXT = ".ndsfc"

    @staticmethod
    def pqc_available() -> bool:
        return HAS_PQC

    @staticmethod
    def pqc_kem_names() -> list[str]:
        return [name for name in _PQC_ORDER if name in _PQC_KEMS]

    @staticmethod
    def _get_kem(kem_name: str):
        kem = _PQC_KEMS.get(kem_name)
        if not kem:
            raise ValueError("Unsupported PQC KEM")
        return kem

    @staticmethod
    def _kem_keypair(kem_name: str) -> tuple[bytes, bytes]:
        kem = CryptoEngine._get_kem(kem_name)
        if hasattr(kem, "generate_keypair"):
            return kem.generate_keypair()
        if hasattr(kem, "keypair"):
            return kem.keypair()
        raise ValueError("PQC KEM missing keypair method")

    @staticmethod
    def _kem_encapsulate(kem_name: str, public_key: bytes) -> tuple[bytes, bytes]:
        kem = CryptoEngine._get_kem(kem_name)
        if hasattr(kem, "encrypt"):
            return kem.encrypt(public_key)
        if hasattr(kem, "encapsulate"):
            return kem.encapsulate(public_key)
        raise ValueError("PQC KEM missing encapsulate method")

    @staticmethod
    def _kem_decapsulate(kem_name: str, private_key: bytes, ciphertext: bytes) -> bytes:
        kem = CryptoEngine._get_kem(kem_name)
        if hasattr(kem, "decrypt"):
            return kem.decrypt(private_key, ciphertext)
        if hasattr(kem, "decapsulate"):
            return kem.decapsulate(private_key, ciphertext)
        raise ValueError("PQC KEM missing decapsulate method")

    @staticmethod
    def generate_pqc_keypair(kem_name: str) -> tuple[str, str]:
        if not HAS_PQC:
            raise RuntimeError("PQC library not available")
        pub, priv = CryptoEngine._kem_keypair(kem_name)
        return (
            base64.b64encode(pub).decode("ascii"),
            base64.b64encode(priv).decode("ascii"),
        )

    @staticmethod
    def decode_pqc_key(b64_value: str) -> bytes:
        return base64.b64decode(b64_value.encode("ascii"))

    @staticmethod
    def derive_key_argon2id(
        password: str,
        salt: bytes,
        length: int = 32,
        mem_kib: int = DEFAULT_MEM_KIB,
        time_cost: int = DEFAULT_TIME_COST,
        parallelism: int = DEFAULT_PARALLELISM,
    ) -> bytes:
        return hash_secret_raw(
            password.encode("utf-8"),
            salt,
            time_cost=time_cost,
            memory_cost=mem_kib,
            parallelism=parallelism,
            hash_len=length,
            type=Type.ID,
        )

    @staticmethod
    def derive_key_scrypt(password: str, salt: bytes, length: int = 32) -> bytes:
        return scrypt(password.encode("utf-8"), salt, length, N=2**15, r=8, p=1)

    @staticmethod
    def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
        return hmac.new(salt, ikm, hashlib.sha256).digest()

    @staticmethod
    def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
        out = b""
        counter = 1
        last = b""
        while len(out) < length:
            last = hmac.new(prk, last + info + bytes([counter]), hashlib.sha256).digest()
            out += last
            counter += 1
        return out[:length]

    @staticmethod
    def _hkdf(ikm: bytes, salt: bytes = b"", info: bytes = b"", length: int = 32) -> bytes:
        if not salt:
            salt = b"\x00" * 32
        prk = CryptoEngine._hkdf_extract(salt, ikm)
        return CryptoEngine._hkdf_expand(prk, info, length)

    @staticmethod
    def _build_header(
        alg_id: int,
        flags: int,
        salt: bytes,
        mem_kib: int,
        time_cost: int,
        parallelism: int,
        nonce_len: int,
        tag_len: int,
        kem_id: Optional[int] = None,
        kem_ct: Optional[bytes] = None,
    ) -> bytes:
        base = struct.pack(
            ">4sBBBB16sIIBBB",
            CryptoEngine.FILE_MAGIC,
            CryptoEngine.FILE_VERSION,
            alg_id,
            CryptoEngine.KDF_ARGON2ID,
            flags,
            salt,
            mem_kib,
            time_cost,
            parallelism,
            nonce_len,
            tag_len,
        )
        if kem_id is None or kem_ct is None:
            return base
        if len(kem_ct) > 65535:
            raise ValueError("KEM ciphertext too large")
        return base + struct.pack(">BH", kem_id, len(kem_ct)) + kem_ct

    @staticmethod
    def _parse_header(data: bytes) -> tuple[dict, int]:
        if len(data) < 35:
            raise ValueError("Invalid file header")
        (
            magic,
            version,
            alg_id,
            kdf_id,
            flags,
            salt,
            mem_kib,
            time_cost,
            parallelism,
            nonce_len,
            tag_len,
        ) = struct.unpack(">4sBBBB16sIIBBB", data[:35])
        if magic != CryptoEngine.FILE_MAGIC:
            raise ValueError("Unknown file magic")
        if version != CryptoEngine.FILE_VERSION:
            raise ValueError("Unsupported file version")
        offset = 35
        kem_id = None
        kem_ct = None
        if flags & CryptoEngine.FLAG_PQC:
            if len(data) < offset + 3:
                raise ValueError("Invalid PQC header")
            kem_id, kem_len = struct.unpack(">BH", data[offset : offset + 3])
            offset += 3
            kem_ct = data[offset : offset + kem_len]
            if len(kem_ct) != kem_len:
                raise ValueError("Invalid KEM ciphertext")
            offset += kem_len
        return (
            {
                "alg_id": alg_id,
                "kdf_id": kdf_id,
                "flags": flags,
                "salt": salt,
                "mem_kib": mem_kib,
                "time_cost": time_cost,
                "parallelism": parallelism,
                "nonce_len": nonce_len,
                "tag_len": tag_len,
                "kem_id": kem_id,
                "kem_ct": kem_ct,
            },
            offset,
        )

    @staticmethod
    def encrypt_file(
        input_path: str,
        password: str,
        algo: str,
        pqc_public_key: Optional[bytes] = None,
        pqc_kem: str = "kyber512",
        compress: bool = False,
    ) -> tuple[bool, str]:
        if not os.path.exists(input_path):
            return False, "Input file missing"

        with open(input_path, "rb") as f:
            plaintext = f.read()

        flags = 0
        if compress:
            plaintext = zlib.compress(plaintext)
            flags |= CryptoEngine.FLAG_COMPRESS

        salt = get_random_bytes(16)
        mem_kib = CryptoEngine.DEFAULT_MEM_KIB
        time_cost = CryptoEngine.DEFAULT_TIME_COST
        parallelism = CryptoEngine.DEFAULT_PARALLELISM

        base_key = CryptoEngine.derive_key_argon2id(
            password,
            salt,
            length=32,
            mem_kib=mem_kib,
            time_cost=time_cost,
            parallelism=parallelism,
        )

        alg_map = {
            "chacha20-poly1305": CryptoEngine.ALG_CHACHA20,
            "aes-256-gcm": CryptoEngine.ALG_AESGCM,
            "pqc-hybrid": CryptoEngine.ALG_PQC_HYBRID,
        }
        alg_id = alg_map.get(algo)
        if not alg_id:
            return False, "Unsupported algorithm"

        kem_id = None
        kem_ct = None
        final_key = base_key

        if alg_id == CryptoEngine.ALG_PQC_HYBRID:
            if not HAS_PQC:
                return False, "PQC library not available"
            if not pqc_public_key:
                return False, "PQC public key required"
            if pqc_kem not in CryptoEngine.pqc_kem_names():
                return False, "Unsupported PQC KEM"
            kem_id = CryptoEngine.pqc_kem_names().index(pqc_kem) + 1
            kem_ct, shared = CryptoEngine._kem_encapsulate(pqc_kem, pqc_public_key)
            final_key = CryptoEngine._hkdf(base_key + shared, salt, b"noxium-pqc", 32)
            flags |= CryptoEngine.FLAG_PQC

        nonce = get_random_bytes(12)
        tag_len = 16
        header = CryptoEngine._build_header(
            alg_id,
            flags,
            salt,
            mem_kib,
            time_cost,
            parallelism,
            len(nonce),
            tag_len,
            kem_id=kem_id,
            kem_ct=kem_ct,
        )

        if alg_id == CryptoEngine.ALG_AESGCM:
            cipher = AES.new(final_key, AES.MODE_GCM, nonce=nonce)
        else:
            cipher = ChaCha20_Poly1305.new(key=final_key, nonce=nonce)

        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        out_path = input_path + CryptoEngine.ENCRYPTED_EXT
        with open(out_path, "wb") as f:
            f.write(header)
            f.write(nonce)
            f.write(tag)
            f.write(ciphertext)

        return True, out_path

    @staticmethod
    def decrypt_file(
        input_path: str,
        password: str,
        pqc_private_key: Optional[bytes] = None,
    ) -> tuple[bool, str]:
        if not os.path.exists(input_path):
            return False, "Input file missing"

        with open(input_path, "rb") as f:
            raw = f.read()

        if len(raw) < 4:
            return False, "Invalid file"

        if raw[:4] != CryptoEngine.FILE_MAGIC:
            return CryptoEngine._decrypt_legacy(input_path, password)

        try:
            header, offset = CryptoEngine._parse_header(raw)
        except Exception as e:
            return False, f"Header error: {e}"

        nonce_end = offset + header["nonce_len"]
        tag_end = nonce_end + header["tag_len"]
        if tag_end > len(raw):
            return False, "Invalid payload"

        nonce = raw[offset:nonce_end]
        tag = raw[nonce_end:tag_end]
        ciphertext = raw[tag_end:]

        base_key = CryptoEngine.derive_key_argon2id(
            password,
            header["salt"],
            length=32,
            mem_kib=header["mem_kib"],
            time_cost=header["time_cost"],
            parallelism=header["parallelism"],
        )

        final_key = base_key
        if header["flags"] & CryptoEngine.FLAG_PQC:
            if not pqc_private_key:
                return False, "PQC private key required"
            kem_id = header["kem_id"]
            if kem_id is None:
                return False, "Missing PQC metadata"
            kem_names = CryptoEngine.pqc_kem_names()
            if kem_id - 1 >= len(kem_names):
                return False, "Unknown PQC KEM"
            kem_name = kem_names[kem_id - 1]
            shared = CryptoEngine._kem_decapsulate(
                kem_name, pqc_private_key, header["kem_ct"]
            )
            final_key = CryptoEngine._hkdf(
                base_key + shared, header["salt"], b"noxium-pqc", 32
            )

        if header["alg_id"] == CryptoEngine.ALG_AESGCM:
            cipher = AES.new(final_key, AES.MODE_GCM, nonce=nonce)
        else:
            cipher = ChaCha20_Poly1305.new(key=final_key, nonce=nonce)

        header_bytes = raw[:offset]
        cipher.update(header_bytes)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            return False, f"Decryption Error: {e}"

        if header["flags"] & CryptoEngine.FLAG_COMPRESS:
            try:
                plaintext = zlib.decompress(plaintext)
            except Exception as e:
                return False, f"Decompression Error: {e}"

        out_path = input_path.replace(CryptoEngine.ENCRYPTED_EXT, "")
        with open(out_path, "wb") as f:
            f.write(plaintext)

        return True, out_path

    @staticmethod
    def _decrypt_legacy(input_path: str, password: str) -> tuple[bool, str]:
        try:
            with open(input_path, "rb") as f:
                magic = f.read(4)
                salt = f.read(16)

                key = CryptoEngine.derive_key_scrypt(password, salt, 32)

                if magic == CryptoEngine.MAGIC_SIV:
                    n_len = struct.unpack("B", f.read(1))[0]
                    nonce = f.read(n_len)
                    t_len = struct.unpack("B", f.read(1))[0]
                    tag = f.read(t_len)
                    ciphertext = f.read()

                    key_siv = CryptoEngine.derive_key_scrypt(password, salt, 64)
                    cipher = AES.new(key_siv, AES.MODE_SIV, nonce=nonce)
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

                elif magic == CryptoEngine.MAGIC_BLF:
                    n_len = struct.unpack("B", f.read(1))[0]
                    nonce = f.read(n_len)
                    f.read(1)
                    ciphertext = f.read()
                    from Crypto.Cipher import Blowfish

                    cipher = Blowfish.new(key, Blowfish.MODE_CTR, nonce=nonce)
                    plaintext = cipher.decrypt(ciphertext)

                elif magic == CryptoEngine.MAGIC_CST:
                    n_len = struct.unpack("B", f.read(1))[0]
                    nonce = f.read(n_len)
                    f.read(1)
                    ciphertext = f.read()
                    from Crypto.Cipher import CAST

                    key_cast = key[:16]
                    cipher = CAST.new(key_cast, CAST.MODE_CTR, nonce=nonce)
                    plaintext = cipher.decrypt(ciphertext)

                elif magic == CryptoEngine.MAGIC_PQC:
                    n_len = struct.unpack("B", f.read(1))[0]
                    nonce = f.read(n_len)
                    t_len = struct.unpack("B", f.read(1))[0]
                    tag = f.read(t_len)
                    ciphertext = f.read()

                    try:
                        key2 = hashlib.sha3_512(key).digest()[:32]
                    except Exception:
                        key2 = hashlib.sha512(key).digest()[:32]

                    cipher2 = ChaCha20_Poly1305.new(key=key2, nonce=nonce)
                    inner = cipher2.decrypt_and_verify(ciphertext, tag)

                    aes_nonce = inner[-16:]
                    aes_tag = inner[-32:-16]
                    aes_cipher = inner[:-32]
                    cipher1 = AES.new(key, AES.MODE_GCM, nonce=aes_nonce)
                    plaintext = cipher1.decrypt_and_verify(aes_cipher, aes_tag)

                elif magic == CryptoEngine.MAGIC_STD:
                    n_len = struct.unpack("B", f.read(1))[0]
                    nonce = f.read(n_len)
                    t_len = struct.unpack("B", f.read(1))[0]
                    tag = f.read(t_len)
                    ciphertext = f.read()

                    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

                else:
                    return False, "Unknown legacy format"

            out_path = input_path.replace(CryptoEngine.ENCRYPTED_EXT, "")
            with open(out_path, "wb") as f:
                f.write(plaintext)
            return True, out_path

        except Exception as e:
            return False, f"Legacy Decryption Error: {e}"

    @staticmethod
    def data_encrypt(data: bytes, password: str) -> dict:
        salt = get_random_bytes(16)
        key = CryptoEngine.derive_key_scrypt(password, salt)
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        return {
            "salt": salt.hex(),
            "nonce": cipher.nonce.hex(),
            "tag": tag.hex(),
            "ciphertext": ciphertext.hex(),
        }

    @staticmethod
    def data_decrypt(enc_dict: dict, password: str) -> bytes:
        try:
            salt = bytes.fromhex(enc_dict["salt"])
            nonce = bytes.fromhex(enc_dict["nonce"])
            tag = bytes.fromhex(enc_dict["tag"])
            ciphertext = bytes.fromhex(enc_dict["ciphertext"])

            key = CryptoEngine.derive_key_scrypt(password, salt)
            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except (ValueError, KeyError):
            raise ValueError("Decryption Failed")

    @staticmethod
    def data_encrypt_blob(data: bytes, password: str) -> bytes:
        salt = get_random_bytes(16)
        key = CryptoEngine.derive_key_scrypt(password, salt)
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        nonce = cipher.nonce

        if len(nonce) > 255 or len(tag) > 255:
            raise ValueError("Nonce/Tag length overflow")

        return b"".join(
            [
                CryptoEngine.DATA_MAGIC,
                bytes([CryptoEngine.DATA_VERSION]),
                salt,
                bytes([len(nonce)]),
                nonce,
                bytes([len(tag)]),
                tag,
                ciphertext,
            ]
        )

    @staticmethod
    def data_decrypt_blob(blob: bytes, password: str) -> bytes:
        if len(blob) < 4 + 1 + 16 + 1 + 1:
            raise ValueError("Invalid blob length")

        magic = blob[:4]
        version = blob[4]
        if magic != CryptoEngine.DATA_MAGIC or version != CryptoEngine.DATA_VERSION:
            raise ValueError("Unknown blob format")

        offset = 5
        salt = blob[offset : offset + 16]
        offset += 16

        n_len = blob[offset]
        offset += 1
        nonce = blob[offset : offset + n_len]
        offset += n_len

        t_len = blob[offset]
        offset += 1
        tag = blob[offset : offset + t_len]
        offset += t_len

        ciphertext = blob[offset:]

        key = CryptoEngine.derive_key_scrypt(password, salt)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    @staticmethod
    def data_encrypt_key_blob(data: bytes, key: bytes) -> bytes:
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        nonce = cipher.nonce

        if len(nonce) > 255 or len(tag) > 255:
            raise ValueError("Nonce/Tag length overflow")

        return b"".join(
            [
                CryptoEngine.KEY_MAGIC,
                bytes([CryptoEngine.KEY_VERSION]),
                bytes([len(nonce)]),
                nonce,
                bytes([len(tag)]),
                tag,
                ciphertext,
            ]
        )

    @staticmethod
    def data_decrypt_key_blob(blob: bytes, key: bytes) -> bytes:
        if len(blob) < 4 + 1 + 1 + 1:
            raise ValueError("Invalid key blob length")

        magic = blob[:4]
        version = blob[4]
        if magic != CryptoEngine.KEY_MAGIC or version != CryptoEngine.KEY_VERSION:
            raise ValueError("Unknown key blob format")

        offset = 5
        n_len = blob[offset]
        offset += 1
        nonce = blob[offset : offset + n_len]
        offset += n_len

        t_len = blob[offset]
        offset += 1
        tag = blob[offset : offset + t_len]
        offset += t_len

        ciphertext = blob[offset:]

        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    @staticmethod
    def encrypt_advanced(input_path, password, mode, compress=False, pqc_public_key=None, pqc_kem="kyber512"):
        mode_map = {
            "standard": "chacha20-poly1305",
            "siv": "aes-256-gcm",
            "blowfish": "aes-256-gcm",
            "cast": "aes-256-gcm",
            "pqc": "pqc-hybrid",
        }
        algo = mode_map.get(mode, "chacha20-poly1305")
        return CryptoEngine.encrypt_file(
            input_path,
            password,
            algo,
            pqc_public_key=pqc_public_key,
            pqc_kem=pqc_kem,
            compress=compress,
        )

    @staticmethod
    def decrypt_advanced(input_path, password, pqc_private_key=None):
        return CryptoEngine.decrypt_file(
            input_path, password, pqc_private_key=pqc_private_key
        )
