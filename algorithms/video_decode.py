DELIMITER = b"#####"
HASH_DELIMITER = "#####HASH#####"


def decode_video(input_path):
    """
    Full payload extraction
    """
    with open(input_path, "rb") as f:
        data = f.read()

    if DELIMITER not in data:
        return None

    message = data.split(DELIMITER)[-1]

    return message.decode(errors="ignore")


def decode_video_header(input_path):
    """
    Fast header-only extraction:
    Extract SHA256 hash + HASH_DELIMITER
    """
    with open(input_path, "rb") as f:
        data = f.read()

    if DELIMITER not in data:
        return None

    payload = data.split(DELIMITER)[-1]

    header_length = 64 + len(HASH_DELIMITER)

    header = payload[:header_length]

    return header.decode(errors="ignore")


def decode_video_full(input_path):
    return decode_video(input_path)


def extract_video_hash(header_payload):
    if not header_payload:
        return None

    if HASH_DELIMITER not in header_payload:
        return None

    stored_hash = header_payload.split(HASH_DELIMITER, 1)[0]

    if len(stored_hash) != 64:
        return None

    return stored_hash
