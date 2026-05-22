import wave
import struct

def text_to_binary(data: bytes):
    return ''.join(format(byte, '08b') for byte in data)

def encode_audio(input_path, message, output_path):

    song = wave.open(input_path, mode='rb')

    frame_bytes = bytearray(
        list(song.readframes(song.getnframes()))
    )

    message_bytes = message.encode("utf-8")

    payload = (
        struct.pack(">I", len(message_bytes))
        + message_bytes
    )

    binary_data = text_to_binary(payload)

    if len(binary_data) > len(frame_bytes):
        raise ValueError(
            "Audio file too small to hold message"
        )

    for i in range(len(binary_data)):
        frame_bytes[i] = (
            frame_bytes[i] & 254
        ) | int(binary_data[i])

    with wave.open(output_path, 'wb') as fd:

        fd.setparams(song.getparams())

        fd.writeframes(bytes(frame_bytes))

    song.close()