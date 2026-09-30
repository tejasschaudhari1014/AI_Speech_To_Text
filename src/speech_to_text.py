import os
import subprocess
import shutil
import wave

import numpy as np
import whisper
import imageio_ffmpeg


_model = None

# 5 minutes per chunk
CHUNK_DURATION = 300

# Whisper uses 16 kHz audio
SAMPLE_RATE = 16000


# =========================================================
# LOAD WHISPER MODEL
# =========================================================

def load_model():

    global _model

    if _model is None:

        print("Loading Whisper model...")

        _model = whisper.load_model("tiny")

        print("Whisper model loaded.")

    return _model


# =========================================================
# GET BUNDLED FFMPEG
# =========================================================

def get_ffmpeg():

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    print("FFmpeg:")
    print(ffmpeg_path)

    if not os.path.exists(ffmpeg_path):

        raise FileNotFoundError(
            f"FFmpeg executable not found:\n{ffmpeg_path}"
        )

    return ffmpeg_path


# =========================================================
# CREATE AUDIO CHUNKS
# =========================================================

def create_audio_chunks(audio_path):

    if not os.path.exists(audio_path):

        raise FileNotFoundError(
            f"Audio file not found:\n{audio_path}"
        )

    ffmpeg_path = get_ffmpeg()

    filename = os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    parent_folder = os.path.dirname(
        audio_path
    )

    chunks_folder = os.path.join(
        parent_folder,
        filename + "_chunks"
    )

    # Remove old chunks
    if os.path.exists(chunks_folder):

        shutil.rmtree(chunks_folder)

    os.makedirs(
        chunks_folder,
        exist_ok=True
    )

    output_pattern = os.path.join(
        chunks_folder,
        "chunk_%03d.wav"
    )

    command = [
        ffmpeg_path,

        "-y",

        "-i",
        audio_path,

        "-vn",

        "-ac",
        "1",

        "-ar",
        str(SAMPLE_RATE),

        "-sample_fmt",
        "s16",

        "-f",
        "segment",

        "-segment_time",
        str(CHUNK_DURATION),

        "-reset_timestamps",
        "1",

        output_pattern
    ]

    print()
    print("====================================")
    print("Creating audio chunks...")
    print("====================================")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg failed:\n"
            + result.stderr
        )

    chunks = []

    for name in sorted(
        os.listdir(chunks_folder)
    ):

        if name.lower().endswith(".wav"):

            path = os.path.join(
                chunks_folder,
                name
            )

            if os.path.getsize(path) > 1000:

                chunks.append(path)

    if not chunks:

        raise RuntimeError(
            "No WAV chunks were created."
        )

    print(
        "Created",
        len(chunks),
        "audio chunks."
    )

    return chunks, chunks_folder


# =========================================================
# READ WAV DIRECTLY
# =========================================================

def read_wav_file(wav_path):

    """
    Read WAV file directly using Python's wave module.

    This avoids Whisper trying to call the external
    'ffmpeg' command from Windows PATH.
    """

    with wave.open(
        wav_path,
        "rb"
    ) as wav:

        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frames = wav.getnframes()

        audio_bytes = wav.readframes(
            frames
        )

    # -----------------------------------------------------
    # Convert PCM data to numpy
    # -----------------------------------------------------

    if sample_width == 2:

        audio = np.frombuffer(
            audio_bytes,
            dtype=np.int16
        )

    elif sample_width == 1:

        audio = (
            np.frombuffer(
                audio_bytes,
                dtype=np.uint8
            ).astype(np.float32)
            - 128
        )

    elif sample_width == 4:

        audio = np.frombuffer(
            audio_bytes,
            dtype=np.int32
        )

    else:

        raise ValueError(
            f"Unsupported WAV sample width: "
            f"{sample_width}"
        )

    # -----------------------------------------------------
    # Convert to float32
    # -----------------------------------------------------

    audio = audio.astype(
        np.float32
    )

    if sample_width == 2:

        audio = audio / 32768.0

    elif sample_width == 4:

        audio = audio / 2147483648.0

    elif sample_width == 1:

        audio = audio / 128.0

    # -----------------------------------------------------
    # Convert stereo → mono
    # -----------------------------------------------------

    if channels > 1:

        audio = audio.reshape(
            -1,
            channels
        )

        audio = np.mean(
            audio,
            axis=1
        )

    # -----------------------------------------------------
    # Verify sample rate
    # -----------------------------------------------------

    if sample_rate != SAMPLE_RATE:

        raise ValueError(
            f"Expected {SAMPLE_RATE} Hz audio, "
            f"but received {sample_rate} Hz."
        )

    return audio


