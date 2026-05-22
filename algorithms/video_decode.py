import struct

DELIMITER = b"STEGSECURE"

HASH_DELIMITER = "#####HASH#####"

def decode_video(input_path):

    with open(input_path, "rb") as f:
        data = f.read()

    if DELIMITER not in data:
        return None

    payload = data.split(DELIMITER)[-1]

    if len(payload) < 4:
        return None

    msg_length = struct.unpack(
        ">I",
        payload[:4]
    )[0]

    message_bytes = payload[4:4+msg_length]

    return message_bytes.decode(
        errors="ignore"
    )

def decode_video_header(input_path):

    full = decode_video(input_path)

    if not full:
        return None

    header_length = 64 + len(HASH_DELIMITER)

    return full[:header_length]

def decode_video_full(input_path):
    return decode_video(input_path)

def extract_video_hash(header_payload):

    if not header_payload:
        return None

    if HASH_DELIMITER not in header_payload:
        return None

    stored_hash = (
        header_payload.split(
            HASH_DELIMITER,
            1
        )[0]
    )

    if len(stored_hash) != 64:
        return None

    return stored_hash