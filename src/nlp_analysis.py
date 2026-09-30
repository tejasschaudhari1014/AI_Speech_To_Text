import re
from collections import Counter


STOP_WORDS = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "this",
    "that",
    "it",
    "was",
    "are",
    "as",
    "be",
    "at",
    "by",
    "from",
    "we",
    "you",
    "i",
    "he",
    "she",
    "they",
    "have",
    "has",
    "had",
    "will",
    "would",
    "can",
    "could"
}


def clean_words(text):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text.lower()
    )

    return [
        word for word in words
        if word not in STOP_WORDS
    ]


def analyze_text(text):

    words = clean_words(text)

    sentences = re.split(
        r"[.!?]+",
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    word_count = len(words)
    sentence_count = len(sentences)

    character_count = len(text)

    unique_words = len(set(words))

    frequency = Counter(words)

    keywords = frequency.most_common(10)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "character_count": character_count,
        "unique_words": unique_words,
        "keywords": keywords
    }