# AI Speech To Text

AI Speech-to-Text web application built with Python, Flask,
Whisper AI and NLP.

## Features

- Audio upload
- Speech-to-text conversion
- Whisper AI
- NLP analysis
- Keyword extraction
- Word counting
- Sentence counting
- Extractive text summarization
- Sentiment analysis
- HTML report generation
- n8n workflow integration
- Responsive web interface

## Project Structure

AI_Speech_To_Text/

├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── audio/
│   ├── transcripts/
│   └── reports/
│
├── models/
│
├── src/
│   ├── speech_to_text.py
│   ├── transcription.py
│   ├── nlp_analysis.py
│   ├── summarizer.py
│   ├── sentiment.py
│   └── report_generator.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── report.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── n8n/
    └── workflow.json

## Installation

Create a virtual environment:

python -m venv venv

Activate on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Download TextBlob data:

python -m textblob.download_corpora

## Run Application

python app.py

Open:

http://127.0.0.1:5000

## n8n

Start n8n:

n8n

Then open the n8n interface and import:

n8n/workflow.json

## Workflow

Audio
   ↓
Whisper Speech Recognition
   ↓
Transcript
   ↓
NLP Analysis
   ↓
Keyword Extraction
   ↓
Summarization
   ↓
Sentiment Analysis
   ↓
HTML Report