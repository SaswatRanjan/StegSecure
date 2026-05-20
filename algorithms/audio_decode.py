import wave

DELIMITER = "#####"
HASH_DELIMITER = "#####HASH#####"


def binary_to_text(binary):
    chars = []

    for i in range(0, len(binary), 8):
        byte = binary[i : i + 8]

        if len(byte) < 8:
            continue

        chars.append(chr(int(byte, 2)))

    return "".join(chars)


def decode_audio(stego_path):
    """
    Full payload extraction
    """
    song = wave.open(stego_path, mode="rb")

    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    extracted_bits = [str(byte & 1) for byte in frame_bytes]
    binary_data = "".join(extracted_bits)

    decoded_text = binary_to_text(binary_data)

    song.close()

    return decoded_text.split(DELIMITER)[0]


def decode_audio_header(stego_path):
    """
    Fast header-only extraction:
    SHA256 hash + HASH_DELIMITER
    """
    song = wave.open(stego_path, mode="rb")

    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    required_chars = 64 + len(HASH_DELIMITER)
    required_bits = required_chars * 8

    extracted_bits = ""

    for byte in frame_bytes:
        extracted_bits += str(byte & 1)

        if len(extracted_bits) >= required_bits:
            break

    song.close()

    header_text = binary_to_text(extracted_bits)

    return header_text


def decode_audio_full(stego_path):
    return decode_audio(stego_path)


def extract_audio_hash(header_payload):
    if not header_payload:
        return None

    if HASH_DELIMITER not in header_payload:
        return None

    stored_hash = header_payload.split(HASH_DELIMITER, 1)[0]

    if len(stored_hash) != 64:
        return None

    return stored_hash
