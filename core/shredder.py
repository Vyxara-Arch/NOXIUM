import os
import secrets


class Shredder:
    @staticmethod
    def wipe_file(file_path: str):

        if not os.path.exists(file_path):
            return

        file_size = os.path.getsize(file_path)

        with open(file_path, "wb") as f:

            f.write(b"\x00" * file_size)
            f.flush()
            os.fsync(f.fileno())
            f.seek(0)

            f.write(b"\xff" * file_size)
            f.flush()
            os.fsync(f.fileno())
            f.seek(0)

            f.write(secrets.token_bytes(file_size))
            f.flush()
            os.fsync(f.fileno())

        os.remove(file_path)
