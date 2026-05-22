import struct

DELIMITER = b"STEGSECURE"

def encode_video(input_path, message, output_path):

    with open(input_path, "rb") as f:
        video_data = f.read()

    message_bytes = message.encode("utf-8")

    payload = (
        DELIMITER
        + struct.pack(">I", len(message_bytes))
        + message_bytes
    )

    with open(output_path, "wb") as f:
        f.write(video_data + payload)