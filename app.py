from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import os
import uuid

from quality_metrics import (
    calculate_psnr,
    calculate_ssim,
    generate_image_heatmap,
    calculate_audio_snr,
    calculate_audio_mse,
    calculate_video_file_metrics,
)

from algorithms.Encode import encode_lsb
from algorithms.Decode import (
    decode_lsb_header,
    decode_lsb_full,
    extract_hash,
)

from algorithms.audio_encode import encode_audio
from algorithms.audio_decode import (
    decode_audio_header,
    decode_audio_full,
    extract_audio_hash,
)

from algorithms.video_encode import encode_video
from algorithms.video_decode import (
    decode_video_header,
    decode_video_full,
    extract_video_hash,
)

from crypto_utils import (
    encrypt_message,
    decrypt_message,
    bytes_to_text,
    text_to_bytes,
    generate_password_hash,
    verify_password,
)

app = Flask(__name__)

# =========================
# CONFIG
# =========================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# ALLOWED EXTENSIONS
# =========================

ALLOWED_IMAGE = {".png", ".bmp"}
ALLOWED_AUDIO = {".wav", ".flac"}
ALLOWED_VIDEO = {".mp4", ".avi", ".mkv"}


def allowed_file(filename, method):
    ext = os.path.splitext(filename)[1].lower()

    if method == "image":
        return ext in ALLOWED_IMAGE

    elif method == "audio":
        return ext in ALLOWED_AUDIO

    elif method == "video":
        return ext in ALLOWED_VIDEO

    return False


# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/tool")
def tool():
    return render_template("tool.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


# =========================
# DOWNLOAD ROUTE
# =========================

@app.route("/download/<filename>")
def download_file(filename):

    safe_filename = secure_filename(filename)

    return send_from_directory(
        app.config["OUTPUT_FOLDER"],
        safe_filename,
        as_attachment=True
    )


# =========================
# ENCODE
# =========================

@app.route("/encode", methods=["POST"])
def encode():

    try:

        uploaded_file = request.files.get("image")
        message = request.form.get("message")
        password = request.form.get("password")
        method = request.form.get("stegMethod")

        if not uploaded_file or not message or not method:
            return jsonify({
                "status": "error",
                "message": "All fields required"
            })

        if not password:
            return jsonify({
                "status": "error",
                "message": "Password required"
            })

        if not allowed_file(uploaded_file.filename, method):
            return jsonify({
                "status": "error",
                "message": "Unsupported file format"
            })

        # =========================
        # SECURE FILENAMES
        # =========================

        original_name = secure_filename(uploaded_file.filename)

        ext = os.path.splitext(original_name)[1]

        unique_name = f"{uuid.uuid4().hex}{ext}"

        input_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )

        output_filename = f"stego_{uuid.uuid4().hex}{ext}"

        output_path = os.path.join(
            OUTPUT_FOLDER,
            output_filename
        )

        uploaded_file.save(input_path)

        # =========================
        # ENCRYPTION
        # =========================

        password_hash = generate_password_hash(password)

        encrypted = encrypt_message(message, password)

        encrypted_text = bytes_to_text(encrypted)

        final_payload = (
            password_hash
            + "#####HASH#####"
            + encrypted_text
        )

        # =========================
        # IMAGE
        # =========================

        if method == "image":

            encode_lsb(
                input_path,
                final_payload,
                output_path
            )

            psnr_value = calculate_psnr(
                input_path,
                output_path
            )

            ssim_value = calculate_ssim(
                input_path,
                output_path
            )

            heatmap_filename = (
                "heatmap_"
                + uuid.uuid4().hex
                + ".png"
            )

            heatmap_path = os.path.join(
                OUTPUT_FOLDER,
                heatmap_filename
            )

            generate_image_heatmap(
                input_path,
                output_path,
                heatmap_path
            )

            metrics = {
                "psnr": psnr_value,
                "ssim": ssim_value,
                "heatmap": heatmap_filename
            }

        # =========================
        # AUDIO
        # =========================

        elif method == "audio":

            encode_audio(
                input_path,
                final_payload,
                output_path
            )

            snr_value = calculate_audio_snr(
                input_path,
                output_path
            )

            mse_value = calculate_audio_mse(
                input_path,
                output_path
            )

            metrics = {
                "snr": snr_value,
                "mse": mse_value
            }

        # =========================
        # VIDEO
        # =========================

        elif method == "video":

            encode_video(
                input_path,
                final_payload,
                output_path
            )

            metrics = calculate_video_file_metrics(
                input_path,
                output_path
            )

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid method"
            })

        # =========================
        # FILE INFO
        # =========================

        file_size = round(
            os.path.getsize(output_path)
            / (1024 * 1024),
            2
        )

        file_extension = os.path.splitext(
            output_path
        )[1].upper()

        return jsonify({
            "status": "success",
            "message": "Encoding successful",
            "metrics": metrics,
            "output_file": output_filename,
            "file_size": f"{file_size} MB",
            "file_type": file_extension
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })


# =========================
# DECODE
# =========================

@app.route("/decode", methods=["POST"])
def decode():

    try:

        uploaded_file = request.files.get("image")
        password = request.form.get("password")
        method = request.form.get("stegMethod")

        if not uploaded_file or not method:
            return jsonify({
                "status": "error",
                "message": "File and method required"
            })

        if not password:
            return jsonify({
                "status": "error",
                "message": "Password required"
            })

        if not allowed_file(uploaded_file.filename, method):
            return jsonify({
                "status": "error",
                "message": "Unsupported file format"
            })

        original_name = secure_filename(uploaded_file.filename)

        ext = os.path.splitext(original_name)[1]

        unique_name = f"{uuid.uuid4().hex}{ext}"

        input_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )

        uploaded_file.save(input_path)

        # =========================
        # IMAGE
        # =========================

        if method == "image":

            header = decode_lsb_header(input_path)

            stored_hash = extract_hash(header)

            if not stored_hash or not verify_password(password, stored_hash):

                return jsonify({
                    "status": "error",
                    "message": "Incorrect password or corrupted hidden data"
                })

            full_payload = decode_lsb_full(input_path)

        # =========================
        # AUDIO
        # =========================

        elif method == "audio":

            header = decode_audio_header(input_path)

            stored_hash = extract_audio_hash(header)

            if not stored_hash or not verify_password(password, stored_hash):

                return jsonify({
                    "status": "error",
                    "message": "Incorrect password or corrupted hidden data"
                })

            full_payload = decode_audio_full(input_path)

        # =========================
        # VIDEO
        # =========================

        elif method == "video":

            header = decode_video_header(input_path)

            stored_hash = extract_video_hash(header)

            if not stored_hash or not verify_password(password, stored_hash):

                return jsonify({
                    "status": "error",
                    "message": "Incorrect password or corrupted hidden data"
                })

            full_payload = decode_video_full(input_path)

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid method"
            })

        # =========================
        # PAYLOAD VALIDATION
        # =========================

        if not full_payload:
            return jsonify({
                "status": "error",
                "message": "No hidden message found"
            })

        if "#####HASH#####" not in full_payload:
            return jsonify({
                "status": "error",
                "message": "Corrupted or invalid hidden data"
            })

        stored_hash, encrypted_text = full_payload.split(
            "#####HASH#####",
            1
        )

        encrypted_bytes = text_to_bytes(encrypted_text)

        try:

            message = decrypt_message(
                encrypted_bytes,
                password
            )

        except Exception:

            return jsonify({
                "status": "error",
                "message": "Incorrect password or corrupted data"
            })

        return jsonify({
            "status": "success",
            "message": message
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )