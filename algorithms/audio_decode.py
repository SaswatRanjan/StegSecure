import wave
import struct

HASH_DELIMITER = "#####HASH#####"

def bits_to_bytes(bits):

    output = bytearray()

    for i in range(0, len(bits), 8):

        byte = bits[i:i+8]

        if len(byte) < 8:
            break

        output.append(int(byte, 2))

    return bytes(output)

def decode_audio(stego_path):

    song = wave.open(stego_path, mode="rb")

    frame_bytes = bytearray(
        list(song.readframes(song.getnframes()))
    )

    bits = ''.join(
        str(byte & 1)
        for byte in frame_bytes
    )

    raw = bits_to_bytes(bits)

    song.close()

    if len(raw) < 4:
        return None

    msg_length = struct.unpack(
        ">I",
        raw[:4]
    )[0]

    message_bytes = raw[4:4+msg_length]

    return message_bytes.decode(
        "utf-8",
        errors="ignore"
    )

def decode_audio_header(stego_path):

    full = decode_audio(stego_path)

    if not full:
        return None

    header_length = 64 + len(HASH_DELIMITER)

    return full[:header_length]

def decode_audio_full(stego_path):
    return decode_audio(stego_path)

def extract_audio_hash(header_payload):

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