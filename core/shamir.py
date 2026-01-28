import struct
from binascii import hexlify, unhexlify

from Crypto.Protocol.SecretSharing import Shamir


class ShamirVault:
    MAGIC = b"NX"
    VERSION = 1
    CHUNK_SIZE = 16
    HEADER_FMT = ">2sBH"
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    @staticmethod
    def _split_chunks(secret_bytes: bytes) -> tuple[int, list[bytes]]:
        length = len(secret_bytes)
        if length == 0:
            raise ValueError("Secret is empty")
        chunks = []
        for i in range(0, length, ShamirVault.CHUNK_SIZE):
            chunk = secret_bytes[i : i + ShamirVault.CHUNK_SIZE]
            if len(chunk) < ShamirVault.CHUNK_SIZE:
                chunk = chunk.ljust(ShamirVault.CHUNK_SIZE, b"\x00")
            chunks.append(chunk)
        return length, chunks

    @staticmethod
    def split_secret(secret_bytes: bytes, threshold: int, num_shares: int):
        if not isinstance(secret_bytes, (bytes, bytearray)):
            raise ValueError("Secret must be bytes")
        if threshold < 2:
            raise ValueError("Threshold must be at least 2")
        if num_shares < threshold:
            raise ValueError("Number of shares must be >= threshold")

        length, chunks = ShamirVault._split_chunks(bytes(secret_bytes))
        header = struct.pack(ShamirVault.HEADER_FMT, ShamirVault.MAGIC, ShamirVault.VERSION, length)

        aggregated = {}
        for chunk in chunks:
            shares = Shamir.split(threshold, num_shares, chunk)
            for idx, share in shares:
                aggregated.setdefault(idx, []).append(share)

        out = []
        for idx in sorted(aggregated.keys()):
            payload = header + b"".join(aggregated[idx])
            out.append((idx, hexlify(payload).decode("ascii")))
        return out

    @staticmethod
    def combine_shares(shares_list):
        if not shares_list:
            raise ValueError("No shares provided")

        parsed = []
        for idx, share_hex in shares_list:
            parsed.append((int(idx), unhexlify(share_hex)))

        first = parsed[0][1]
        if len(first) == ShamirVault.CHUNK_SIZE:
            return Shamir.combine([(idx, raw) for idx, raw in parsed])

        if len(first) < ShamirVault.HEADER_SIZE:
            raise ValueError("Invalid share length")

        magic, version, length = struct.unpack(
            ShamirVault.HEADER_FMT, first[: ShamirVault.HEADER_SIZE]
        )
        if magic != ShamirVault.MAGIC or version != ShamirVault.VERSION:
            raise ValueError("Unsupported share format")

        payload_len = len(first) - ShamirVault.HEADER_SIZE
        if payload_len % ShamirVault.CHUNK_SIZE != 0:
            raise ValueError("Invalid share payload")

        chunk_count = payload_len // ShamirVault.CHUNK_SIZE
        for _, raw in parsed:
            if len(raw) != len(first):
                raise ValueError("Inconsistent share length")
            m, v, l = struct.unpack(
                ShamirVault.HEADER_FMT, raw[: ShamirVault.HEADER_SIZE]
            )
            if m != magic or v != version or l != length:
                raise ValueError("Mismatched share metadata")

        chunks = []
        for i in range(chunk_count):
            start = ShamirVault.HEADER_SIZE + i * ShamirVault.CHUNK_SIZE
            end = start + ShamirVault.CHUNK_SIZE
            chunk_shares = [(idx, raw[start:end]) for idx, raw in parsed]
            chunks.append(Shamir.combine(chunk_shares))

        return b"".join(chunks)[:length]


