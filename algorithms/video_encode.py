def encode_video(input_path, message, output_path):

    with open(input_path, "rb") as f:
        video_data = f.read()

    message_bytes = message.encode()
    delimiter = b"#####"

    with open(output_path, "wb") as f:
        f.write(video_data + delimiter + message_bytes)