# =========================================================
# TRANSCRIBE LARGE AUDIO
# =========================================================

def speech_to_text(audio_path):

    if not os.path.exists(audio_path):

        raise FileNotFoundError(
            f"Audio file not found:\n{audio_path}"
        )

    allowed_extensions = {
        ".mp3",
        ".mp4",
        ".wav",
        ".m4a",
        ".flac",
        ".ogg"
    }

    extension = os.path.splitext(
        audio_path
    )[1].lower()

    if extension not in allowed_extensions:

        raise ValueError(
            "Unsupported file format. "
            "Use MP3, MP4, WAV, M4A, FLAC or OGG."
        )

    print()
    print("====================================")
    print("STARTING LARGE AUDIO TRANSCRIPTION")
    print("====================================")

    print("Input file:")
    print(audio_path)

    chunks = []
    chunks_folder = None

    try:

        # -------------------------------------------------
        # CREATE CHUNKS
        # -------------------------------------------------

        chunks, chunks_folder = create_audio_chunks(
            audio_path
        )

        # -------------------------------------------------
        # LOAD WHISPER
        # -------------------------------------------------

        model = load_model()

        transcripts = []

        total_chunks = len(chunks)

        # -------------------------------------------------
        # PROCESS EACH CHUNK
        # -------------------------------------------------

        for index, chunk_path in enumerate(
            chunks,
            start=1
        ):

            print()
            print("------------------------------------")
            print(
                f"Processing chunk {index}/{total_chunks}"
            )
            print("------------------------------------")

            try:

                # -------------------------------------------------
                # READ WAV DIRECTLY
                # -------------------------------------------------

                audio = read_wav_file(
                    chunk_path
                )

                print(
                    "Audio samples:",
                    len(audio)
                )

                print(
                    "Audio duration:",
                    round(
                        len(audio) / SAMPLE_RATE,
                        2
                    ),
                    "seconds"
                )

                # -------------------------------------------------
                # SEND NUMPY AUDIO TO WHISPER
                #
                # IMPORTANT:
                # We pass the numpy array instead of the
                # WAV filename.
                #
                # Therefore Whisper does NOT call external
                # FFmpeg.
                # -------------------------------------------------

                result = model.transcribe(
                    audio,
                    fp16=False,
                    temperature=0,
                    condition_on_previous_text=False
                )

                text = result.get(
                    "text",
                    ""
                ).strip()

                language = result.get(
                    "language",
                    "unknown"
                )

                print(
                    "Detected language:",
                    language
                )

                print(
                    "Text length:",
                    len(text)
                )

                if text:

                    transcripts.append(
                        text
                    )

                    print(
                        f"Chunk {index} completed."
                    )

                else:

                    print(
                        f"Chunk {index}: "
                        "No speech detected."
                    )

            except Exception as e:

                print(
                    f"Chunk {index} failed:"
                )

                print(
                    str(e)
                )

                # Continue processing
                # remaining chunks

        # -------------------------------------------------
        # COMBINE TRANSCRIPTS
        # -------------------------------------------------

        transcript = "\n\n".join(
            transcripts
        ).strip()

        if not transcript:

            raise RuntimeError(
                "No speech was detected in the audio file."
            )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print()
        print("====================================")
        print("TRANSCRIPTION COMPLETED")
        print("====================================")

        print(
            "Total chunks:",
            total_chunks
        )

        print(
            "Successful chunks:",
            len(transcripts)
        )

        print(
            "Transcript characters:",
            len(transcript)
        )

        return transcript

    finally:

        # -------------------------------------------------
        # DELETE TEMPORARY CHUNKS
        # -------------------------------------------------

        if chunks_folder:

            if os.path.exists(
                chunks_folder
            ):

                shutil.rmtree(
                    chunks_folder,
                    ignore_errors=True
                )

                print(
                    "Temporary chunks deleted."
                )