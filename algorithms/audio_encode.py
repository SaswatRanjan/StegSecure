import wave

DELIMITER = "#####"


def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)


def encode_audio(input_path, message, output_path):
    song = wave.open(input_path, mode='rb')

    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # add delimiter
    message += DELIMITER
    binary_data = text_to_binary(message)

    if len(binary_data) > len(frame_bytes):
        raise ValueError("Audio file too small to hold message")

    # LSB embedding
    for i in range(len(binary_data)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_data[i])

    modified_frames = bytes(frame_bytes)

    # save new audio
    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(modified_frames)

    song.close()