from datetime import datetime
import html


def generate_report(
    transcript,
    nlp_result,
    summary,
    sentiment,
    output_path
):

    keywords_html = ""

    for word, count in nlp_result["keywords"]:
        keywords_html += f"""
        <li>
            <strong>{html.escape(word)}</strong>
            - {count}
        </li>
        """

    safe_transcript = html.escape(transcript)
    safe_summary = html.escape(summary)

    report = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>AI Speech Analysis Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f6f9;
    margin: 0;
    padding: 30px;
}}

.container {{
    max-width: 1000px;
    margin: auto;
}}

.card {{
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}}

h1 {{
    text-align: center;
}}

.stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}}

.stat {{
    padding: 20px;
    background: #eef2ff;
    text-align: center;
    border-radius: 10px;
}}

.stat h2 {{
    margin: 0;
}}

.transcript {{
    white-space: pre-wrap;
    line-height: 1.7;
}}

</style>

</head>

<body>

<div class="container">

<h1>AI Speech-to-Text Analysis Report</h1>

<div class="card">

<p>
Generated on:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</p>

</div>

<div class="card">

<h2>Statistics</h2>

<div class="stats">

<div class="stat">
<h2>{nlp_result["word_count"]}</h2>
<p>Words</p>
</div>

<div class="stat">
<h2>{nlp_result["sentence_count"]}</h2>
<p>Sentences</p>
</div>

<div class="stat">
<h2>{nlp_result["unique_words"]}</h2>
<p>Unique Words</p>
</div>

<div class="stat">
<h2>{nlp_result["character_count"]}</h2>
<p>Characters</p>
</div>

</div>

</div>

<div class="card">

<h2>Transcript</h2>

<div class="transcript">
{safe_transcript}
</div>

</div>

<div class="card">

<h2>Summary</h2>

<p>
{safe_summary}
</p>

</div>

<div class="card">

<h2>Sentiment Analysis</h2>

<p>
<strong>Sentiment:</strong>
{sentiment["label"]}
</p>

<p>
<strong>Polarity:</strong>
{sentiment["polarity"]}
</p>

<p>
<strong>Subjectivity:</strong>
{sentiment["subjectivity"]}
</p>

</div>

<div class="card">

<h2>Top Keywords</h2>

<ul>

{keywords_html}

</ul>

</div>

</div>

</body>
</html>
"""

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    return output_path