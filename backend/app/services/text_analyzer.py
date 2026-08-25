import re
from collections import Counter
import nltk


# ============================================================
# NLTK RESOURCE SETUP
# ============================================================

_nltk_ready = False

def ensure_nltk_resources():
    """
    Check tokenizer resources quietly without blocking network socket downloads.
    """
    global _nltk_ready
    if _nltk_ready:
        return

    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
    ]

    for resource_path, resource_name in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            # Avoid hanging network download attempts if offline or restricted
            pass

    _nltk_ready = True


# ============================================================
# SENSATIONAL LANGUAGE DICTIONARY
# ============================================================

SENSATIONAL_WORDS = {
    "breaking", "shocking", "unbelievable", "explosive", "terrifying",
    "outrage", "outrageous", "scandal", "scandalous", "secret",
    "exposed", "urgent", "warning", "danger", "dangerous",
    "incredible", "amazing", "miracle", "disaster", "destroy",
    "destroyed", "crisis", "bombshell", "horrific", "massive", "ultimate",
}


# ============================================================
# MAIN TEXT ANALYZER
# ============================================================

def analyze_text(text: str) -> dict:
    """
    Analyze article text and calculate stylometric sensationalism indicators.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "average_sentence_length": 0.0,
            "exclamation_count": 0,
            "question_count": 0,
            "uppercase_word_count": 0,
            "repeated_word_ratio": 0.0,
            "sensational_word_count": 0,
            "sensational_words": [],
            "sensationalism_score": 0.0,
        }

    ensure_nltk_resources()

    # Sentence & Word Tokenization with instant Regex Fallback
    try:
        sentences = nltk.tokenize.sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    try:
        words = nltk.tokenize.word_tokenize(text)
    except Exception:
        words = re.findall(r"\b\w+\b|[^\w\s]", text)

    alphabetic_words = [
        word.lower()
        for word in words
        if re.fullmatch(r"[A-Za-z]+", word)
    ]

    word_count = len(alphabetic_words)
    sentence_count = len(sentences) if sentences else (1 if word_count > 0 else 0)

    average_sentence_length = (
        word_count / sentence_count
        if sentence_count
        else 0.0
    )

    exclamation_count = text.count("!")
    question_count = text.count("?")

    uppercase_word_count = sum(
        1
        for word in words
        if len(word) >= 2
        and word.isalpha()
        and word.isupper()
    )

    word_frequency = Counter(alphabetic_words)

    repeated_words = sum(
        count - 1
        for count in word_frequency.values()
        if count > 1
    )

    repeated_word_ratio = (
        repeated_words / word_count
        if word_count
        else 0.0
    )

    sensational_words = sorted(
        set(alphabetic_words) & SENSATIONAL_WORDS
    )

    sensational_word_count = sum(
        word_frequency[word]
        for word in sensational_words
    )

    # Sensationalism Scoring
    exclamation_score = min(exclamation_count * 5, 20)
    question_score = min(question_count * 2, 10)
    uppercase_score = min(uppercase_word_count * 4, 20)
    sensational_word_score = min(sensational_word_count * 5, 30)
    repetition_score = min(repeated_word_ratio * 100, 20)

    sensationalism_score = min(
        100.0,
        exclamation_score
        + question_score
        + uppercase_score
        + sensational_word_score
        + repetition_score,
    )

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "average_sentence_length": round(average_sentence_length, 2),
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "uppercase_word_count": uppercase_word_count,
        "repeated_word_ratio": round(repeated_word_ratio, 3),
        "sensational_word_count": sensational_word_count,
        "sensational_words": sensational_words,
        "sensationalism_score": round(sensationalism_score, 2),
    }