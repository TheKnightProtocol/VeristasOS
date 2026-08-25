import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.text_analyzer import analyze_text


def test_analyze_text_returns_all_expected_fields():
    result = analyze_text("This is a simple test sentence.")

    expected_fields = {
        "word_count",
        "sentence_count",
        "average_sentence_length",
        "exclamation_count",
        "question_count",
        "uppercase_word_count",
        "repeated_word_ratio",
        "sensational_word_count",
        "sensational_words",
        "sensationalism_score",
    }

    assert set(result.keys()) == expected_fields


def test_word_count():
    result = analyze_text("This is a test.")
    assert result["word_count"] == 4


def test_sentence_count():
    result = analyze_text("This is sentence one. This is sentence two.")
    assert result["sentence_count"] == 2


def test_exclamation_count():
    result = analyze_text("This is amazing! This is incredible!")
    assert result["exclamation_count"] == 2


def test_question_count():
    result = analyze_text("Is this real? Are you sure?")
    assert result["question_count"] == 2


def test_sensationalism_score_is_numeric():
    result = analyze_text("BREAKING! SHOCKING! This is unbelievable!")
    assert isinstance(result["sensationalism_score"], (int, float))


def test_uppercase_word_count():
    result = analyze_text("THIS is a TEST article.")
    assert result["uppercase_word_count"] == 2


def test_sensational_words_is_list():
    result = analyze_text("BREAKING shocking unbelievable news!")
    assert isinstance(result["sensational_words"], list)


def test_repeated_word_ratio_is_valid():
    result = analyze_text("news news news is important")
    assert 0 <= result["repeated_word_ratio"] <= 1


def test_empty_text_returns_result():
    result = analyze_text("")
    assert isinstance(result, dict)


def test_sensational_word_count_matches_words():
    result = analyze_text("BREAKING SHOCKING unbelievable news!")
    assert result["sensational_word_count"] == len(result["sensational_words"])