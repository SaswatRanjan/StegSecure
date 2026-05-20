import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def generate_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def derive_key(password: str) -> bytes:
    """
    Derive a 256-bit AES key from password
    """
    return hashlib.sha256(password.encode()).digest()


def encrypt_message(message: str, password: str) -> bytes:
    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_CBC)

    ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
    return cipher.iv + ciphertext


def decrypt_message(encrypted_data: bytes, password: str) -> str:
    key = derive_key(password)

    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    return plaintext.decode("utf-8")


def bytes_to_text(data: bytes) -> str:
    """
    Convert encrypted bytes to Base64-safe text
    """
    return base64.b64encode(data).decode("utf-8")


def text_to_bytes(text: str) -> bytes:
    """
    Convert Base64 text back to encrypted bytes
    """
    return base64.b64decode(text.encode("utf-8"))
