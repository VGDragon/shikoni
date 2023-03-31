import numpy as np


class Message:
    def __int__(self):
        header = "shikoni"

    def example(self):
        file = "temp_file.shikoni"
        header = "shikoni"
        message_bytes = b""
        message_bytes += header.encode("utf-8") #header
        message_bytes += bytes([1])  # message_type_bytes
        with open(file, "wb") as f:
            f.write(message_bytes)

    def example_read(self):
        file = "temp_file.shikoni"
        with open(file, "rb") as f:
            header = f.read(7).decode()
            message_type_bytes = ord(f.read(1))
            message_type = ord(f.read(message_type_bytes))

        print()


