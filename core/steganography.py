from PIL import Image
import struct
import os


class StegoEngine:
    HEADER_SIZE = 4

    @staticmethod
    def get_capacity(image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                total_bits = width * height * 3
                total_bytes = total_bits // 8
                return total_bytes - StegoEngine.HEADER_SIZE
        except Exception as e:
            return 0

    @staticmethod
    def encode(cover_path, secret_path, output_path):
        if not os.path.exists(cover_path):
            raise FileNotFoundError(f"Cover image not found: {cover_path}")
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"Secret file not found: {secret_path}")

        img = Image.open(cover_path).convert("RGB")
        pixels = img.load()
        width, height = img.size

        with open(secret_path, "rb") as f:
            data = f.read()

        payload = struct.pack(">I", len(data)) + data

        required_bits = len(payload) * 8
        available_bits = width * height * 3

        if required_bits > available_bits:
            raise ValueError(
                f"Insufficient capacity. Need {required_bits//8} bytes, have {available_bits//8} bytes."
            )

        data_idx = 0
        bit_idx = 0
        payload_len = len(payload)

        # Iterating pixels
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
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
                        break  # Done

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

        img = Image.open(stego_path).convert("RGB")
        pixels = img.load()
        width, height = img.size

        def bit_generator():
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    yield r & 1
                    yield g & 1
                    yield b & 1

        bg = bit_generator()

        length_val = 0
        try:
            for _ in range(32):
                length_val = (length_val << 1) | next(bg)
        except StopIteration:
            raise ValueError("Image too small or corrupted header")

        if length_val > width * height * 3 // 8:
            raise ValueError(
                f"Extracted length header seems corrupt: {length_val} bytes"
            )

        data_bytes = bytearray()
        try:
            for _ in range(length_val):
                byte_val = 0
                for _ in range(8):
                    byte_val = (byte_val << 1) | next(bg)
                data_bytes.append(byte_val)
        except StopIteration:
            raise ValueError("Unexpected end of image data")

        with open(output_path, "wb") as f:
            f.write(data_bytes)

        return len(data_bytes)
