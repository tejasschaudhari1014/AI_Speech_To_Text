
import os

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory
)

from src.speech_to_text import speech_to_text
from src.nlp_analysis import analyze_text
from src.summarizer import summarize_text
from src.sentiment import analyze_sentiment
from src.report_generator import generate_report


app = Flask(__name__)


# =========================================================
# FOLDERS
# =========================================================

UPLOAD_FOLDER = "data/audio"
TRANSCRIPT_FOLDER = "data/transcripts"
REPORT_FOLDER = "data/reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# ALLOWED AUDIO / VIDEO FORMATS
# =========================================================

ALLOWED_EXTENSIONS = {
    ".mp3",
    ".mp4",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg"
}


def allowed_file(filename):

    extension = os.path.splitext(filename)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# PROCESS AUDIO
# =========================================================

@app.route("/process", methods=["POST"])
def process_audio():

    if "audio" not in request.files:

        return "No audio file uploaded", 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":

        return "Please select an audio file", 400

    filename = audio_file.filename

    # Check file format
    if not allowed_file(filename):

        return (
            "Unsupported file format. "
            "Please upload MP3, MP4, WAV, M4A, FLAC or OGG.",
            400
        )

    # Save uploaded file
    audio_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    audio_file.save(audio_path)

    try:

        # =================================================
        # 1. SPEECH TO TEXT
        # =================================================

        
        transcript = speech_to_text(audio_path)


        # =================================================
        # 2. SAVE TRANSCRIPT
        # =================================================

        transcript_name = (
            os.path.splitext(filename)[0]
            + ".txt"
        )

        transcript_path = os.path.join(
            TRANSCRIPT_FOLDER,
            transcript_name
        )

        with open(
            transcript_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(transcript)


        # =================================================
        # 3. NLP ANALYSIS
        # =================================================

        nlp_result = analyze_text(
            transcript
        )


        # =================================================
        # 4. SUMMARY
        # =================================================

        summary = summarize_text(
            transcript
        )


        # =================================================
        # 5. SENTIMENT ANALYSIS
        # =================================================

        sentiment_result = analyze_sentiment(
            transcript
        )


        # =================================================
        # 6. GENERATE REPORT
        # =================================================

        report_filename = (
            os.path.splitext(filename)[0]
            + "_report.html"
        )

        report_path = os.path.join(
            REPORT_FOLDER,
            report_filename
        )

        generate_report(
            transcript=transcript,
            nlp_result=nlp_result,
            summary=summary,
            sentiment=sentiment_result,
            output_path=report_path
        )


        # =================================================
        # 7. SHOW RESULT
        # =================================================

        return render_template(
            "result.html",
            filename=filename,
            transcript=transcript,
            nlp=nlp_result,
            summary=summary,
            sentiment=sentiment_result,
            report_filename=report_filename
        )


    except Exception as e:
        import traceback

        print("\n========== PROCESSING ERROR ==========")
        traceback.print_exc()
        print("=====================================\n")

        return (
            f"Processing error: {str(e)}",
            500
        )


# =========================================================
# VIEW REPORT
# =========================================================

@app.route("/report/<filename>")
def report(filename):

    return send_from_directory(
        REPORT_FOLDER,
        filename
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

