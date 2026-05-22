import cv2
import math
import wave
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt


# ================= IMAGE =================
def calculate_psnr(original_path, stego_path):
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    mse = np.mean((original - stego) ** 2)

    if mse == 0:
        return 100

    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

    return round(psnr, 2)


def calculate_ssim(original_path, stego_path):
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    stego_gray = cv2.cvtColor(stego, cv2.COLOR_BGR2GRAY)

    score, _ = ssim(original_gray, stego_gray, full=True)

    return round(score, 4)


def generate_image_heatmap(original_path, stego_path, output_path):
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    diff = cv2.absdiff(original, stego)

    heatmap = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    plt.figure(figsize=(8, 6))
    plt.imshow(heatmap, cmap="hot", interpolation="nearest")
    plt.colorbar()
    plt.title("Image Distortion Heatmap")

    plt.savefig(output_path)
    plt.close()

    return output_path


# ================= AUDIO =================
def calculate_audio_mse(original_path, stego_path):

    with wave.open(original_path, "rb") as orig:

        orig_frames = np.frombuffer(
            orig.readframes(orig.getnframes()),
            dtype=np.int16
        ).astype(np.float64)

    with wave.open(stego_path, "rb") as steg:

        steg_frames = np.frombuffer(
            steg.readframes(steg.getnframes()),
            dtype=np.int16
        ).astype(np.float64)

    min_len = min(len(orig_frames), len(steg_frames))

    mse = np.mean(
        (
            orig_frames[:min_len]
            - steg_frames[:min_len]
        ) ** 2
    )

    if np.isnan(mse):
        return 0

    return round(float(mse), 4)


def calculate_audio_snr(original_path, stego_path):

    with wave.open(original_path, "rb") as orig:

        orig_frames = np.frombuffer(
            orig.readframes(orig.getnframes()),
            dtype=np.int16
        ).astype(np.float64)

    with wave.open(stego_path, "rb") as steg:

        steg_frames = np.frombuffer(
            steg.readframes(steg.getnframes()),
            dtype=np.int16
        ).astype(np.float64)

    min_len = min(len(orig_frames), len(steg_frames))

    original_signal = orig_frames[:min_len]

    stego_signal = steg_frames[:min_len]

    signal_power = np.mean(original_signal ** 2)

    noise_power = np.mean(
        (original_signal - stego_signal) ** 2
    )

    if (
        noise_power <= 0
        or signal_power <= 0
        or np.isnan(noise_power)
        or np.isnan(signal_power)
    ):
        return 100

    snr = 10 * math.log10(
        signal_power / noise_power
    )

    return round(snr, 2)


# ================= VIDEO =================
def calculate_video_file_metrics(original_path, stego_path):
    original_size = os.path.getsize(original_path)
    stego_size = os.path.getsize(stego_path)

    size_difference = stego_size - original_size

    percentage_increase = (
        (size_difference / original_size) * 100 if original_size > 0 else 0
    )

    return {
        "original_size_kb": round(original_size / 1024, 2),
        "stego_size_kb": round(stego_size / 1024, 2),
        "size_increase_kb": round(size_difference / 1024, 2),
        "percentage_increase": round(percentage_increase, 2),
    }
