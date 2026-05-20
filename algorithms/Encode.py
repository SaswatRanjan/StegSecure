from PIL import Image
import numpy as np


def encode_lsb(input_image, message, output_image):
    image = Image.open(input_image)
    image = image.convert("RGB")

    data = np.array(image)
    flat = data.reshape(-1)

    # Convert message to bytes
    message_bytes = message.encode("utf-8")

    # Add 4-byte length header
    length_bytes = len(message_bytes).to_bytes(4, "big")
    payload = length_bytes + message_bytes

    # Convert payload to bits
    bits = ""
    for byte in payload:
        bits += format(byte, "08b")

    if len(bits) > len(flat):
        raise ValueError("Image resolution too low for this message.")

    # Embed bits
    for i in range(len(bits)):
        flat[i] = (flat[i] & 254) | int(bits[i])

    encoded = flat.reshape(data.shape)
    Image.fromarray(encoded.astype("uint8")).save(output_image)
