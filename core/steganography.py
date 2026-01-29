from PIL import Image
import struct
import os
import zlib


class StegoEngine:
    MAGIC = b"NXSG"
    VERSION = 1
    HEADER_FMT = ">4sBII"
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    @staticmethod
    def get_capacity(image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                total_bits = width * height * 3
                total_bytes = total_bits // 8
                return max(0, total_bytes - StegoEngine.HEADER_SIZE)
        except Exception:
            return 0

    @staticmethod
    def _open_rgb_image(path: str) -> Image.Image:
        with Image.open(path) as img:
            has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
            if has_alpha:
                return img.convert("RGBA")
            return img.convert("RGB")

    @staticmethod
    def _bit_generator(pixels, width, height):
        for y in range(height):
            for x in range(width):
                px = pixels[x, y]
                r, g, b = px[:3]
                yield r & 1
                yield g & 1
                yield b & 1

    @staticmethod
    def _read_bytes(bit_iter, count: int) -> bytes:
        out = bytearray()
        for _ in range(count):
            val = 0
            for _ in range(8):
                val = (val << 1) | next(bit_iter)
            out.append(val)
        return bytes(out)

    @staticmethod
    def encode(cover_path, secret_path, output_path):
        if not os.path.exists(cover_path):
            raise FileNotFoundError(f"Cover image not found: {cover_path}")
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"Secret file not found: {secret_path}")

        img = StegoEngine._open_rgb_image(cover_path)
        pixels = img.load()
        width, height = img.size

        with open(secret_path, "rb") as f:
            data = f.read()

        crc = zlib.crc32(data) & 0xFFFFFFFF
        header = struct.pack(
            StegoEngine.HEADER_FMT, StegoEngine.MAGIC, StegoEngine.VERSION, len(data), crc
        )
        payload = header + data

        required_bits = len(payload) * 8
        available_bits = width * height * 3

        if required_bits > available_bits:
            raise ValueError(
                f"Insufficient capacity. Need {required_bits//8} bytes, have {available_bits//8} bytes."
            )

        data_idx = 0
        bit_idx = 0
        payload_len = len(payload)

        for y in range(height):
            for x in range(width):
                px = pixels[x, y]
                r, g, b = px[:3]
                rgb = [r, g, b]

                for i in range(3):
                    if data_idx < payload_len:
                        bit = (payload[data_idx] >> (7 - bit_idx)) & 1
                        rgb[i] = (rgb[i] & ~1) | bit
                        bit_idx += 1
                        if bit_idx == 8:
                            bit_idx = 0
                            data_idx += 1
                    else:
                        break

                if len(px) == 4:
                    pixels[x, y] = (rgb[0], rgb[1], rgb[2], px[3])
                else:
                    pixels[x, y] = tuple(rgb)

                if data_idx >= payload_len:
                    break
            if data_idx >= payload_len:
                break

        img.save(output_path, "PNG")
        return True

    @staticmethod
    def decode(stego_path, output_path):
        if not os.path.exists(stego_path):
            raise FileNotFoundError("Stego image not found")

        img = StegoEngine._open_rgb_image(stego_path)
        pixels = img.load()
        width, height = img.size

        capacity = (width * height * 3) // 8
        bg = StegoEngine._bit_generator(pixels, width, height)

        try:
            prefix = StegoEngine._read_bytes(bg, 4)
        except StopIteration:
            raise ValueError("Image too small or corrupted header")

        if prefix == StegoEngine.MAGIC:
            try:
                rest = StegoEngine._read_bytes(bg, StegoEngine.HEADER_SIZE - 4)
            except StopIteration:
                raise ValueError("Image too small or corrupted header")

            magic, version, length_val, crc = struct.unpack(
                StegoEngine.HEADER_FMT, prefix + rest
            )
            if version != StegoEngine.VERSION:
                raise ValueError("Unsupported stego version")

            if length_val > capacity - StegoEngine.HEADER_SIZE:
                raise ValueError("Extracted length header seems corrupt")

            try:
                data = StegoEngine._read_bytes(bg, length_val)
            except StopIteration:
                raise ValueError("Unexpected end of image data")
            if (zlib.crc32(data) & 0xFFFFFFFF) != crc:
                raise ValueError("Stego payload corrupted (CRC mismatch)")
        else:
            length_val = struct.unpack(">I", prefix)[0]
            if length_val > capacity - 4:
                raise ValueError("Extracted length header seems corrupt")
            try:
                data = StegoEngine._read_bytes(bg, length_val)
            except StopIteration:
                raise ValueError("Unexpected end of image data")

        with open(output_path, "wb") as f:
            f.write(data)

        return len(data)
