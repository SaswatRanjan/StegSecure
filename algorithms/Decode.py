from PIL import Image
import numpy as np

HASH_DELIMITER = "#####HASH#####"


def decode_lsb(stego_image):
    """
    Full payload extraction
    """
    image = Image.open(stego_image)
    image = image.convert("RGB")

    data = np.array(image)
    flat = data.reshape(-1)

    bits = ""

    for pixel in flat:
        bits += str(pixel & 1)

    extracted_bytes = bytearray()

    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]

        if len(byte) < 8:
            break

        extracted_bytes.append(int(byte, 2))

    if len(extracted_bytes) < 4:
        return None

    msg_length = int.from_bytes(extracted_bytes[:4], "big")

    message_bytes = extracted_bytes[4 : 4 + msg_length]

    return message_bytes.decode("utf-8", errors="ignore")


def decode_lsb_header(stego_image):
    """
    Extract only password hash + delimiter
    """
    image = Image.open(stego_image)
    image = image.convert("RGB")

    data = np.array(image)
    flat = data.reshape(-1)

    bits = ""

    required_chars = 64 + len(HASH_DELIMITER)
    required_bits = (required_chars + 4) * 8

    for pixel in flat:
        bits += str(pixel & 1)

        if len(bits) >= required_bits:
            break

    extracted_bytes = bytearray()

    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]

        if len(byte) < 8:
            break

        extracted_bytes.append(int(byte, 2))

    if len(extracted_bytes) < 4:
        return None

    payload_bytes = extracted_bytes[4:]

    return payload_bytes.decode("utf-8", errors="ignore")


def decode_lsb_full(stego_image):
    return decode_lsb(stego_image)


def extract_hash(header_payload):
    if not header_payload:
        return None

    if HASH_DELIMITER not in header_payload:
        return None

    stored_hash = header_payload.split(HASH_DELIMITER, 1)[0]

    if len(stored_hash) != 64:
        return None

    return stored_hash
