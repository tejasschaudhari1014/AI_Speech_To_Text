import re
from collections import Counter


STOP_WORDS = {
    "the", "is", "a", "an", "and",
    "or", "of", "to", "in", "on",
    "for", "with", "this", "that",
    "it", "was", "are", "as", "be",
    "at", "by", "from"
}


def summarize_text(text, sentence_limit=3):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if len(sentences) <= sentence_limit:
        return text

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text.lower()
    )

    words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    frequency = Counter(words)

    sentence_scores = []

    for index, sentence in enumerate(sentences):

        sentence_words = re.findall(
            r"\b[a-zA-Z]+\b",
            sentence.lower()
        )

        score = sum(
            frequency[word]
            for word in sentence_words
            if word in frequency
        )

        sentence_scores.append(
            (score, index, sentence)
        )

    top_sentences = sorted(
        sentence_scores,
        reverse=True
    )[:sentence_limit]

    top_sentences = sorted(
        top_sentences,
        key=lambda x: x[1]
    )

    summary = " ".join(
        sentence
        for _, _, sentence in top_sentences
    )

    return summary